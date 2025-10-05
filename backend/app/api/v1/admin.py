"""
Admin Endpoints
Administrative functions for managing the platform, providers, and assignments
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_, or_
from typing import List, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel

from app.db.session import get_db
from app.schemas.notification import NotificationResponse, NotificationUpdate
from app.schemas.admin import AssignReportRequest, ApproveProviderRequest
from app.models.notification import Notification
from app.models.intake_session import IntakeSession
from app.models.intake_report import IntakeReport
from app.models.provider_profile import ProviderProfile
from app.models.audit_log import AuditLog
from app.models.user import User, UserRole
from app.models.provider_review import ProviderReview
from app.core.deps import get_current_admin
from app.services.assignment_service import assignment_service
from app.services.notification_service import notification_service

router = APIRouter()


# Pydantic models for new admin endpoints
class SystemStats(BaseModel):
    total_reports: int
    assigned_reports: int
    unassigned_reports: int
    high_risk_unassigned: int
    total_providers: int
    active_providers: int
    pending_providers: int
    assignment_rate: float


class ProviderWorkloadInfo(BaseModel):
    provider_id: int
    provider_name: str
    pending_reports: int
    high_risk_reports: int
    max_caseload: int
    utilization_percent: float
    recent_reviews: int


class AssignmentStats(BaseModel):
    reports_by_status: dict
    provider_workloads: List[ProviderWorkloadInfo]
    assignment_rate: float


@router.get("/system-stats", response_model=SystemStats)
async def get_system_stats(
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Get comprehensive system statistics for admin dashboard
    """
    # Get assignment statistics
    assignment_stats = assignment_service.get_assignment_stats(db)
    
    # Get provider statistics
    total_providers = db.query(User).filter(User.role == "provider").count()
    active_providers = db.query(User).filter(
        User.role == "provider",
        User.is_active == True,
        User.provider_profile.has(is_approved=True)
    ).count()
    pending_providers = db.query(ProviderProfile).filter(
        ProviderProfile.approval_status == "pending"
    ).count()
    
    return SystemStats(
        total_reports=assignment_stats["total_reports"],
        assigned_reports=assignment_stats["assigned_reports"],
        unassigned_reports=assignment_stats["unassigned_reports"],
        high_risk_unassigned=assignment_stats["high_risk_unassigned"],
        total_providers=total_providers,
        active_providers=active_providers,
        pending_providers=pending_providers,
        assignment_rate=assignment_stats["assignment_rate"]
    )


@router.get("/assignment-stats", response_model=AssignmentStats)
async def get_assignment_stats(
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Get detailed assignment statistics and provider workloads
    """
    stats = assignment_service.get_assignment_stats(db)
    
    return AssignmentStats(
        reports_by_status=stats["reports_by_status"],
        provider_workloads=[
            ProviderWorkloadInfo(
                provider_id=pw["provider_id"],
                provider_name=pw["provider_name"],
                pending_reports=pw["pending_reports"],
                high_risk_reports=pw["high_risk_reports"],
                max_caseload=pw["max_caseload"],
                utilization_percent=pw["utilization_percent"]
            ) for pw in stats["provider_workloads"]
        ],
        assignment_rate=stats["assignment_rate"]
    )


@router.get("/unassigned-reports")
async def get_unassigned_reports(
    limit: int = Query(50, description="Maximum number of reports"),
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Get reports that haven't been assigned to any provider
    """
    reports = assignment_service.get_unassigned_reports(db, limit)
    
    return [
        {
            "id": report.id,
            "patient_id": report.patient_id,
            "risk_level": report.risk_level,
            "urgency": report.urgency,
            "created_at": report.created_at,
            "chief_complaint": report.report_data.get("chief_complaint") if report.report_data else None
        } for report in reports
    ]


@router.post("/auto-assign-report/{report_id}")
async def auto_assign_report(
    report_id: int,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Auto-assign report to least-busy provider
    """
    try:
        assigned_provider_id = assignment_service.auto_assign_report(report_id, db)
        
        # Get provider info
        provider = db.query(User).filter(User.id == assigned_provider_id).first()
        
        return {
            "message": "Report auto-assigned successfully",
            "report_id": report_id,
            "assigned_provider_id": assigned_provider_id,
            "assigned_provider_name": provider.name if provider else "Unknown"
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/manual-assign-report")
async def manual_assign_report(
    report_id: int,
    provider_id: int,
    reason: Optional[str] = None,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Manually assign report to specific provider
    """
    try:
        success = assignment_service.manual_assign_report(report_id, provider_id, db)
        
        if success:
            # Get provider info
            provider = db.query(User).filter(User.id == provider_id).first()
            
            return {
                "message": "Report manually assigned successfully",
                "report_id": report_id,
                "assigned_provider_id": provider_id,
                "assigned_provider_name": provider.name if provider else "Unknown",
                "reason": reason
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to assign report"
            )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/reassign-report")
async def reassign_report(
    report_id: int,
    new_provider_id: int,
    reason: Optional[str] = None,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Reassign report to different provider
    """
    try:
        success = assignment_service.reassign_report(report_id, new_provider_id, db, reason)
        
        if success:
            # Get provider info
            provider = db.query(User).filter(User.id == new_provider_id).first()
            
            return {
                "message": "Report reassigned successfully",
                "report_id": report_id,
                "new_provider_id": new_provider_id,
                "new_provider_name": provider.name if provider else "Unknown",
                "reason": reason
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to reassign report"
            )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/notifications", response_model=List[NotificationResponse])
async def get_admin_notifications(
    unread_only: bool = False,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Get notifications for admin user
    
    High-risk patient alerts will appear here
    """
    query = db.query(Notification).filter(Notification.user_id == current_user.id)
    
    if unread_only:
        query = query.filter(Notification.read_at == None)
    
    notifications = query.order_by(desc(Notification.created_at)).limit(100).all()
    
    return notifications


@router.put("/notifications/{notification_id}")
async def update_notification(
    notification_id: str,
    update_data: NotificationUpdate,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Mark notification as read or acknowledged
    """
    notification = db.query(Notification).filter(
        Notification.id == notification_id,
        Notification.user_id == current_user.id
    ).first()
    
    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )
    
    if update_data.read and not notification.read_at:
        notification.read_at = datetime.utcnow()
    
    if update_data.acknowledged and not notification.acknowledged_at:
        notification.acknowledged_at = datetime.utcnow()
    
    db.commit()
    db.refresh(notification)
    
    return notification


@router.get("/high-risk-intakes")
async def get_high_risk_intakes(
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Get all high-risk intake sessions for review
    """
    high_risk_reports = db.query(IntakeReport).filter(
        IntakeReport.risk_level == "high"
    ).order_by(desc(IntakeReport.created_at)).all()
    
    return {
        "count": len(high_risk_reports),
        "reports": [
            {
                "id": report.id,
                "patient_id": report.patient_id,
                "risk_level": report.risk_level,
                "urgency": report.urgency,
                "created_at": report.created_at.isoformat(),
                "safety_assessment": report.report_data.get("safety_assessment"),
                "session_token": report.session.session_token if report.session else None
            }
            for report in high_risk_reports
        ]
    }


@router.get("/stats")
async def get_admin_stats(
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Get platform statistics for admin dashboard
    """
    total_intakes = db.query(IntakeSession).count()
    completed_intakes = db.query(IntakeSession).filter(IntakeSession.status == "completed").count()
    active_intakes = db.query(IntakeSession).filter(IntakeSession.status == "active").count()
    
    total_reports = db.query(IntakeReport).count()
    high_risk_count = db.query(IntakeReport).filter(IntakeReport.risk_level == "high").count()
    
    pending_providers = db.query(ProviderProfile).filter(
        ProviderProfile.approval_status == "pending"
    ).count()
    
    approved_providers = db.query(ProviderProfile).filter(
        ProviderProfile.approval_status == "approved"
    ).count()
    
    return {
        "intakes": {
            "total": total_intakes,
            "completed": completed_intakes,
            "active": active_intakes,
            "abandoned": total_intakes - completed_intakes - active_intakes
        },
        "reports": {
            "total": total_reports,
            "high_risk": high_risk_count
        },
        "providers": {
            "pending_approval": pending_providers,
            "approved": approved_providers
        }
    }


@router.post("/providers/{provider_id}/approve")
async def approve_provider(
    provider_id: str,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Approve a pending provider
    """
    provider_profile = db.query(ProviderProfile).filter(
        ProviderProfile.user_id == provider_id
    ).first()
    
    if not provider_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Provider profile not found"
        )
    
    if provider_profile.approval_status == "approved":
        return {"message": "Provider already approved", "status": "approved"}
    
    provider_profile.approval_status = "approved"
    provider_profile.approved_by = current_user.id
    provider_profile.approved_at = datetime.utcnow()
    
    db.commit()
    
    return {"message": "Provider approved successfully", "status": "approved"}


@router.get("/providers/pending")
async def get_pending_providers(
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Get all providers pending approval
    """
    pending = db.query(ProviderProfile).filter(
        ProviderProfile.approval_status == "pending"
    ).all()
    
    return {
        "count": len(pending),
        "providers": [
            {
                "user_id": p.user_id,
                "email": p.user.email if p.user else None,
                "name": f"{p.user.first_name} {p.user.last_name}" if p.user else None,
                "npi": p.npi,
                "license_number": p.license_number,
                "license_state": p.license_state,
                "specialty": p.specialty,
                "created_at": p.created_at.isoformat()
            }
            for p in pending
        ]
    }


@router.post("/assign-report")
async def assign_report_to_provider(
    request: AssignReportRequest,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Assign an intake report to a provider for review
    
    This is the core workflow for the pilot:
    1. Patient completes intake
    2. Admin reviews and assigns to appropriate provider
    3. Provider reviews report and provides clinical input
    """
    # Get report
    report = db.query(IntakeReport).filter(IntakeReport.id == request.report_id).first()
    
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found"
        )
    
    # Verify provider exists and is approved
    provider = db.query(User).filter(
        User.id == request.provider_id,
        User.role == UserRole.PROVIDER
    ).first()
    
    if not provider:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Provider not found"
        )
    
    # Check if provider is approved
    provider_profile = db.query(ProviderProfile).filter(
        ProviderProfile.user_id == request.provider_id
    ).first()
    
    if provider_profile and provider_profile.approval_status != "approved":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot assign to provider with status: {provider_profile.approval_status}"
        )
    
    # Assign report
    report.shared_with_provider_id = request.provider_id
    
    # Create notification for provider
    notification = Notification(
        user_id=request.provider_id,
        type="report_assigned",
        priority="medium",
        title="New Intake Report Assigned",
        message=f"A new intake report has been assigned to you for review.\n\nChief Complaint: {report.report_data.get('chief_complaint', 'N/A')}\nSeverity: {report.severity_level}\nRisk Level: {report.risk_level}",
        resource_type="intake_report",
        resource_id=report.id
    )
    db.add(notification)
    
    # Audit log
    audit = AuditLog(
        event_type="report_assigned",
        action="update",
        user_id=current_user.id,
        resource_type="intake_report",
        resource_id=report.id,
        event_metadata={
            "provider_id": request.provider_id,
            "notes": request.notes
        },
        timestamp=datetime.utcnow()
    )
    db.add(audit)
    
    db.commit()
    
    return {
        "message": "Report assigned successfully",
        "report_id": report.id,
        "provider_id": request.provider_id,
        "provider_notified": True
    }

