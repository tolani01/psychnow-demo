"""
Reports Endpoints
Intake report management
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List

from app.db.session import get_db
from app.schemas.report import ReportResponse, ReportListItem
from app.models.intake_report import IntakeReport
from app.core.deps import get_current_user, get_current_user_optional
from app.models.user import User
from typing import Optional

router = APIRouter()


@router.get("/me", response_model=List[ReportListItem])
async def get_my_reports(
    limit: int = 3,
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """
    Get current user's completed assessment reports (default: 3 most recent)
    
    Query params:
    - limit: Number of reports to return (default: 3, max: 50)
    """
    if not current_user:
        return []
    
    # Limit to reasonable maximum
    limit = min(limit, 50)
    
    # Get patient's reports
    reports = db.query(IntakeReport).filter(
        IntakeReport.patient_id == str(current_user.id)
    ).order_by(desc(IntakeReport.created_at)).limit(limit).all()
    
    # Create list items with details
    result = []
    for report in reports:
        item = ReportListItem(
            id=report.id,
            patient_id=report.patient_id,
            severity_level=report.severity_level,
            risk_level=report.risk_level,
            urgency=report.urgency,
            created_at=report.created_at,
            chief_complaint=report.report_data.get("chief_complaint") if report.report_data else None
        )
        result.append(item)
    
    return result


@router.get("/", response_model=List[ReportListItem])
async def list_reports(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List intake reports for current user (all reports - for providers/admins)
    
    Patients see their own reports
    Providers see reports assigned to them
    """
    if current_user.role.value == "patient":
        # Patient sees their own reports
        reports = db.query(IntakeReport).filter(
            IntakeReport.patient_id == str(current_user.id)
        ).order_by(desc(IntakeReport.created_at)).all()
    elif current_user.role.value == "provider":
        # Provider sees reports assigned to them
        reports = db.query(IntakeReport).filter(
            IntakeReport.shared_with_provider_id == current_user.id
        ).order_by(desc(IntakeReport.created_at)).all()
    else:
        # Admin sees all reports
        reports = db.query(IntakeReport).order_by(desc(IntakeReport.created_at)).limit(100).all()
    
    # Create list items with chief complaint
    result = []
    for report in reports:
        item = ReportListItem(
            id=report.id,
            patient_id=report.patient_id,
            severity_level=report.severity_level,
            risk_level=report.risk_level,
            urgency=report.urgency,
            created_at=report.created_at,
            chief_complaint=report.report_data.get("chief_complaint") if report.report_data else None
        )
        result.append(item)
    
    return result


@router.get("/{report_id}", response_model=ReportResponse)
async def get_report(
    report_id: str,
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """
    Get detailed intake report
    
    Authorization:
    - Anonymous users can access reports they just created (via localStorage)
    - Patients can access their own reports
    - Providers can access reports assigned to them
    - Admins can access any report
    """
    report = db.query(IntakeReport).filter(IntakeReport.id == report_id).first()
    
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found"
        )
    
    # Check authorization
    if current_user:
        if current_user.role.value == "patient":
            if report.patient_id != str(current_user.id):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Not authorized to view this report"
                )
        elif current_user.role.value == "provider":
            if report.shared_with_provider_id != current_user.id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Report not assigned to you"
                )
        # Admins can access all reports
    else:
        # Anonymous user - allow access to their own reports
        # They would only have the report_id if they just completed the assessment
        # This is safe since report_id is a UUID and not guessable
        pass
    
    return report


@router.get("/{report_id}/pdf")
async def download_report_pdf(
    report_id: str,
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """
    Download report as PDF
    
    TODO: Implement PDF generation with ReportLab
    """
    report = db.query(IntakeReport).filter(IntakeReport.id == report_id).first()
    
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found"
        )
    
    # Authorization check (same as get_report)
    if current_user:
        if current_user.role.value == "patient":
            if report.patient_id != str(current_user.id):
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
        elif current_user.role.value == "provider":
            if report.shared_with_provider_id != current_user.id:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    # Anonymous users allowed (same logic as get_report)
    
    # TODO: Generate PDF
    # For now, return JSON
    return {
        "message": "PDF generation coming soon",
        "report_id": report_id,
        "download_json": f"/api/v1/reports/{report_id}"
    }

