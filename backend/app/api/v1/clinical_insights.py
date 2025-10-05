"""
Clinical Insights API Endpoints
AI-powered clinical decision support and insights
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional
from pydantic import BaseModel

from app.db.session import get_db
from app.models.user import User
from app.models.intake_report import IntakeReport
from app.core.deps import get_current_provider, get_current_user
from app.services.ai_clinical_service import ai_clinical_service

router = APIRouter()


# Pydantic models
class ClinicalAnalysisRequest(BaseModel):
    report_id: int
    include_ai_insights: bool = True
    include_treatment_recommendations: bool = True
    include_risk_assessment: bool = True


class ClinicalInsightsResponse(BaseModel):
    report_id: int
    clinical_analysis: Dict[str, Any]
    ai_insights: str
    treatment_recommendations: Dict[str, Any]
    confidence_scores: Dict[str, float]
    red_flags: list
    follow_up_priorities: list
    analysis_timestamp: str


@router.post("/analyze-report", response_model=ClinicalInsightsResponse)
async def analyze_clinical_report(
    request: ClinicalAnalysisRequest,
    current_user: User = Depends(get_current_provider),
    db: Session = Depends(get_db)
):
    """
    Perform comprehensive clinical analysis of an intake report using AI
    """
    try:
        # Get the report
        report = db.query(IntakeReport).filter(
            IntakeReport.id == request.report_id
        ).first()
        
        if not report:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Report not found"
            )
        
        # Verify provider has access to this report
        if (report.assigned_provider_id != current_user.id and 
            current_user.role != "admin"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this report"
            )
        
        # Get session data for analysis
        session_data = report.session
        if not session_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No session data available for analysis"
            )
        
        # Perform clinical analysis
        analysis_result = await ai_clinical_service.analyze_clinical_data(
            report_data=report.report_data or {},
            screener_scores=session_data.screener_scores or {},
            conversation_history=session_data.conversation_history or [],
            db=db
        )
        
        # Update report with analysis results
        if "clinical_analysis" not in report.report_data:
            report.report_data = report.report_data or {}
        
        report.report_data["ai_clinical_analysis"] = analysis_result
        db.commit()
        
        return ClinicalInsightsResponse(
            report_id=report.id,
            clinical_analysis=analysis_result.get("clinical_analysis", {}),
            ai_insights=analysis_result.get("ai_insights", ""),
            treatment_recommendations=analysis_result.get("treatment_recommendations", {}),
            confidence_scores=analysis_result.get("confidence_scores", {}),
            red_flags=analysis_result.get("red_flags", []),
            follow_up_priorities=analysis_result.get("follow_up_priorities", []),
            analysis_timestamp=analysis_result.get("analysis_timestamp", "")
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Clinical analysis failed: {str(e)}"
        )


@router.get("/report/{report_id}/insights")
async def get_report_insights(
    report_id: int,
    current_user: User = Depends(get_current_provider),
    db: Session = Depends(get_db)
):
    """
    Get existing clinical insights for a report
    """
    try:
        # Get the report
        report = db.query(IntakeReport).filter(
            IntakeReport.id == report_id
        ).first()
        
        if not report:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Report not found"
            )
        
        # Verify provider has access to this report
        if (report.assigned_provider_id != current_user.id and 
            current_user.role != "admin"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this report"
            )
        
        # Check if analysis already exists
        report_data = report.report_data or {}
        ai_analysis = report_data.get("ai_clinical_analysis")
        
        if not ai_analysis:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No clinical analysis available. Please run analysis first."
            )
        
        return {
            "success": True,
            "report_id": report.id,
            "analysis": ai_analysis,
            "analysis_timestamp": ai_analysis.get("analysis_timestamp")
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get insights: {str(e)}"
        )


@router.post("/pattern-analysis")
async def analyze_symptom_patterns(
    patient_text: str,
    screener_data: Optional[Dict[str, Any]] = None,
    current_user: User = Depends(get_current_provider)
):
    """
    Analyze symptom patterns from patient text input
    """
    try:
        # Create mock clinical info for analysis
        clinical_info = {
            "chief_complaint": patient_text,
            "conversation_text": patient_text,
            "screener_scores": screener_data or {}
        }
        
        # Perform pattern analysis
        pattern_analysis = ai_clinical_service._analyze_symptom_patterns(clinical_info)
        
        return {
            "success": True,
            "pattern_analysis": pattern_analysis,
            "detected_conditions": pattern_analysis.get("detected_conditions", []),
            "symptom_severity": pattern_analysis.get("symptom_severity", {}),
            "confidence_scores": ai_clinical_service._calculate_confidence_scores(pattern_analysis)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Pattern analysis failed: {str(e)}"
        )


@router.post("/risk-assessment")
async def assess_clinical_risk(
    clinical_data: Dict[str, Any],
    current_user: User = Depends(get_current_provider)
):
    """
    Perform clinical risk assessment
    """
    try:
        # Perform risk assessment
        risk_assessment = ai_clinical_service._assess_clinical_risk(
            clinical_data, 
            clinical_data.get("pattern_analysis", {})
        )
        
        return {
            "success": True,
            "risk_assessment": risk_assessment,
            "overall_risk": risk_assessment.get("overall_risk"),
            "risk_factors": risk_assessment.get("risk_factors", []),
            "red_flags": ai_clinical_service._identify_red_flags(clinical_data, risk_assessment)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Risk assessment failed: {str(e)}"
        )


@router.post("/treatment-recommendations")
async def get_treatment_recommendations(
    condition_data: Dict[str, Any],
    current_user: User = Depends(get_current_provider)
):
    """
    Get evidence-based treatment recommendations
    """
    try:
        pattern_analysis = condition_data.get("pattern_analysis", {})
        risk_assessment = condition_data.get("risk_assessment", {})
        
        # Generate treatment recommendations
        recommendations = ai_clinical_service._generate_treatment_recommendations(
            pattern_analysis, 
            risk_assessment
        )
        
        return {
            "success": True,
            "treatment_recommendations": recommendations,
            "immediate_actions": recommendations.get("immediate_actions", []),
            "treatment_modalities": recommendations.get("treatment_modalities", []),
            "monitoring_plan": recommendations.get("monitoring_plan", [])
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Treatment recommendations failed: {str(e)}"
        )


@router.post("/differential-diagnosis")
async def generate_differential_diagnosis(
    clinical_data: Dict[str, Any],
    current_user: User = Depends(get_current_provider)
):
    """
    Generate differential diagnosis based on clinical data
    """
    try:
        pattern_analysis = clinical_data.get("pattern_analysis", {})
        
        # Generate differential diagnosis
        differential = ai_clinical_service._generate_differential_diagnosis(
            clinical_data, 
            pattern_analysis
        )
        
        return {
            "success": True,
            "differential_diagnosis": differential,
            "primary_diagnoses": differential[:3],  # Top 3 most likely
            "rule_out_considerations": [
                item["rule_out"] for item in differential
            ]
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Differential diagnosis failed: {str(e)}"
        )


@router.get("/clinical-guidelines/{condition}")
async def get_clinical_guidelines(
    condition: str,
    current_user: User = Depends(get_current_provider)
):
    """
    Get clinical guidelines and best practices for specific conditions
    """
    try:
        # Get treatment recommendations for condition
        condition_key = condition.lower().replace(" ", "_")
        
        if condition_key in ai_clinical_service.treatment_recommendations:
            recommendations = ai_clinical_service.treatment_recommendations[condition_key]
            
            return {
                "success": True,
                "condition": condition,
                "treatment_recommendations": recommendations,
                "severity_levels": list(recommendations.keys()),
                "evidence_based": True
            }
        else:
            return {
                "success": False,
                "message": f"No clinical guidelines available for {condition}",
                "available_conditions": list(ai_clinical_service.treatment_recommendations.keys())
            }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get clinical guidelines: {str(e)}"
        )


@router.get("/symptom-patterns")
async def get_symptom_patterns(
    current_user: User = Depends(get_current_provider)
):
    """
    Get available symptom patterns and conditions for analysis
    """
    try:
        return {
            "success": True,
            "symptom_patterns": ai_clinical_service.symptom_patterns,
            "available_conditions": list(ai_clinical_service.symptom_patterns.keys()),
            "treatment_recommendations": list(ai_clinical_service.treatment_recommendations.keys())
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get symptom patterns: {str(e)}"
        )
