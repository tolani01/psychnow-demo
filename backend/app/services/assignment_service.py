"""
Assignment Service for Patient-Provider Matching
Handles auto-assignment, workload balancing, and provider capacity management
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_, func, desc

from app.models.user import User
from app.models.intake_report import IntakeReport
from app.models.provider_review import ProviderReview
from app.models.notification import Notification
from app.services.notification_service import notification_service


class AssignmentService:
    """Service for managing patient-provider assignments"""
    
    def __init__(self):
        self.notification_service = notification_service
    
    def get_available_providers(self, db: Session) -> List[User]:
        """Get list of available providers (active and approved)"""
        return db.query(User).filter(
            User.role == "provider",
            User.is_active == True,
            User.provider_profile.has(is_approved=True)
        ).all()
    
    def calculate_provider_workload(self, provider_id: int, db: Session) -> Dict[str, int]:
        """Calculate provider's current workload"""
        
        # Count pending reports assigned to provider
        pending_reports = db.query(IntakeReport).filter(
            IntakeReport.assigned_provider_id == provider_id,
            IntakeReport.review_status.in_(["pending", "in_review"])
        ).count()
        
        # Count high-risk reports assigned to provider
        high_risk_reports = db.query(IntakeReport).filter(
            IntakeReport.assigned_provider_id == provider_id,
            IntakeReport.risk_level == "high",
            IntakeReport.review_status.in_(["pending", "in_review"])
        ).count()
        
        # Count reports reviewed in last 7 days (activity indicator)
        recent_reviews = db.query(ProviderReview).filter(
            ProviderReview.provider_id == provider_id,
            ProviderReview.created_at >= datetime.utcnow() - timedelta(days=7)
        ).count()
        
        # Calculate workload score (higher = more busy)
        workload_score = pending_reports + (high_risk_reports * 2)
        
        return {
            "pending_reports": pending_reports,
            "high_risk_reports": high_risk_reports,
            "recent_reviews": recent_reviews,
            "workload_score": workload_score
        }
    
    def get_provider_capacity(self, provider_id: int, db: Session) -> Dict[str, any]:
        """Get provider's capacity and preferences"""
        provider = db.query(User).filter(User.id == provider_id).first()
        if not provider or not provider.provider_profile:
            return {"max_caseload": 50, "specializations": [], "availability": "full_time"}
        
        profile = provider.provider_profile
        return {
            "max_caseload": profile.max_caseload or 50,
            "specializations": profile.specializations or [],
            "availability": profile.availability or "full_time",
            "preferred_patient_types": profile.preferred_patient_types or []
        }
    
    def auto_assign_report(self, report_id: int, db: Session) -> Optional[int]:
        """Auto-assign report to least-busy available provider"""
        
        # Get the report
        report = db.query(IntakeReport).filter(IntakeReport.id == report_id).first()
        if not report:
            raise ValueError(f"Report with ID {report_id} not found")
        
        # Check if already assigned
        if report.assigned_provider_id:
            print(f"Report {report_id} already assigned to provider {report.assigned_provider_id}")
            return report.assigned_provider_id
        
        # Get available providers
        available_providers = self.get_available_providers(db)
        if not available_providers:
            raise ValueError("No available providers found")
        
        # Calculate workload for each provider
        provider_workloads = {}
        for provider in available_providers:
            workload = self.calculate_provider_workload(provider.id, db)
            capacity = self.get_provider_capacity(provider.id, db)
            
            # Check if provider is at capacity
            if workload["pending_reports"] >= capacity["max_caseload"]:
                continue
            
            # Consider specializations if available
            specialization_bonus = 0
            if capacity["specializations"]:
                # Check if report matches provider specializations
                report_conditions = self._extract_report_conditions(report)
                for condition in report_conditions:
                    if condition.lower() in [spec.lower() for spec in capacity["specializations"]]:
                        specialization_bonus = -5  # Prefer this provider
                        break
            
            # Final workload score (lower is better)
            final_score = workload["workload_score"] + specialization_bonus
            
            provider_workloads[provider.id] = {
                "provider": provider,
                "workload": workload,
                "capacity": capacity,
                "final_score": final_score
            }
        
        if not provider_workloads:
            raise ValueError("All providers are at capacity")
        
        # Assign to provider with lowest workload score
        best_provider_id = min(provider_workloads.keys(), 
                              key=lambda pid: provider_workloads[pid]["final_score"])
        
        # Update report assignment
        report.assigned_provider_id = best_provider_id
        report.assigned_at = datetime.utcnow()
        report.review_status = "pending"
        
        db.commit()
        
        # Send notification to assigned provider
        import asyncio
        asyncio.create_task(self.notification_service.create_provider_assignment(
            best_provider_id, 
            report.patient_name or "Unknown Patient", 
            report_id, 
            db
        ))
        
        provider_info = provider_workloads[best_provider_id]["provider"]
        print(f"Report {report_id} auto-assigned to provider {provider_info.name} (ID: {best_provider_id})")
        
        return best_provider_id
    
    def manual_assign_report(self, report_id: int, provider_id: int, db: Session) -> bool:
        """Manually assign report to specific provider"""
        
        # Get the report
        report = db.query(IntakeReport).filter(IntakeReport.id == report_id).first()
        if not report:
            raise ValueError(f"Report with ID {report_id} not found")
        
        # Verify provider exists and is available
        provider = db.query(User).filter(
            User.id == provider_id,
            User.role == "provider",
            User.is_active == True,
            User.provider_profile.has(is_approved=True)
        ).first()
        
        if not provider:
            raise ValueError(f"Provider with ID {provider_id} not found or not available")
        
        # Check provider capacity
        capacity = self.get_provider_capacity(provider_id, db)
        workload = self.calculate_provider_workload(provider_id, db)
        
        if workload["pending_reports"] >= capacity["max_caseload"]:
            raise ValueError(f"Provider {provider.name} is at maximum capacity ({capacity['max_caseload']} reports)")
        
        # Update report assignment
        report.assigned_provider_id = provider_id
        report.assigned_at = datetime.utcnow()
        report.review_status = "pending"
        
        db.commit()
        
        # Send notification to assigned provider
        import asyncio
        asyncio.create_task(self.notification_service.create_provider_assignment(
            provider_id, 
            report.patient_name or "Unknown Patient", 
            report_id, 
            db
        ))
        
        print(f"Report {report_id} manually assigned to provider {provider.name}")
        return True
    
    def reassign_report(self, report_id: int, new_provider_id: int, db: Session, reason: str = None) -> bool:
        """Reassign report to different provider"""
        
        # Get the report
        report = db.query(IntakeReport).filter(IntakeReport.id == report_id).first()
        if not report:
            raise ValueError(f"Report with ID {report_id} not found")
        
        old_provider_id = report.assigned_provider_id
        
        # Assign to new provider
        success = self.manual_assign_report(report_id, new_provider_id, db)
        
        if success and old_provider_id:
            # Notify old provider about reassignment
            import asyncio
            asyncio.create_task(self.notification_service.create_system_notification(
                "Report Reassigned",
                f"Report #{report_id} has been reassigned to another provider{f' ({reason})' if reason else ''}",
                target_role="provider",
                data={"report_id": report_id, "reason": reason},
                db=db
            ))
        
        return success
    
    def get_provider_assigned_reports(
        self, 
        provider_id: int, 
        status_filter: Optional[str] = None,
        risk_level_filter: Optional[str] = None,
        limit: int = 50,
        db: Session = None
    ) -> List[IntakeReport]:
        """Get reports assigned to specific provider with optional filters"""
        
        query = db.query(IntakeReport).filter(
            IntakeReport.assigned_provider_id == provider_id
        )
        
        if status_filter:
            query = query.filter(IntakeReport.review_status == status_filter)
        
        if risk_level_filter:
            query = query.filter(IntakeReport.risk_level == risk_level_filter)
        
        return query.order_by(
            desc(IntakeReport.risk_level),
            desc(IntakeReport.assigned_at)
        ).limit(limit).all()
    
    def get_unassigned_reports(self, db: Session, limit: int = 50) -> List[IntakeReport]:
        """Get reports that haven't been assigned to any provider"""
        return db.query(IntakeReport).filter(
            IntakeReport.assigned_provider_id.is_(None)
        ).order_by(
            desc(IntakeReport.risk_level),
            desc(IntakeReport.created_at)
        ).limit(limit).all()
    
    def get_assignment_stats(self, db: Session) -> Dict[str, any]:
        """Get assignment statistics for admin dashboard"""
        
        # Total reports
        total_reports = db.query(IntakeReport).count()
        
        # Assigned vs unassigned
        assigned_reports = db.query(IntakeReport).filter(
            IntakeReport.assigned_provider_id.isnot(None)
        ).count()
        
        unassigned_reports = total_reports - assigned_reports
        
        # Reports by status
        pending_reports = db.query(IntakeReport).filter(
            IntakeReport.review_status == "pending"
        ).count()
        
        in_review_reports = db.query(IntakeReport).filter(
            IntakeReport.review_status == "in_review"
        ).count()
        
        completed_reports = db.query(IntakeReport).filter(
            IntakeReport.review_status == "completed"
        ).count()
        
        # High-risk unassigned reports
        high_risk_unassigned = db.query(IntakeReport).filter(
            and_(
                IntakeReport.assigned_provider_id.is_(None),
                IntakeReport.risk_level == "high"
            )
        ).count()
        
        # Provider workload distribution
        provider_workloads = []
        available_providers = self.get_available_providers(db)
        
        for provider in available_providers:
            workload = self.calculate_provider_workload(provider.id, db)
            capacity = self.get_provider_capacity(provider.id, db)
            
            provider_workloads.append({
                "provider_id": provider.id,
                "provider_name": provider.name,
                "pending_reports": workload["pending_reports"],
                "high_risk_reports": workload["high_risk_reports"],
                "max_caseload": capacity["max_caseload"],
                "utilization_percent": (workload["pending_reports"] / capacity["max_caseload"]) * 100
            })
        
        return {
            "total_reports": total_reports,
            "assigned_reports": assigned_reports,
            "unassigned_reports": unassigned_reports,
            "high_risk_unassigned": high_risk_unassigned,
            "reports_by_status": {
                "pending": pending_reports,
                "in_review": in_review_reports,
                "completed": completed_reports
            },
            "provider_workloads": provider_workloads,
            "assignment_rate": (assigned_reports / total_reports * 100) if total_reports > 0 else 0
        }
    
    def _extract_report_conditions(self, report: IntakeReport) -> List[str]:
        """Extract medical conditions from report for specialization matching"""
        conditions = []
        
        # Extract from screener scores
        if report.screener_scores:
            for screener_name, score_data in report.screener_scores.items():
                if isinstance(score_data, dict) and score_data.get("score", 0) > 10:
                    conditions.append(screener_name.replace("-", " ").title())
        
        # Extract from report data
        if report.report_data:
            report_data = report.report_data
            if isinstance(report_data, dict):
                # Look for specific conditions in the report
                if "chief_complaint" in report_data:
                    complaint = report_data["chief_complaint"].lower()
                    if "depression" in complaint:
                        conditions.append("Depression")
                    if "anxiety" in complaint:
                        conditions.append("Anxiety")
                    if "trauma" in complaint or "ptsd" in complaint:
                        conditions.append("Trauma")
                    if "adhd" in complaint or "attention" in complaint:
                        conditions.append("ADHD")
                    if "bipolar" in complaint or "mania" in complaint:
                        conditions.append("Bipolar Disorder")
                    if "substance" in complaint or "alcohol" in complaint:
                        conditions.append("Substance Use")
        
        return list(set(conditions))  # Remove duplicates
    
    def get_provider_performance_metrics(self, provider_id: int, days: int = 30, db: Session = None) -> Dict[str, any]:
        """Get performance metrics for a specific provider"""
        
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        # Reviews completed in time period
        reviews_completed = db.query(ProviderReview).filter(
            ProviderReview.provider_id == provider_id,
            ProviderReview.created_at >= cutoff_date
        ).count()
        
        # Average review time
        reviews_with_times = db.query(ProviderReview).filter(
            ProviderReview.provider_id == provider_id,
            ProviderReview.created_at >= cutoff_date,
            ProviderReview.review_start_time.isnot(None)
        ).all()
        
        avg_review_time = 0
        if reviews_with_times:
            total_time = sum([
                (review.created_at - review.review_start_time).total_seconds() / 60 
                for review in reviews_with_times 
                if review.review_start_time
            ])
            avg_review_time = total_time / len(reviews_with_times)
        
        # High-risk cases handled
        high_risk_reviews = db.query(ProviderReview).join(IntakeReport).filter(
            ProviderReview.provider_id == provider_id,
            ProviderReview.created_at >= cutoff_date,
            IntakeReport.risk_level == "high"
        ).count()
        
        # Patient satisfaction (if available)
        # This would require patient feedback system
        
        return {
            "reviews_completed": reviews_completed,
            "avg_review_time_minutes": round(avg_review_time, 1),
            "high_risk_cases_handled": high_risk_reviews,
            "period_days": days
        }


# Global assignment service instance
assignment_service = AssignmentService()
