"""
Feedback API Endpoints
Collects and stores clinician feedback on demo assessments
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from datetime import datetime
import logging

from app.db.session import get_db
from app.schemas.feedback import FeedbackSubmissionCreate, FeedbackSubmissionResponse
from app.models.feedback import FeedbackSubmission
from app.models.intake_session import IntakeSession
from app.models.intake_report import IntakeReport
from app.services.email_service import email_service
from app.core.rate_limit import limiter

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/submit", response_model=FeedbackSubmissionResponse)
@limiter.limit("100/minute")  # Rate limit feedback submissions - increased for development
async def submit_feedback(
    request: Request,
    feedback: FeedbackSubmissionCreate,
    db: Session = Depends(get_db)
):
    """
    Submit clinician feedback on demo assessment
    
    - Validates feedback data
    - Stores in database
    - Sends email notification to admin
    - Returns confirmation
    """
    try:
        # Verify session exists
        session = db.query(IntakeSession).filter(
            IntakeSession.session_token == feedback.session_id
        ).first()
        
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found. The assessment may have expired."
            )
        
        # Check if feedback already submitted for this session
        existing_feedback = db.query(FeedbackSubmission).filter(
            FeedbackSubmission.session_id == feedback.session_id
        ).first()
        
        if existing_feedback:
            logger.warning(f"Feedback already exists for session {feedback.session_id}, updating...")
            # Update existing feedback instead of creating duplicate
            existing_feedback.conversation_rating = feedback.conversation_rating
            existing_feedback.patient_report_rating = feedback.patient_report_rating
            existing_feedback.clinician_report_rating = feedback.clinician_report_rating
            existing_feedback.would_use = feedback.would_use
            existing_feedback.strength = feedback.strength
            existing_feedback.concern = feedback.concern
            existing_feedback.missing_patient = feedback.missing_patient
            existing_feedback.missing_clinician = feedback.missing_clinician
            existing_feedback.additional_comments = feedback.additional_comments
            existing_feedback.tester_email = feedback.tester_email
            existing_feedback.tester_name = feedback.tester_name
            existing_feedback.submitted_at = datetime.utcnow()
            
            db_feedback = existing_feedback
        else:
            # Create new feedback record
            db_feedback = FeedbackSubmission(
                session_id=feedback.session_id,
                conversation_rating=feedback.conversation_rating,
                patient_report_rating=feedback.patient_report_rating,
                clinician_report_rating=feedback.clinician_report_rating,
                would_use=feedback.would_use,
                strength=feedback.strength,
                concern=feedback.concern,
                missing_patient=feedback.missing_patient,
                missing_clinician=feedback.missing_clinician,
                additional_comments=feedback.additional_comments,
                tester_email=feedback.tester_email,
                tester_name=feedback.tester_name,
            )
            
            db.add(db_feedback)
        
        # Mark report as having feedback
        report = db.query(IntakeReport).filter(
            IntakeReport.session_id == feedback.session_id
        ).first()
        
        if report:
            report.feedback_submitted = True
        
        db.commit()
        db.refresh(db_feedback)
        
        # Send email notification to admin
        try:
            email_service.send_feedback_submission_email(db_feedback.to_dict())
            logger.info(f"✅ Feedback email sent for session {feedback.session_id}")
        except Exception as email_error:
            logger.error(f"⚠️ Failed to send feedback email: {str(email_error)}")
            # Don't fail the request if email fails
        
        logger.info(f"✅ Feedback submitted successfully for session {feedback.session_id}")
        
        return FeedbackSubmissionResponse(
            id=db_feedback.id,
            session_id=db_feedback.session_id,
            submitted_at=db_feedback.submitted_at,
            message="Thank you for your valuable feedback! Your input will help shape PsychNow."
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error submitting feedback: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to submit feedback: {str(e)}"
        )


@router.get("/stats")
@limiter.limit("100/minute")  # Increased for development
async def get_feedback_stats(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Get aggregated feedback statistics (for admin dashboard)
    """
    try:
        feedbacks = db.query(FeedbackSubmission).all()
        
        if not feedbacks:
            return {
                "total_submissions": 0,
                "average_ratings": {},
                "would_use_breakdown": {}
            }
        
        # Calculate averages
        total = len(feedbacks)
        avg_conversation = sum(f.conversation_rating for f in feedbacks) / total
        avg_patient = sum(f.patient_report_rating for f in feedbacks) / total
        avg_clinician = sum(f.clinician_report_rating for f in feedbacks) / total
        
        # Would use breakdown
        would_use_counts = {}
        for f in feedbacks:
            would_use_counts[f.would_use] = would_use_counts.get(f.would_use, 0) + 1
        
        return {
            "total_submissions": total,
            "average_ratings": {
                "conversation": round(avg_conversation, 2),
                "patient_report": round(avg_patient, 2),
                "clinician_report": round(avg_clinician, 2)
            },
            "would_use_breakdown": would_use_counts
        }
        
    except Exception as e:
        logger.error(f"Error getting feedback stats: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve feedback statistics"
        )

