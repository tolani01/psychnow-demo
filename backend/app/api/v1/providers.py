"""
Provider Endpoints
Provider-specific functionality including dashboard, notifications, and assignments
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_, or_
from typing import List, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel

from app.db.session import get_db
from app.schemas.report import ReportResponse, ReportListItem
from app.models.intake_report import IntakeReport
from app.models.provider_review import ProviderReview
from app.models.notification import Notification
from app.core.deps import get_current_provider, get_current_user
from app.models.user import User
from app.services.assignment_service import assignment_service
from app.services.notification_service import notification_service

router = APIRouter()


# Pydantic models for new endpoints
class DashboardStats(BaseModel):
    total_assigned: int
    pending_review: int
    high_risk_pending: int
    completed_today: int
    unread_notifications: int


class ProviderAssignmentRequest(BaseModel):
    report_id: int
    provider_id: int
    reason: Optional[str] = None


class ClinicalNotesRequest(BaseModel):
    clinical_notes: str
    treatment_plan: Optional[str] = None
    follow_up_required: bool = False
    follow_up_date: Optional[datetime] = None
    risk_assessment: Optional[str] = None


class NotificationResponse(BaseModel):
    id: int
    type: str
    title: str
    message: str
    priority: str
    data: dict
    is_read: bool
    created_at: datetime


@router.get("/dashboard-stats", response_model=DashboardStats)
async def get_dashboard_stats(
    current_user: User = Depends(get_current_provider),
    db: Session = Depends(get_db)
):
    """
    Get provider dashboard statistics
    """
    # Get assigned reports count
    total_assigned = db.query(IntakeReport).filter(
        IntakeReport.assigned_provider_id == current_user.id
    ).count()
    
    # Get pending review count
    pending_review = db.query(IntakeReport).filter(
        IntakeReport.assigned_provider_id == current_user.id,
        IntakeReport.review_status.in_(["pending", "in_review"])
    ).count()
    
    # Get high-risk pending count
    high_risk_pending = db.query(IntakeReport).filter(
        IntakeReport.assigned_provider_id == current_user.id,
        IntakeReport.risk_level == "high",
        IntakeReport.review_status.in_(["pending", "in_review"])
    ).count()
    
    # Get completed today count
    today = datetime.utcnow().date()
    completed_today = db.query(ProviderReview).filter(
        ProviderReview.provider_id == current_user.id,
        ProviderReview.reviewed_at >= today
    ).count()
    
    # Get unread notifications count
    unread_notifications = notification_service.get_unread_count(current_user.id, db)
    
    return DashboardStats(
        total_assigned=total_assigned,
        pending_review=pending_review,
        high_risk_pending=high_risk_pending,
        completed_today=completed_today,
        unread_notifications=unread_notifications
    )


@router.get("/assigned-reports", response_model=List[ReportListItem])
async def get_assigned_reports(
    status_filter: Optional[str] = Query(None, description="Filter by review status"),
    risk_level_filter: Optional[str] = Query(None, description="Filter by risk level"),
    limit: int = Query(50, description="Maximum number of reports to return"),
    current_user: User = Depends(get_current_provider),
    db: Session = Depends(get_db)
):
    """
    Get all intake reports assigned to this provider with optional filters
    """
    # Use assignment service to get filtered reports
    reports = assignment_service.get_provider_assigned_reports(
        current_user.id, 
        status_filter, 
        risk_level_filter, 
        limit, 
        db
    )
    
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


@router.get("/reports/{report_id}", response_model=ReportResponse)
async def get_report_detail(
    report_id: int,
    current_user: User = Depends(get_current_provider),
    db: Session = Depends(get_db)
):
    """
    Get detailed report (must be assigned to this provider)
    """
    report = db.query(IntakeReport).filter(
        IntakeReport.id == report_id,
        IntakeReport.assigned_provider_id == current_user.id
    ).first()
    
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found or not assigned to you"
        )
    
    return report


@router.post("/reports/{report_id}/review")
async def create_review(
    report_id: int,
    request: ClinicalNotesRequest,
    current_user: User = Depends(get_current_provider),
    db: Session = Depends(get_db)
):
    """
    Add clinical review to an intake report
    """
    # Verify report is assigned to this provider
    report = db.query(IntakeReport).filter(
        IntakeReport.id == report_id,
        IntakeReport.assigned_provider_id == current_user.id
    ).first()
    
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found or not assigned to you"
        )
    
    # Check if review already exists
    existing_review = db.query(ProviderReview).filter(
        ProviderReview.report_id == report_id,
        ProviderReview.provider_id == current_user.id
    ).first()
    
    if existing_review:
        # Update existing review
        existing_review.clinical_notes = request.clinical_notes
        existing_review.recommendations = request.treatment_plan
        existing_review.follow_up_required = request.follow_up_required
        existing_review.follow_up_date = request.follow_up_date
        existing_review.risk_assessment = request.risk_assessment
        existing_review.status = "completed"
        existing_review.reviewed_at = datetime.utcnow()
        db.commit()
        db.refresh(existing_review)
        return existing_review
    
    # Create new review
    review = ProviderReview(
        report_id=report_id,
        provider_id=current_user.id,
        clinical_notes=request.clinical_notes,
        recommendations=request.treatment_plan,
        follow_up_required=request.follow_up_required,
        follow_up_date=request.follow_up_date,
        risk_assessment=request.risk_assessment,
        status="completed",
        reviewed_at=datetime.utcnow()
    )
    
    db.add(review)
    
    # Update report status
    report.review_status = "completed"
    report.reviewed_at = datetime.utcnow()
    
    db.commit()
    db.refresh(review)
    
    return review


@router.get("/notifications", response_model=List[NotificationResponse])
async def get_notifications(
    unread_only: bool = Query(False, description="Return only unread notifications"),
    limit: int = Query(50, description="Maximum number of notifications"),
    current_user: User = Depends(get_current_provider),
    db: Session = Depends(get_db)
):
    """
    Get notifications for the current provider
    """
    notifications = notification_service.get_user_notifications(
        current_user.id, limit, unread_only, db
    )
    
    return [
        NotificationResponse(
            id=n.id,
            type=n.type,
            title=n.title,
            message=n.message,
            priority=n.priority,
            data=n.data,
            is_read=n.is_read,
            created_at=n.created_at
        ) for n in notifications
    ]


@router.post("/notifications/{notification_id}/read")
async def mark_notification_read(
    notification_id: int,
    current_user: User = Depends(get_current_provider),
    db: Session = Depends(get_db)
):
    """
    Mark notification as read
    """
    success = notification_service.mark_notification_read(notification_id, current_user.id, db)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found or not accessible"
        )
    
    return {"message": "Notification marked as read"}


@router.post("/notifications/read-all")
async def mark_all_notifications_read(
    current_user: User = Depends(get_current_provider),
    db: Session = Depends(get_db)
):
    """
    Mark all notifications as read for current provider
    """
    updated_count = notification_service.mark_all_notifications_read(current_user.id, db)
    
    return {
        "message": f"Marked {updated_count} notifications as read",
        "updated_count": updated_count
    }


@router.get("/workload")
async def get_provider_workload(
    current_user: User = Depends(get_current_provider),
    db: Session = Depends(get_db)
):
    """
    Get current provider workload and capacity information
    """
    workload = assignment_service.calculate_provider_workload(current_user.id, db)
    capacity = assignment_service.get_provider_capacity(current_user.id, db)
    
    return {
        "workload": workload,
        "capacity": capacity,
        "utilization_percent": (workload["pending_reports"] / capacity["max_caseload"]) * 100
    }

