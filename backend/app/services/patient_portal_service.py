"""
Patient Portal Service
Handles patient portal functionality including appointments, health records, and messaging
"""

import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from app.models.user import User
from app.models.appointment import Appointment, AppointmentStatus, AppointmentType
from app.models.intake_report import IntakeReport
from app.models.intake_session import IntakeSession
from app.services.notification_service import notification_service


class PatientPortalService:
    """Service for patient portal functionality"""
    
    def __init__(self):
        self.notification_service = notification_service
    
    def get_patient_dashboard_data(
        self,
        patient_id: int,
        db: Session
    ) -> Dict[str, Any]:
        """Get comprehensive dashboard data for patient"""
        
        # Get upcoming appointments
        upcoming_appointments = self.get_upcoming_appointments(patient_id, db)
        
        # Get recent appointments
        recent_appointments = self.get_recent_appointments(patient_id, db, limit=5)
        
        # Get health records
        health_records = self.get_patient_health_records(patient_id, db)
        
        # Get pending tasks
        pending_tasks = self.get_pending_tasks(patient_id, db)
        
        # Get notifications
        notifications = self.get_patient_notifications(patient_id, db)
        
        return {
            "upcoming_appointments": upcoming_appointments,
            "recent_appointments": recent_appointments,
            "health_records": health_records,
            "pending_tasks": pending_tasks,
            "notifications": notifications,
            "dashboard_summary": self._generate_dashboard_summary(
                upcoming_appointments, recent_appointments, pending_tasks
            )
        }
    
    def get_upcoming_appointments(
        self,
        patient_id: int,
        db: Session,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get upcoming appointments for patient"""
        
        appointments = db.query(Appointment).filter(
            Appointment.patient_id == patient_id,
            Appointment.status.in_([
                AppointmentStatus.SCHEDULED,
                AppointmentStatus.CONFIRMED
            ]),
            Appointment.scheduled_start >= datetime.utcnow()
        ).order_by(Appointment.scheduled_start.asc()).limit(limit).all()
        
        return [
            {
                "id": apt.id,
                "type": apt.appointment_type.value,
                "status": apt.status.value,
                "scheduled_start": apt.scheduled_start.isoformat(),
                "scheduled_end": apt.scheduled_end.isoformat(),
                "duration_minutes": apt.duration_minutes,
                "location_type": apt.location_type,
                "location_details": apt.location_details,
                "meeting_link": apt.meeting_link,
                "reason_for_visit": apt.reason_for_visit,
                "provider_name": f"{apt.provider.first_name} {apt.provider.last_name}" if apt.provider else "Unknown Provider",
                "can_cancel": self._can_cancel_appointment(apt),
                "can_reschedule": self._can_reschedule_appointment(apt),
                "reminder_sent": apt.reminder_sent,
                "confirmation_sent": apt.confirmation_sent
            }
            for apt in appointments
        ]
    
    def get_recent_appointments(
        self,
        patient_id: int,
        db: Session,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get recent appointments for patient"""
        
        appointments = db.query(Appointment).filter(
            Appointment.patient_id == patient_id,
            Appointment.status.in_([
                AppointmentStatus.COMPLETED,
                AppointmentStatus.CANCELLED,
                AppointmentStatus.NO_SHOW
            ]),
            Appointment.scheduled_start < datetime.utcnow()
        ).order_by(Appointment.scheduled_start.desc()).limit(limit).all()
        
        return [
            {
                "id": apt.id,
                "type": apt.appointment_type.value,
                "status": apt.status.value,
                "scheduled_start": apt.scheduled_start.isoformat(),
                "actual_start": apt.actual_start.isoformat() if apt.actual_start else None,
                "actual_end": apt.actual_end.isoformat() if apt.actual_end else None,
                "duration_minutes": apt.duration_minutes,
                "location_type": apt.location_type,
                "reason_for_visit": apt.reason_for_visit,
                "provider_name": f"{apt.provider.first_name} {apt.provider.last_name}" if apt.provider else "Unknown Provider",
                "notes": apt.notes,
                "provider_notes": apt.provider_notes,
                "cancellation_reason": apt.cancellation_reason
            }
            for apt in appointments
        ]
    
    def get_patient_health_records(
        self,
        patient_id: int,
        db: Session
    ) -> Dict[str, Any]:
        """Get patient health records and reports"""
        
        # Get intake reports
        reports = db.query(IntakeReport).filter(
            IntakeReport.patient_id == patient_id
        ).order_by(IntakeReport.created_at.desc()).limit(20).all()
        
        # Get intake sessions
        sessions = db.query(IntakeSession).filter(
            IntakeSession.patient_id == patient_id
        ).order_by(IntakeSession.created_at.desc()).limit(10).all()
        
        return {
            "intake_reports": [
                {
                    "id": report.id,
                    "created_at": report.created_at.isoformat(),
                    "risk_level": report.risk_level,
                    "urgency": report.urgency,
                    "severity_level": report.severity_level,
                    "review_status": report.review_status,
                    "chief_complaint": report.report_data.get("chief_complaint") if report.report_data else None,
                    "summary": self._extract_report_summary(report.report_data)
                }
                for report in reports
            ],
            "intake_sessions": [
                {
                    "id": session.id,
                    "created_at": session.created_at.isoformat(),
                    "status": session.status,
                    "completed_at": session.completed_at.isoformat() if session.completed_at else None,
                    "duration_minutes": self._calculate_session_duration(session)
                }
                for session in sessions
            ],
            "total_reports": len(reports),
            "total_sessions": len(sessions)
        }
    
    def get_pending_tasks(
        self,
        patient_id: int,
        db: Session
    ) -> List[Dict[str, Any]]:
        """Get pending tasks for patient"""
        
        tasks = []
        
        # Check for incomplete intake sessions
        incomplete_sessions = db.query(IntakeSession).filter(
            IntakeSession.patient_id == patient_id,
            IntakeSession.status.in_(["active", "paused"])
        ).all()
        
        for session in incomplete_sessions:
            tasks.append({
                "type": "complete_intake",
                "title": "Complete Mental Health Assessment",
                "description": "Finish your mental health assessment to receive personalized care recommendations",
                "due_date": None,
                "priority": "high",
                "session_id": session.session_token,
                "progress": self._calculate_session_progress(session)
            })
        
        # Check for upcoming appointments that need confirmation
        upcoming_apts = db.query(Appointment).filter(
            Appointment.patient_id == patient_id,
            Appointment.status == AppointmentStatus.SCHEDULED,
            Appointment.scheduled_start >= datetime.utcnow(),
            Appointment.scheduled_start <= datetime.utcnow() + timedelta(days=2),
            Appointment.confirmation_sent == False
        ).all()
        
        for apt in upcoming_apts:
            tasks.append({
                "type": "confirm_appointment",
                "title": "Confirm Upcoming Appointment",
                "description": f"Please confirm your appointment with {apt.provider.first_name} {apt.provider.last_name}",
                "due_date": apt.scheduled_start.isoformat(),
                "priority": "medium",
                "appointment_id": apt.id
            })
        
        return tasks
    
    def get_patient_notifications(
        self,
        patient_id: int,
        db: Session,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """Get notifications for patient"""
        
        notifications = self.notification_service.get_user_notifications(
            user_id=patient_id,
            limit=limit,
            unread_only=False,
            db=db
        )
        
        return [
            {
                "id": notif.id,
                "type": notif.type,
                "title": notif.title,
                "message": notif.message,
                "priority": notif.priority,
                "is_read": notif.is_read,
                "created_at": notif.created_at.isoformat(),
                "data": notif.data
            }
            for notif in notifications
        ]
    
    def create_appointment_request(
        self,
        patient_id: int,
        provider_id: int,
        appointment_data: Dict[str, Any],
        db: Session
    ) -> Dict[str, Any]:
        """Create appointment request from patient"""
        
        # Validate appointment data
        if not self._validate_appointment_data(appointment_data):
            raise ValueError("Invalid appointment data")
        
        # Create appointment
        appointment = Appointment(
            patient_id=patient_id,
            provider_id=provider_id,
            appointment_type=AppointmentType(appointment_data.get("type", "consultation")),
            status=AppointmentStatus.SCHEDULED,
            scheduled_start=datetime.fromisoformat(appointment_data["scheduled_start"]),
            scheduled_end=datetime.fromisoformat(appointment_data["scheduled_end"]),
            duration_minutes=appointment_data.get("duration_minutes", 60),
            location_type=appointment_data.get("location_type", "virtual"),
            location_details=appointment_data.get("location_details"),
            reason_for_visit=appointment_data.get("reason_for_visit"),
            notes=appointment_data.get("notes"),
            created_by=patient_id,
            created_at=datetime.utcnow()
        )
        
        db.add(appointment)
        db.commit()
        db.refresh(appointment)
        
        # Send notification to provider
        self.notification_service.create_notification(
            user_id=provider_id,
            type="appointment_request",
            title="New Appointment Request",
            message=f"Patient has requested an appointment for {appointment.scheduled_start.strftime('%B %d, %Y at %I:%M %p')}",
            priority="medium",
            data={
                "appointment_id": appointment.id,
                "patient_id": patient_id,
                "scheduled_start": appointment.scheduled_start.isoformat()
            },
            db=db
        )
        
        return {
            "success": True,
            "appointment_id": appointment.id,
            "status": appointment.status.value,
            "message": "Appointment request created successfully"
        }
    
    def cancel_appointment(
        self,
        appointment_id: int,
        patient_id: int,
        cancellation_reason: str,
        db: Session
    ) -> Dict[str, Any]:
        """Cancel appointment by patient"""
        
        appointment = db.query(Appointment).filter(
            Appointment.id == appointment_id,
            Appointment.patient_id == patient_id
        ).first()
        
        if not appointment:
            raise ValueError("Appointment not found")
        
        if not self._can_cancel_appointment(appointment):
            raise ValueError("Appointment cannot be cancelled at this time")
        
        # Update appointment
        appointment.status = AppointmentStatus.CANCELLED
        appointment.cancellation_reason = cancellation_reason
        appointment.cancelled_by = patient_id
        appointment.cancelled_at = datetime.utcnow()
        appointment.updated_at = datetime.utcnow()
        
        db.commit()
        
        # Send notification to provider
        self.notification_service.create_notification(
            user_id=appointment.provider_id,
            type="appointment_cancelled",
            title="Appointment Cancelled",
            message=f"Patient has cancelled their appointment scheduled for {appointment.scheduled_start.strftime('%B %d, %Y at %I:%M %p')}",
            priority="medium",
            data={
                "appointment_id": appointment.id,
                "patient_id": patient_id,
                "cancellation_reason": cancellation_reason
            },
            db=db
        )
        
        return {
            "success": True,
            "message": "Appointment cancelled successfully"
        }
    
    def reschedule_appointment(
        self,
        appointment_id: int,
        patient_id: int,
        new_datetime: str,
        db: Session
    ) -> Dict[str, Any]:
        """Reschedule appointment by patient"""
        
        appointment = db.query(Appointment).filter(
            Appointment.id == appointment_id,
            Appointment.patient_id == patient_id
        ).first()
        
        if not appointment:
            raise ValueError("Appointment not found")
        
        if not self._can_reschedule_appointment(appointment):
            raise ValueError("Appointment cannot be rescheduled at this time")
        
        # Calculate new end time
        new_start = datetime.fromisoformat(new_datetime)
        new_end = new_start + timedelta(minutes=appointment.duration_minutes)
        
        # Update appointment
        old_start = appointment.scheduled_start
        appointment.scheduled_start = new_start
        appointment.scheduled_end = new_end
        appointment.updated_at = datetime.utcnow()
        
        db.commit()
        
        # Send notification to provider
        self.notification_service.create_notification(
            user_id=appointment.provider_id,
            type="appointment_rescheduled",
            title="Appointment Rescheduled",
            message=f"Patient has rescheduled their appointment from {old_start.strftime('%B %d, %Y at %I:%M %p')} to {new_start.strftime('%B %d, %Y at %I:%M %p')}",
            priority="medium",
            data={
                "appointment_id": appointment.id,
                "patient_id": patient_id,
                "old_start": old_start.isoformat(),
                "new_start": new_start.isoformat()
            },
            db=db
        )
        
        return {
            "success": True,
            "message": "Appointment rescheduled successfully",
            "new_scheduled_start": new_start.isoformat()
        }
    
    def confirm_appointment(
        self,
        appointment_id: int,
        patient_id: int,
        db: Session
    ) -> Dict[str, Any]:
        """Confirm appointment by patient"""
        
        appointment = db.query(Appointment).filter(
            Appointment.id == appointment_id,
            Appointment.patient_id == patient_id,
            Appointment.status == AppointmentStatus.SCHEDULED
        ).first()
        
        if not appointment:
            raise ValueError("Appointment not found or cannot be confirmed")
        
        # Update appointment
        appointment.status = AppointmentStatus.CONFIRMED
        appointment.confirmation_sent = True
        appointment.updated_at = datetime.utcnow()
        
        db.commit()
        
        # Send notification to provider
        self.notification_service.create_notification(
            user_id=appointment.provider_id,
            type="appointment_confirmed",
            title="Appointment Confirmed",
            message=f"Patient has confirmed their appointment for {appointment.scheduled_start.strftime('%B %d, %Y at %I:%M %p')}",
            priority="low",
            data={
                "appointment_id": appointment.id,
                "patient_id": patient_id
            },
            db=db
        )
        
        return {
            "success": True,
            "message": "Appointment confirmed successfully"
        }
    
    def get_available_slots(
        self,
        provider_id: int,
        date_range: Dict[str, str],
        db: Session
    ) -> List[Dict[str, Any]]:
        """Get available appointment slots for provider"""
        
        start_date = datetime.fromisoformat(date_range["start"])
        end_date = datetime.fromisoformat(date_range["end"])
        
        # Get existing appointments for provider in date range
        existing_appointments = db.query(Appointment).filter(
            Appointment.provider_id == provider_id,
            Appointment.scheduled_start >= start_date,
            Appointment.scheduled_start <= end_date,
            Appointment.status.in_([
                AppointmentStatus.SCHEDULED,
                AppointmentStatus.CONFIRMED,
                AppointmentStatus.IN_PROGRESS
            ])
        ).all()
        
        # Generate available slots (simplified - in production, use provider's schedule)
        available_slots = []
        current_date = start_date
        
        while current_date <= end_date:
            # Skip weekends for now
            if current_date.weekday() < 5:  # Monday = 0, Friday = 4
                # Generate hourly slots from 9 AM to 5 PM
                for hour in range(9, 17):
                    slot_start = current_date.replace(hour=hour, minute=0, second=0, microsecond=0)
                    slot_end = slot_start + timedelta(hours=1)
                    
                    # Check if slot is available
                    is_available = not any(
                        apt.scheduled_start <= slot_start < apt.scheduled_end or
                        apt.scheduled_start < slot_end <= apt.scheduled_end
                        for apt in existing_appointments
                    )
                    
                    if is_available:
                        available_slots.append({
                            "start": slot_start.isoformat(),
                            "end": slot_end.isoformat(),
                            "duration_minutes": 60,
                            "available": True
                        })
            
            current_date += timedelta(days=1)
        
        return available_slots
    
    def _validate_appointment_data(self, data: Dict[str, Any]) -> bool:
        """Validate appointment request data"""
        
        required_fields = ["scheduled_start", "scheduled_end"]
        for field in required_fields:
            if field not in data:
                return False
        
        try:
            start = datetime.fromisoformat(data["scheduled_start"])
            end = datetime.fromisoformat(data["scheduled_end"])
            
            if start >= end:
                return False
            
            if start <= datetime.utcnow():
                return False
                
        except ValueError:
            return False
        
        return True
    
    def _can_cancel_appointment(self, appointment: Appointment) -> bool:
        """Check if appointment can be cancelled"""
        
        # Can cancel if more than 24 hours in advance
        time_until_appointment = appointment.scheduled_start - datetime.utcnow()
        return time_until_appointment.total_seconds() > 24 * 3600
    
    def _can_reschedule_appointment(self, appointment: Appointment) -> bool:
        """Check if appointment can be rescheduled"""
        
        # Can reschedule if more than 24 hours in advance
        time_until_appointment = appointment.scheduled_start - datetime.utcnow()
        return time_until_appointment.total_seconds() > 24 * 3600
    
    def _extract_report_summary(self, report_data: Dict[str, Any]) -> str:
        """Extract summary from report data"""
        
        if not report_data:
            return "No summary available"
        
        summary = report_data.get("summary_impression", "")
        if not summary:
            summary = report_data.get("chief_complaint", "Assessment completed")
        
        return summary[:200] + "..." if len(summary) > 200 else summary
    
    def _calculate_session_duration(self, session: IntakeSession) -> Optional[int]:
        """Calculate session duration in minutes"""
        
        if session.created_at and session.completed_at:
            duration = session.completed_at - session.created_at
            return int(duration.total_seconds() / 60)
        
        return None
    
    def _calculate_session_progress(self, session: IntakeSession) -> Dict[str, Any]:
        """Calculate progress of incomplete session"""
        
        conversation_length = len(session.conversation_history or [])
        completed_screeners = len(session.completed_screeners or [])
        
        # Estimate progress based on conversation length and completed screeners
        estimated_progress = min(100, (conversation_length * 2) + (completed_screeners * 10))
        
        return {
            "percentage": estimated_progress,
            "conversation_messages": conversation_length,
            "completed_screeners": completed_screeners,
            "current_phase": session.current_phase
        }
    
    def _generate_dashboard_summary(
        self,
        upcoming_appointments: List[Dict[str, Any]],
        recent_appointments: List[Dict[str, Any]],
        pending_tasks: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate dashboard summary"""
        
        next_appointment = upcoming_appointments[0] if upcoming_appointments else None
        high_priority_tasks = [task for task in pending_tasks if task["priority"] == "high"]
        
        return {
            "next_appointment": next_appointment,
            "total_upcoming": len(upcoming_appointments),
            "total_recent": len(recent_appointments),
            "pending_tasks": len(pending_tasks),
            "high_priority_tasks": len(high_priority_tasks),
            "has_urgent_tasks": len(high_priority_tasks) > 0
        }


# Global patient portal service instance
patient_portal_service = PatientPortalService()
