"""
Patient Portal API endpoints
"""

from datetime import datetime
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.patient_portal import (
    PatientDashboardResponse,
    AppointmentRequest,
    AppointmentResponse,
    AppointmentListResponse,
    AppointmentSlotResponse,
    HealthRecordsResponse,
    TaskListResponse,
    NotificationListResponse
)
from app.services.patient_portal_service import patient_portal_service
from app.core.rate_limit import limiter

router = APIRouter()


@router.get("/dashboard", response_model=PatientDashboardResponse)
async def get_patient_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get patient dashboard data"""
    
    if current_user.role != "patient":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Patient role required."
        )
    
    try:
        dashboard_data = patient_portal_service.get_patient_dashboard_data(
            patient_id=current_user.id,
            db=db
        )
        
        return PatientDashboardResponse(**dashboard_data)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get dashboard data: {str(e)}"
        )


@router.get("/appointments/upcoming", response_model=AppointmentListResponse)
async def get_upcoming_appointments(
    limit: int = 10,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get upcoming appointments for patient"""
    
    if current_user.role != "patient":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Patient role required."
        )
    
    try:
        appointments = patient_portal_service.get_upcoming_appointments(
            patient_id=current_user.id,
            db=db,
            limit=limit
        )
        
        return AppointmentListResponse(
            appointments=appointments,
            total_count=len(appointments)
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get upcoming appointments: {str(e)}"
        )


@router.get("/appointments/recent", response_model=AppointmentListResponse)
async def get_recent_appointments(
    limit: int = 10,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get recent appointments for patient"""
    
    if current_user.role != "patient":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Patient role required."
        )
    
    try:
        appointments = patient_portal_service.get_recent_appointments(
            patient_id=current_user.id,
            db=db,
            limit=limit
        )
        
        return AppointmentListResponse(
            appointments=appointments,
            total_count=len(appointments)
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get recent appointments: {str(e)}"
        )


@router.post("/appointments", response_model=AppointmentResponse)
@limiter.limit("10/minute")
async def create_appointment_request(
    request: Request,
    appointment_request: AppointmentRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create appointment request"""
    
    if current_user.role != "patient":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Patient role required."
        )
    
    try:
        result = patient_portal_service.create_appointment_request(
            patient_id=current_user.id,
            provider_id=appointment_request.provider_id,
            appointment_data=appointment_request.dict(),
            db=db
        )
        
        return AppointmentResponse(**result)
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create appointment request: {str(e)}"
        )


@router.post("/appointments/{appointment_id}/cancel", response_model=AppointmentResponse)
@limiter.limit("10/minute")
async def cancel_appointment(
    request: Request,
    appointment_id: int,
    cancellation_reason: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Cancel appointment"""
    
    if current_user.role != "patient":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Patient role required."
        )
    
    try:
        result = patient_portal_service.cancel_appointment(
            appointment_id=appointment_id,
            patient_id=current_user.id,
            cancellation_reason=cancellation_reason,
            db=db
        )
        
        return AppointmentResponse(**result)
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to cancel appointment: {str(e)}"
        )


@router.post("/appointments/{appointment_id}/reschedule", response_model=AppointmentResponse)
@limiter.limit("10/minute")
async def reschedule_appointment(
    request: Request,
    appointment_id: int,
    new_datetime: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Reschedule appointment"""
    
    if current_user.role != "patient":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Patient role required."
        )
    
    try:
        result = patient_portal_service.reschedule_appointment(
            appointment_id=appointment_id,
            patient_id=current_user.id,
            new_datetime=new_datetime,
            db=db
        )
        
        return AppointmentResponse(**result)
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to reschedule appointment: {str(e)}"
        )


@router.post("/appointments/{appointment_id}/confirm", response_model=AppointmentResponse)
@limiter.limit("10/minute")
async def confirm_appointment(
    request: Request,
    appointment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Confirm appointment"""
    
    if current_user.role != "patient":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Patient role required."
        )
    
    try:
        result = patient_portal_service.confirm_appointment(
            appointment_id=appointment_id,
            patient_id=current_user.id,
            db=db
        )
        
        return AppointmentResponse(**result)
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to confirm appointment: {str(e)}"
        )


@router.get("/appointments/available-slots", response_model=List[AppointmentSlotResponse])
async def get_available_slots(
    provider_id: int,
    start_date: str,
    end_date: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get available appointment slots for provider"""
    
    if current_user.role != "patient":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Patient role required."
        )
    
    try:
        slots = patient_portal_service.get_available_slots(
            provider_id=provider_id,
            date_range={"start": start_date, "end": end_date},
            db=db
        )
        
        return [AppointmentSlotResponse(**slot) for slot in slots]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get available slots: {str(e)}"
        )


@router.get("/health-records", response_model=HealthRecordsResponse)
async def get_health_records(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get patient health records"""
    
    if current_user.role != "patient":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Patient role required."
        )
    
    try:
        health_records = patient_portal_service.get_patient_health_records(
            patient_id=current_user.id,
            db=db
        )
        
        return HealthRecordsResponse(**health_records)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get health records: {str(e)}"
        )


@router.get("/tasks", response_model=TaskListResponse)
async def get_pending_tasks(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get pending tasks for patient"""
    
    if current_user.role != "patient":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Patient role required."
        )
    
    try:
        tasks = patient_portal_service.get_pending_tasks(
            patient_id=current_user.id,
            db=db
        )
        
        return TaskListResponse(
            tasks=tasks,
            total_count=len(tasks)
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get pending tasks: {str(e)}"
        )


@router.get("/notifications", response_model=NotificationListResponse)
async def get_notifications(
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get patient notifications"""
    
    if current_user.role != "patient":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Patient role required."
        )
    
    try:
        notifications = patient_portal_service.get_patient_notifications(
            patient_id=current_user.id,
            db=db,
            limit=limit
        )
        
        return NotificationListResponse(
            notifications=notifications,
            total_count=len(notifications)
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get notifications: {str(e)}"
        )
