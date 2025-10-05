"""
Patient Portal Pydantic schemas
"""

from datetime import datetime
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class AppointmentRequest(BaseModel):
    """Schema for appointment request"""
    provider_id: int
    appointment_type: str = Field(default="consultation", description="Type of appointment")
    scheduled_start: str = Field(..., description="ISO datetime string")
    scheduled_end: str = Field(..., description="ISO datetime string")
    duration_minutes: int = Field(default=60, ge=15, le=240)
    location_type: str = Field(default="virtual", description="virtual, in-person, phone")
    location_details: Optional[str] = None
    reason_for_visit: Optional[str] = None
    notes: Optional[str] = None


class AppointmentResponse(BaseModel):
    """Schema for appointment response"""
    success: bool
    appointment_id: Optional[int] = None
    status: Optional[str] = None
    message: str
    new_scheduled_start: Optional[str] = None


class AppointmentSlot(BaseModel):
    """Schema for appointment slot"""
    start: str = Field(..., description="ISO datetime string")
    end: str = Field(..., description="ISO datetime string")
    duration_minutes: int
    available: bool


class AppointmentSlotResponse(AppointmentSlot):
    """Schema for appointment slot response"""
    pass


class AppointmentSummary(BaseModel):
    """Schema for appointment summary"""
    id: int
    type: str
    status: str
    scheduled_start: str
    scheduled_end: str
    duration_minutes: int
    location_type: str
    location_details: Optional[str] = None
    meeting_link: Optional[str] = None
    reason_for_visit: Optional[str] = None
    provider_name: str
    can_cancel: bool
    can_reschedule: bool
    reminder_sent: bool
    confirmation_sent: bool


class RecentAppointment(BaseModel):
    """Schema for recent appointment"""
    id: int
    type: str
    status: str
    scheduled_start: str
    actual_start: Optional[str] = None
    actual_end: Optional[str] = None
    duration_minutes: int
    location_type: str
    reason_for_visit: Optional[str] = None
    provider_name: str
    notes: Optional[str] = None
    provider_notes: Optional[str] = None
    cancellation_reason: Optional[str] = None


class AppointmentListResponse(BaseModel):
    """Schema for appointment list response"""
    appointments: List[AppointmentSummary]
    total_count: int


class RecentAppointmentListResponse(BaseModel):
    """Schema for recent appointment list response"""
    appointments: List[RecentAppointment]
    total_count: int


class IntakeReportSummary(BaseModel):
    """Schema for intake report summary"""
    id: int
    created_at: str
    risk_level: str
    urgency: str
    severity_level: str
    review_status: str
    chief_complaint: Optional[str] = None
    summary: str


class IntakeSessionSummary(BaseModel):
    """Schema for intake session summary"""
    id: int
    created_at: str
    status: str
    completed_at: Optional[str] = None
    duration_minutes: Optional[int] = None


class HealthRecordsResponse(BaseModel):
    """Schema for health records response"""
    intake_reports: List[IntakeReportSummary]
    intake_sessions: List[IntakeSessionSummary]
    total_reports: int
    total_sessions: int


class TaskProgress(BaseModel):
    """Schema for task progress"""
    percentage: int
    conversation_messages: int
    completed_screeners: int
    current_phase: str


class PendingTask(BaseModel):
    """Schema for pending task"""
    type: str
    title: str
    description: str
    due_date: Optional[str] = None
    priority: str
    session_id: Optional[str] = None
    appointment_id: Optional[int] = None
    progress: Optional[TaskProgress] = None


class TaskListResponse(BaseModel):
    """Schema for task list response"""
    tasks: List[PendingTask]
    total_count: int


class NotificationSummary(BaseModel):
    """Schema for notification summary"""
    id: int
    type: str
    title: str
    message: str
    priority: str
    is_read: bool
    created_at: str
    data: Optional[Dict[str, Any]] = None


class NotificationListResponse(BaseModel):
    """Schema for notification list response"""
    notifications: List[NotificationSummary]
    total_count: int


class DashboardSummary(BaseModel):
    """Schema for dashboard summary"""
    next_appointment: Optional[AppointmentSummary] = None
    total_upcoming: int
    total_recent: int
    pending_tasks: int
    high_priority_tasks: int
    has_urgent_tasks: bool


class PatientDashboardResponse(BaseModel):
    """Schema for patient dashboard response"""
    upcoming_appointments: List[AppointmentSummary]
    recent_appointments: List[RecentAppointment]
    health_records: HealthRecordsResponse
    pending_tasks: List[PendingTask]
    notifications: List[NotificationSummary]
    dashboard_summary: DashboardSummary
