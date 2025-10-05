"""
Intake Endpoints
Patient intake session and conversation management
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import AsyncIterator
import json
from datetime import datetime, timedelta
import secrets
import logging

from app.schemas.intake import (
    IntakeSessionCreate,
    IntakeSessionResponse,
    ChatRequest,
    ChatResponse,
    FinishIntakeRequest
)
from app.services.conversation_service import conversation_service
from app.core.rate_limit import (
    limiter, 
    get_chat_rate_limit, 
    get_start_rate_limit, 
    get_pause_resume_rate_limit
)
from typing import Optional

# Import these only when needed to avoid loading database dependencies
def _get_db_dependencies():
    """Lazy load database dependencies"""
    try:
        from app.db.session import get_db
        from app.models.intake_session import IntakeSession
        from app.models.intake_report import IntakeReport
        from app.services.report_service import report_service
        from app.services.escalation_service import escalation_service
        from app.services.pdf_service import pdf_service
        from app.services.session_cleanup_service import session_cleanup_service
        from app.services.email_service import email_service
        from app.core.deps import get_current_user_optional
        from app.models.user import User
        return {
            'get_db': get_db,
            'IntakeSession': IntakeSession,
            'IntakeReport': IntakeReport,
            'report_service': report_service,
            'escalation_service': escalation_service,
            'pdf_service': pdf_service,
            'session_cleanup_service': session_cleanup_service,
            'email_service': email_service,
            'get_current_user_optional': get_current_user_optional,
            'User': User
        }
    except Exception as e:
        logger.error(f"Failed to load database dependencies: {e}")
        return None

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/session/{session_token}/recover")
async def recover_session(session_token: str, db: Session = Depends(get_db)):
    """Recover a session that encountered an error"""
    try:
        # Check if session exists
        session = db.query(IntakeSession).filter(
            IntakeSession.session_token == session_token
        ).first()
        
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Try to load session from database first
        loaded_session = conversation_service.load_session_from_db(session_token, db)
        
        # Get conversation history from conversation service
        conversation_history = conversation_service.get_conversation_history(session_token)
        
        # If no conversation history in memory, try to get it from database
        if not conversation_history and session.conversation_history:
            conversation_history = session.conversation_history
        
        if not conversation_history:
            # Return empty conversation history but allow recovery
            return {
                "session_token": session_token,
                "conversation_history": [],
                "recovered": True,
                "message": "Session recovered successfully. You can continue where you left off."
            }
        
        return {
            "session_token": session_token,
            "conversation_history": conversation_history,
            "recovered": True,
            "message": "Session recovered successfully. You can continue where you left off."
        }
        
    except Exception as e:
        logger.error(f"Error recovering session {session_token}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to recover session")


@router.post("/start", response_model=IntakeSessionResponse)
@limiter.limit(get_start_rate_limit)
async def start_intake_session(
    request: Request,
    session_data: IntakeSessionCreate
):
    """
    Start a new intake session
    
    Returns session token for anonymous access
    """
    try:
        # Create session in conversation service (no database required)
        conv_session = conversation_service.create_session(
            patient_id=session_data.patient_id,
            user_name=session_data.user_name
        )
        
        logger.info(f"Session created: {conv_session['session_token']}")
        
        # Always return in-memory session (database optional for now)
        return IntakeSessionResponse(
            id=1,
            session_token=conv_session["session_token"],
            patient_id=session_data.patient_id,
            current_phase=conv_session["current_phase"],
            status="active"
        )
    except Exception as e:
        logger.error(f"Session creation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create session: {str(e)}"
        )


@router.post("/chat")
@limiter.limit(get_chat_rate_limit)
async def chat(
    request: Request,
    chat_request: ChatRequest
):
    """
    Send a message and receive streaming AI response
    
    Uses Server-Sent Events (SSE) for streaming
    """
    # Get in-memory session (no database required)
    session = conversation_service.get_session(chat_request.session_token)
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found. Please start a new session."
        )
    
    # Handle initial greeting (empty prompt)
    if not chat_request.prompt or chat_request.prompt.strip() == "":
        greeting = await conversation_service.get_initial_greeting(chat_request.session_token)
        
        # Format as SSE
        async def stream_greeting():
            # Send greeting
            message = ChatResponse(
                role="model",
                content=greeting,
                timestamp=datetime.utcnow(),
                done=False
            )
            yield f"data: {message.model_dump_json()}\n\n"
            
            # Add to history
            conversation_service.add_message(chat_request.session_token, "model", greeting)
        
        return StreamingResponse(
            stream_greeting(),
            media_type="text/event-stream",
            headers={
                "X-Session-ID": chat_request.session_token,
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
            }
        )
    
    # Handle :finish command
    if chat_request.prompt.strip() == ":finish":
        # Capture session_token for use in nested functions
        session_token_str = chat_request.session_token
        
        try:
            # Generate BOTH reports (patient and clinician versions)
            dual_reports = await report_service.generate_dual_reports(session)
            patient_report = dual_reports["patient_report"]
            clinician_report = dual_reports["clinician_report"]
            
            # Check for high-risk and trigger escalation (use patient report for consistency)
            risk_level = patient_report.get("risk_level", "low")
            if risk_level == "high":
                # Trigger high-risk escalation
                await escalation_service.handle_high_risk_detection(
                    session_data=session,
                    risk_details={
                        "risk_level": risk_level,
                        "screener_name": "Clinical Assessment",
                        "score": patient_report.get("screeners", [{}])[0].get("score", "N/A"),
                        "details": patient_report.get("safety_assessment", "High risk detected in intake")
                    },
                    db=db
                )
            
            # Generate BOTH PDFs - capture patient name
            patient_name = current_user.name if current_user else "Patient"
            patient_pdf_base64 = pdf_service.generate_patient_report_base64(patient_report, patient_name)
            clinician_pdf_base64 = pdf_service.generate_clinician_report_base64(clinician_report, patient_name)
            
            # Send completion message then report
            async def stream_completion():
                # Confirmation message
                conf_msg = ChatResponse(
                    role="model",
                    content="✅ Assessment complete! Your report has been generated and saved to your dashboard.",
                    timestamp=datetime.utcnow(),
                    done=False
                )
                yield f"data: {conf_msg.model_dump_json()}\n\n"
                
                # High-risk alert (if applicable)
                if risk_level == "high":
                    alert_msg = ChatResponse(
                        role="model",
                        content="\n🚨 HIGH RISK ALERT: Admin has been notified for immediate review.",
                        timestamp=datetime.utcnow(),
                        done=False
                    )
                    yield f"data: {alert_msg.model_dump_json()}\n\n"
                
                # Report summary (formatted nicely)
                summary_content = f"""Assessment Summary:

• Risk Level: {risk_level.upper()}
• Urgency: {patient_report.get('urgency', 'routine').upper()}
• Chief Complaint: {patient_report.get('chief_complaint', 'N/A')}
• Report Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}

Two report versions have been generated:
📋 Patient Report - Compassionate summary for you
🩺 Clinician Report - Comprehensive clinical assessment for your provider

Both reports are available for download below.
                """.strip()
                
                report_msg = ChatResponse(
                    role="model",
                    content=summary_content,
                    timestamp=datetime.utcnow(),
                    done=True,
                    pdf_report=patient_pdf_base64,  # Legacy support
                    patient_pdf=patient_pdf_base64,  # Patient version
                    clinician_pdf=clinician_pdf_base64  # Clinician version
                )
                yield f"data: {report_msg.model_dump_json()}\n\n"
                
                # Save report to database
                db_session = db.query(IntakeSession).filter(
                    IntakeSession.session_token == chat_request.session_token
                ).first()
                
                report_id = None
                if db_session:
                    # Create report record with BOTH reports
                    db_report = IntakeReport(
                        session_id=db_session.id,
                        patient_id=db_session.patient_id,
                        report_data=patient_report,  # Patient version as main
                        clinician_report_data=clinician_report,  # Clinician version
                        severity_level=patient_report.get("risk_level"),
                        risk_level=patient_report.get("risk_level"),
                        urgency=patient_report.get("urgency"),
                        patient_pdf_path=f"patient_{db_session.session_token[:8]}.pdf",
                        clinician_pdf_path=f"clinician_{db_session.session_token[:8]}.pdf"
                    )
                    db.add(db_report)
                    
                    # Update session status
                    db_session.status = "completed"
                    db_session.completed_at = datetime.utcnow()
                    
                    db.commit()
                    db.refresh(db_report)
                    report_id = db_report.id
                    
                    # Send email notification to admin with both PDFs
                    try:
                        # Calculate duration
                        duration = None
                        if db_session.created_at and db_session.completed_at:
                            duration_delta = db_session.completed_at - db_session.created_at
                            duration = int(duration_delta.total_seconds() / 60)  # minutes
                        
                        email_service.send_assessment_completion_email(
                            session_id=db_session.session_token,
                            patient_pdf_base64=patient_pdf_base64,
                            clinician_pdf_base64=clinician_pdf_base64,
                            duration_minutes=duration
                        )
                        logger.info(f"✅ Assessment completion email sent for session {db_session.session_token}")
                    except Exception as email_error:
                        logger.error(f"⚠️ Failed to send completion email: {str(email_error)}")
                        # Don't fail the request if email fails
                    
                    # Send report ID in a separate SSE message for frontend to capture
                    report_id_msg = ChatResponse(
                        role="model",
                        content=f"REPORT_ID:{report_id}",  # Special format for frontend parsing
                        timestamp=datetime.utcnow(),
                        done=False
                    )
                    yield f"data: {report_id_msg.model_dump_json()}\n\n"
        
            return StreamingResponse(
                stream_completion(),
                media_type="text/event-stream",
                headers={
                    "X-Session-ID": session_token_str,
                    "Cache-Control": "no-cache",
                }
            )
        
        except Exception as e:
            print(f"Error generating report: {e}")
            import traceback
            traceback.print_exc()
            
            # Return error message to patient
            async def stream_error():
                error_msg = ChatResponse(
                    role="model",
                    content=f"I apologize, but I encountered an error while generating your report. Error: {str(e)[:100]}. Please try again or contact support if the issue persists.",
                    timestamp=datetime.utcnow(),
                    done=True
                )
                yield f"data: {error_msg.model_dump_json()}\n\n"
            
            return StreamingResponse(
                stream_error(),
                media_type="text/event-stream",
                headers={
                    "X-Session-ID": session_token_str,
                    "Cache-Control": "no-cache",
                }
            )
    
    # Normal conversation
    async def stream_response():
        full_response = ""
        
        try:
            async for chunk in conversation_service.process_user_message(
                chat_request.session_token,
                chat_request.prompt
            ):
                full_response += chunk
                
                # Send chunk
                message = ChatResponse(
                    role="model",
                    content=chunk,
                    timestamp=datetime.utcnow(),
                    done=False
                )
                yield f"data: {message.model_dump_json()}\n\n"
        
        except Exception as e:
            logger.error(f"Error processing message for session {chat_request.session_token}: {str(e)}")
            
            # Send error message to user
            error_message = ChatResponse(
                role="model",
                content="I apologize, but I encountered an error processing your message. Please try rephrasing your response or continue with the assessment. Your progress is saved.",
                timestamp=datetime.utcnow(),
                done=True
            )
            yield f"data: {error_message.model_dump_json()}\n\n"
            return
        
        # Check for options and send final message with options if available
        session = conversation_service.get_session(chat_request.session_token)
        if session and session["conversation_history"]:
            last_message = session["conversation_history"][-1]
            if last_message.get("options"):
                # Send final message with options
                final_message = ChatResponse(
                    role="model",
                    content="",  # No additional content, just options
                    timestamp=datetime.utcnow(),
                    done=True,
                    options=last_message["options"]
                )
                yield f"data: {final_message.model_dump_json()}\n\n"
        
        # Update database with comprehensive session data
        try:
            conversation_service.save_session_to_db(chat_request.session_token, db)
        except Exception as e:
            logger.error(f"Error saving session to database: {str(e)}")
            # Continue without failing the response
    
    return StreamingResponse(
        stream_response(),
        media_type="text/event-stream",
        headers={
            "X-Session-ID": chat_request.session_token,
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )


@router.get("/sessions/me")
async def get_my_sessions(
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    Get all sessions for the current user (including paused ones)
    
    Returns list of user's intake sessions
    """
    # Get patient_id from current_user or check localStorage-based temp_user_id
    # For now, we'll return sessions that match the user
    if not current_user:
        # For anonymous users, we can't fetch sessions without authentication
        return {"sessions": [], "message": "Please sign in to see your sessions"}
    
    # Get all sessions for this user
    sessions = db.query(IntakeSession).filter(
        IntakeSession.patient_id == str(current_user.id),
        IntakeSession.status.in_(["active", "paused"])
    ).order_by(IntakeSession.updated_at.desc()).all()
    
    result = []
    for session in sessions:
        result.append({
            "id": session.id,
            "session_token": session.session_token,
            "status": session.status,
            "current_phase": session.current_phase,
            "resume_token": session.resume_token if session.status == "paused" else None,
            "paused_at": session.paused_at.isoformat() if session.paused_at else None,
            "expires_at": session.expires_at.isoformat() if session.expires_at else None,
            "created_at": session.created_at.isoformat(),
            "updated_at": session.updated_at.isoformat() if session.updated_at else None,
            "completed_screeners": session.completed_screeners or []
        })
    
    return {"sessions": result}


@router.get("/session/{session_token}")
async def get_session(
    session_token: str,
    db: Session = Depends(get_db)
):
    """
    Get session state
    
    Returns current session data
    """
    # Check in-memory first
    conv_session = conversation_service.get_session(session_token)
    if conv_session:
        return conv_session
    
    # Check database
    db_session = db.query(IntakeSession).filter(
        IntakeSession.session_token == session_token
    ).first()
    
    if not db_session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    return {
        "session_token": db_session.session_token,
        "status": db_session.status,
        "current_phase": db_session.current_phase,
        "conversation_history": db_session.conversation_history or [],
        "created_at": db_session.created_at.isoformat()
    }


@router.post("/pause")
@limiter.limit(get_pause_resume_rate_limit)
async def pause_session(
    request: Request,
    pause_request: ChatRequest,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    Pause an active intake session
    Can only pause between conversations and after completed assessments
    """
    # Verify session exists
    db_session = db.query(IntakeSession).filter(
        IntakeSession.session_token == pause_request.session_token
    ).first()
    
    if not db_session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    if db_session.status != "active":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Can only pause active sessions"
        )
    
    # Check if we can pause (not in middle of an assessment)
    session_data = conversation_service.get_session(pause_request.session_token)
    if not session_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session data not found"
        )
    
    # Determine if we can pause based on current state
    can_pause = _can_pause_session(session_data)
    
    if not can_pause:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot pause session in the middle of an assessment. Please complete the current assessment first."
        )
    
    # Generate secure resume token
    resume_token = secrets.token_urlsafe(32)
    
    # Calculate expiration (24 hours from now)
    expires_at = datetime.utcnow() + timedelta(hours=24)
    
    # Update session with pause information
    db_session.status = "paused"
    db_session.paused_at = datetime.utcnow()
    db_session.expires_at = expires_at
    db_session.resume_token = resume_token
    
    # Track completed screeners and current progress
    db_session.completed_screeners = session_data.get("completed_screeners", [])
    db_session.current_screener = session_data.get("current_screener")
    db_session.screener_progress = session_data.get("screener_progress", {})
    
    db.commit()
    
    return {
        "message": "Session paused successfully",
        "resume_token": resume_token,
        "expires_at": expires_at.isoformat(),
        "completed_screeners": db_session.completed_screeners,
        "can_resume": True
    }


@router.post("/resume")
@limiter.limit(get_pause_resume_rate_limit)
async def resume_session(
    http_request: Request,
    request: dict,  # {"resume_token": "..."}
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    Resume a paused intake session
    Checks expiration and restores session state
    """
    resume_token = request.get("resume_token")
    if not resume_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Resume token required"
        )
    
    # Find paused session by resume token
    db_session = db.query(IntakeSession).filter(
        IntakeSession.resume_token == resume_token,
        IntakeSession.status == "paused"
    ).first()
    
    if not db_session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Paused session not found or already resumed"
        )
    
    # Check if session has expired
    if db_session.expires_at and db_session.expires_at < datetime.utcnow():
        # Mark as abandoned and clean up
        db_session.status = "abandoned"
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail="Session has expired. Please start a new assessment."
        )
    
    # Restore session state
    db_session.status = "active"
    db_session.paused_at = None
    db_session.expires_at = None
    db_session.resume_token = None
    
    # Restore conversation service state
    session_data = {
        "conversation_history": db_session.conversation_history or [],
        "extracted_data": db_session.extracted_data or {},
        "screener_scores": db_session.screener_scores or {},
        "completed_screeners": db_session.completed_screeners or [],
        "current_screener": db_session.current_screener,
        "screener_progress": db_session.screener_progress or {},
        "current_phase": db_session.current_phase
    }
    
    conversation_service.restore_session(db_session.session_token, session_data)
    
    db.commit()
    
    # Generate smart, compassionate welcome back message with next question
    welcome_message = await _generate_resume_message(session_data)
    
    return {
        "message": "Session resumed successfully",
        "session_token": db_session.session_token,
        "welcome_message": welcome_message,
        "conversation_history": db_session.conversation_history or [],
        "completed_screeners": db_session.completed_screeners,
        "current_phase": db_session.current_phase
    }


def _can_pause_session(session_data: dict) -> bool:
    """
    Determine if session can be paused based on current state
    Can pause: between conversations, after completed assessments
    Cannot pause: during active assessments
    """
    current_phase = session_data.get("current_phase", "")
    conversation_history = session_data.get("conversation_history", [])
    
    # Can't pause during safety assessment (C-SSRS)
    if current_phase == "screening" and "C-SSRS" in str(conversation_history):
        return False
    
    # Can pause if not in the middle of a screener
    if current_phase == "screening":
        # Check if we're in the middle of a screener question
        if conversation_history:
            last_message = conversation_history[-1]
            if last_message.get("role") == "model":
                content = last_message.get("content", "")
                # If the last message was asking a screener question, we're in the middle
                if any(indicator in content for indicator in [
                    "PHQ-9 Question", "GAD-7 Question", "C-SSRS Question"
                ]):
                    return False
    
    # Can pause between conversations or after completed assessments
    return True


async def _generate_resume_message(session_data: dict) -> str:
    """
    Generate a smart, compassionate welcome back message with next question
    Uses LLM to create context-aware continuation
    """
    from app.services.llm_service import llm_service
    from app.prompts.system_prompts import INTAKE_SYSTEM_PROMPT
    
    conversation_history = session_data.get("conversation_history", [])
    completed_screeners = session_data.get("completed_screeners", [])
    current_phase = session_data.get("current_phase", "")
    
    # Build context for LLM
    num_completed = len(completed_screeners)
    time_context = "You both took a pause in your conversation"
    
    resume_prompt = f"""
CONTEXT: The patient paused their mental health assessment and is now resuming. They can see all their previous messages above (faded/grayed out), so DO NOT summarize what they already said - they can read it themselves.

YOUR TASK: Welcome them back in a warm, compassionate way and IMMEDIATELY ask the next question.

CRITICAL INSTRUCTIONS:
1. Start with a brief (1-2 sentences) warm welcome that:
   - Validates their self-care (taking breaks is healthy!)  
   - Acknowledges their courage in continuing this process
   
2. Provide a quick progress update if relevant:
   - Completed: {num_completed} screening(s) so far
   - Current phase: {current_phase}
   
3. THEN, in the SAME message, smoothly transition to the NEXT question they need to answer
   - Don't ask them "are you ready?" - just ask the next question
   - Make it feel like you're picking up mid-conversation, not restarting
   - Be warm but efficient

4. Use their conversational tone - if they were casual, stay casual. If formal, stay professional.

RECENT CONVERSATION (for context only - DON'T repeat this, they can already see it):
{_format_recent_messages(conversation_history, last_n=4)}

EXAMPLE TONE (adapt to their style):
"Welcome back! I'm glad you took that break - self-care is so important. You've made great progress completing the PHQ-9 and GAD-7 screenings. 

Let's continue with understanding your anxiety patterns. Over the last 2 weeks, how often have you felt unable to stop or control worrying?"

NOW GENERATE: Your compassionate welcome + immediate next question in ONE cohesive message.
"""
    
    # Use LLM to generate smart resume message
    messages = [
        {"role": "system", "content": INTAKE_SYSTEM_PROMPT},
        {"role": "user", "content": resume_prompt}
    ]
    
    try:
        response = await llm_service.get_chat_completion(messages, temperature=0.8)
        return response
    except Exception as e:
        # Fallback to simple message if LLM fails
        return f"Welcome back! Thank you for taking care of yourself with that break. Let's continue your assessment."


def _format_recent_messages(conversation_history: list, last_n: int = 4) -> str:
    """Format recent messages for context"""
    if not conversation_history:
        return "No previous conversation"
    
    recent = conversation_history[-last_n:] if len(conversation_history) > last_n else conversation_history
    formatted = []
    
    for msg in recent:
        role = "Patient" if msg.get("role") == "user" else "Ava"
        content = msg.get("content", "")[:100]  # Limit length
        formatted.append(f"{role}: {content}")
    
    return "\n".join(formatted)


@router.post("/cleanup")
async def cleanup_sessions(
    db: Session = Depends(get_db)
):
    """
    Cleanup expired and abandoned sessions
    This endpoint can be called by a scheduled task or manually
    """
    try:
        # Clean up expired paused sessions
        expired_cleaned = session_cleanup_service.cleanup_expired_sessions(db)
        
        # Clean up old abandoned sessions from memory
        abandoned_cleaned = session_cleanup_service.cleanup_abandoned_sessions(db)
        
        # Get current stats
        stats = session_cleanup_service.get_session_stats(db)
        
        return {
            "message": "Session cleanup completed",
            "expired_sessions_cleaned": expired_cleaned,
            "abandoned_sessions_cleaned": abandoned_cleaned,
            "current_stats": stats
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Cleanup failed: {str(e)}"
        )


@router.get("/stats")
async def get_session_stats(
    db: Session = Depends(get_db)
):
    """
    Get session statistics
    """
    try:
        stats = session_cleanup_service.get_session_stats(db)
        return stats
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get stats: {str(e)}"
        )


@router.post("/transfer-session")
async def transfer_session(
    request: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_optional)
):
    """
    Transfer an anonymous session to a newly created authenticated account
    Used when a patient creates an account mid-assessment
    """
    session_token = request.get("session_token")
    new_user_id = request.get("new_user_id")
    user_name = request.get("user_name")
    
    if not session_token or not new_user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="session_token and new_user_id required"
        )
    
    # Find the session
    db_session = db.query(IntakeSession).filter(
        IntakeSession.session_token == session_token
    ).first()
    
    if not db_session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    # Transfer session to new user
    old_patient_id = db_session.patient_id
    db_session.patient_id = str(new_user_id)
    
    # Update in-memory session if exists
    conv_session = conversation_service.get_session(session_token)
    if conv_session:
        conv_session["patient_id"] = str(new_user_id)
        conv_session["user_name"] = user_name
        # Update extracted data with new name if not already set
        if not conv_session.get("extracted_data", {}).get("name"):
            if "extracted_data" not in conv_session:
                conv_session["extracted_data"] = {}
            conv_session["extracted_data"]["name"] = user_name
    
    db.commit()
    
    return {
        "message": "Session transferred successfully",
        "old_patient_id": old_patient_id,
        "new_patient_id": str(new_user_id),
        "session_token": session_token
    }

