"""
Billing Service
Handles billing, invoicing, and payment processing
"""

import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc

from app.models.billing import (
    Invoice, InvoiceLineItem, Payment, InsuranceClaim, BillingSettings, 
    BillingNotification, PaymentStatus, PaymentMethod, BillingStatus
)
from app.models.appointment import Appointment
from app.models.user import User
from app.services.notification_service import notification_service


class BillingService:
    """Service for billing and payment processing"""
    
    def __init__(self):
        self.notification_service = notification_service
    
    def create_invoice(
        self,
        patient_id: int,
        provider_id: int,
        appointment_id: Optional[int] = None,
        line_items: List[Dict[str, Any]] = None,
        db: Session = None
    ) -> Dict[str, Any]:
        """Create a new invoice"""
        
        if line_items is None:
            line_items = []
        
        # Get billing settings for provider
        billing_settings = db.query(BillingSettings).filter(
            BillingSettings.provider_id == provider_id
        ).first()
        
        # Generate invoice number
        invoice_number = self._generate_invoice_number()
        
        # Calculate totals
        subtotal = Decimal('0.00')
        for item in line_items:
            quantity = Decimal(str(item.get('quantity', 1)))
            unit_price = Decimal(str(item.get('unit_price', 0)))
            subtotal += quantity * unit_price
        
        tax_rate = billing_settings.tax_rate if billing_settings else Decimal('0.00')
        tax_amount = subtotal * tax_rate
        discount_amount = Decimal('0.00')  # Can be added later
        total_amount = subtotal + tax_amount - discount_amount
        
        # Determine due date
        payment_terms = billing_settings.default_payment_terms if billing_settings else "Net 30"
        due_date = datetime.utcnow() + timedelta(days=self._parse_payment_terms(payment_terms))
        
        # Create invoice
        invoice = Invoice(
            invoice_number=invoice_number,
            patient_id=patient_id,
            provider_id=provider_id,
            appointment_id=appointment_id,
            subtotal=subtotal,
            tax_amount=tax_amount,
            discount_amount=discount_amount,
            total_amount=total_amount,
            status=BillingStatus.DRAFT,
            issue_date=datetime.utcnow(),
            due_date=due_date,
            payment_terms=payment_terms
        )
        
        db.add(invoice)
        db.commit()
        db.refresh(invoice)
        
        # Create line items
        for item_data in line_items:
            line_item = InvoiceLineItem(
                invoice_id=invoice.id,
                description=item_data.get('description', ''),
                quantity=Decimal(str(item_data.get('quantity', 1))),
                unit_price=Decimal(str(item_data.get('unit_price', 0))),
                line_total=Decimal(str(item_data.get('quantity', 1))) * Decimal(str(item_data.get('unit_price', 0))),
                service_code=item_data.get('service_code'),
                service_category=item_data.get('service_category')
            )
            db.add(line_item)
        
        db.commit()
        
        # Send notification to patient
        self.notification_service.create_notification(
            user_id=patient_id,
            type="invoice_created",
            title="New Invoice Available",
            message=f"Invoice {invoice_number} has been created for your recent appointment.",
            priority="medium",
            data={
                "invoice_id": invoice.id,
                "invoice_number": invoice_number,
                "total_amount": str(total_amount)
            },
            db=db
        )
        
        return {
            "success": True,
            "invoice_id": invoice.id,
            "invoice_number": invoice_number,
            "total_amount": str(total_amount),
            "due_date": due_date.isoformat()
        }
    
    def send_invoice(
        self,
        invoice_id: int,
        db: Session
    ) -> Dict[str, Any]:
        """Send invoice to patient"""
        
        invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
        if not invoice:
            raise ValueError("Invoice not found")
        
        # Update status
        invoice.status = BillingStatus.SENT
        invoice.updated_at = datetime.utcnow()
        db.commit()
        
        # Send notification
        self.notification_service.create_notification(
            user_id=invoice.patient_id,
            type="invoice_sent",
            title="Invoice Sent",
            message=f"Invoice {invoice.invoice_number} has been sent to you.",
            priority="medium",
            data={
                "invoice_id": invoice.id,
                "invoice_number": invoice.invoice_number,
                "total_amount": str(invoice.total_amount),
                "due_date": invoice.due_date.isoformat()
            },
            db=db
        )
        
        return {
            "success": True,
            "message": "Invoice sent successfully"
        }
    
    def process_payment(
        self,
        invoice_id: int,
        payment_data: Dict[str, Any],
        db: Session
    ) -> Dict[str, Any]:
        """Process payment for invoice"""
        
        invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
        if not invoice:
            raise ValueError("Invoice not found")
        
        # Generate payment number
        payment_number = self._generate_payment_number()
        
        # Create payment record
        payment = Payment(
            payment_number=payment_number,
            invoice_id=invoice_id,
            patient_id=invoice.patient_id,
            amount=Decimal(str(payment_data.get('amount', invoice.total_amount))),
            payment_method=PaymentMethod(payment_data.get('payment_method', 'credit_card')),
            status=PaymentStatus.PROCESSING,
            transaction_id=payment_data.get('transaction_id'),
            gateway_response=json.dumps(payment_data.get('gateway_response', {})),
            notes=payment_data.get('notes')
        )
        
        db.add(payment)
        db.commit()
        db.refresh(payment)
        
        # Process payment with gateway (simplified)
        try:
            # In real implementation, integrate with Stripe, PayPal, etc.
            success = self._process_payment_gateway(payment_data)
            
            if success:
                payment.status = PaymentStatus.COMPLETED
                payment.payment_date = datetime.utcnow()
                payment.processed_date = datetime.utcnow()
                
                # Update invoice status
                invoice.status = BillingStatus.PAID
                invoice.paid_date = datetime.utcnow()
                invoice.updated_at = datetime.utcnow()
                
                # Send notifications
                self.notification_service.create_notification(
                    user_id=invoice.patient_id,
                    type="payment_received",
                    title="Payment Received",
                    message=f"Payment of ${payment.amount} has been processed successfully.",
                    priority="low",
                    data={
                        "payment_id": payment.id,
                        "amount": str(payment.amount),
                        "invoice_number": invoice.invoice_number
                    },
                    db=db
                )
                
                self.notification_service.create_notification(
                    user_id=invoice.provider_id,
                    type="payment_received",
                    title="Payment Received",
                    message=f"Payment of ${payment.amount} received for invoice {invoice.invoice_number}.",
                    priority="low",
                    data={
                        "payment_id": payment.id,
                        "amount": str(payment.amount),
                        "invoice_number": invoice.invoice_number
                    },
                    db=db
                )
            else:
                payment.status = PaymentStatus.FAILED
                
                self.notification_service.create_notification(
                    user_id=invoice.patient_id,
                    type="payment_failed",
                    title="Payment Failed",
                    message=f"Payment of ${payment.amount} failed to process. Please try again.",
                    priority="high",
                    data={
                        "payment_id": payment.id,
                        "amount": str(payment.amount),
                        "invoice_number": invoice.invoice_number
                    },
                    db=db
                )
            
            db.commit()
            
            return {
                "success": success,
                "payment_id": payment.id,
                "payment_number": payment_number,
                "status": payment.status.value,
                "message": "Payment processed successfully" if success else "Payment failed to process"
            }
            
        except Exception as e:
            payment.status = PaymentStatus.FAILED
            db.commit()
            raise Exception(f"Payment processing error: {str(e)}")
    
    def get_patient_invoices(
        self,
        patient_id: int,
        status: Optional[str] = None,
        limit: int = 50,
        db: Session = None
    ) -> List[Dict[str, Any]]:
        """Get invoices for patient"""
        
        query = db.query(Invoice).filter(Invoice.patient_id == patient_id)
        
        if status:
            query = query.filter(Invoice.status == BillingStatus(status))
        
        invoices = query.order_by(desc(Invoice.created_at)).limit(limit).all()
        
        return [
            {
                "id": invoice.id,
                "invoice_number": invoice.invoice_number,
                "status": invoice.status.value,
                "total_amount": str(invoice.total_amount),
                "issue_date": invoice.issue_date.isoformat(),
                "due_date": invoice.due_date.isoformat(),
                "paid_date": invoice.paid_date.isoformat() if invoice.paid_date else None,
                "provider_name": f"{invoice.provider.first_name} {invoice.provider.last_name}",
                "appointment_date": invoice.appointment.scheduled_start.isoformat() if invoice.appointment else None,
                "line_items": [
                    {
                        "description": item.description,
                        "quantity": str(item.quantity),
                        "unit_price": str(item.unit_price),
                        "line_total": str(item.line_total)
                    }
                    for item in invoice.line_items
                ]
            }
            for invoice in invoices
        ]
    
    def get_provider_billing_summary(
        self,
        provider_id: int,
        start_date: datetime,
        end_date: datetime,
        db: Session
    ) -> Dict[str, Any]:
        """Get billing summary for provider"""
        
        # Get invoices in date range
        invoices = db.query(Invoice).filter(
            Invoice.provider_id == provider_id,
            Invoice.issue_date >= start_date,
            Invoice.issue_date <= end_date
        ).all()
        
        # Calculate totals
        total_invoiced = sum(invoice.total_amount for invoice in invoices)
        total_paid = sum(invoice.total_amount for invoice in invoices if invoice.status == BillingStatus.PAID)
        total_outstanding = total_invoiced - total_paid
        
        # Count by status
        status_counts = {}
        for status in BillingStatus:
            status_counts[status.value] = len([i for i in invoices if i.status == status])
        
        # Get recent payments
        recent_payments = db.query(Payment).join(Invoice).filter(
            Invoice.provider_id == provider_id,
            Payment.created_at >= start_date,
            Payment.created_at <= end_date,
            Payment.status == PaymentStatus.COMPLETED
        ).order_by(desc(Payment.created_at)).limit(10).all()
        
        return {
            "period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat()
            },
            "summary": {
                "total_invoiced": str(total_invoiced),
                "total_paid": str(total_paid),
                "total_outstanding": str(total_outstanding),
                "invoice_count": len(invoices),
                "status_breakdown": status_counts
            },
            "recent_payments": [
                {
                    "id": payment.id,
                    "amount": str(payment.amount),
                    "payment_date": payment.payment_date.isoformat() if payment.payment_date else None,
                    "patient_name": f"{payment.patient.first_name} {payment.patient.last_name}",
                    "invoice_number": payment.invoice.invoice_number
                }
                for payment in recent_payments
            ]
        }
    
    def create_insurance_claim(
        self,
        appointment_id: int,
        claim_data: Dict[str, Any],
        db: Session
    ) -> Dict[str, Any]:
        """Create insurance claim for appointment"""
        
        appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
        if not appointment:
            raise ValueError("Appointment not found")
        
        # Generate claim number
        claim_number = self._generate_claim_number()
        
        # Create claim
        claim = InsuranceClaim(
            claim_number=claim_number,
            patient_id=appointment.patient_id,
            provider_id=appointment.provider_id,
            appointment_id=appointment_id,
            insurance_company=claim_data.get('insurance_company'),
            policy_number=claim_data.get('policy_number'),
            group_number=claim_data.get('group_number'),
            subscriber_id=claim_data.get('subscriber_id'),
            billed_amount=Decimal(str(claim_data.get('billed_amount', 0))),
            diagnosis_codes=json.dumps(claim_data.get('diagnosis_codes', [])),
            procedure_codes=json.dumps(claim_data.get('procedure_codes', [])),
            submission_date=datetime.utcnow(),
            status="submitted"
        )
        
        db.add(claim)
        db.commit()
        db.refresh(claim)
        
        return {
            "success": True,
            "claim_id": claim.id,
            "claim_number": claim_number,
            "message": "Insurance claim created successfully"
        }
    
    def get_billing_settings(
        self,
        provider_id: int,
        db: Session
    ) -> Optional[Dict[str, Any]]:
        """Get billing settings for provider"""
        
        settings = db.query(BillingSettings).filter(
            BillingSettings.provider_id == provider_id
        ).first()
        
        if not settings:
            return None
        
        return {
            "provider_id": settings.provider_id,
            "default_payment_terms": settings.default_payment_terms,
            "auto_send_invoices": settings.auto_send_invoices,
            "invoice_reminder_days": settings.invoice_reminder_days,
            "late_fee_percentage": str(settings.late_fee_percentage),
            "tax_rate": str(settings.tax_rate),
            "consultation_rate": str(settings.consultation_rate) if settings.consultation_rate else None,
            "therapy_rate": str(settings.therapy_rate) if settings.therapy_rate else None,
            "medication_management_rate": str(settings.medication_management_rate) if settings.medication_management_rate else None,
            "assessment_rate": str(settings.assessment_rate) if settings.assessment_rate else None,
            "has_stripe": bool(settings.stripe_account_id),
            "has_paypal": bool(settings.paypal_client_id)
        }
    
    def update_billing_settings(
        self,
        provider_id: int,
        settings_data: Dict[str, Any],
        db: Session
    ) -> Dict[str, Any]:
        """Update billing settings for provider"""
        
        settings = db.query(BillingSettings).filter(
            BillingSettings.provider_id == provider_id
        ).first()
        
        if not settings:
            # Create new settings
            settings = BillingSettings(provider_id=provider_id)
            db.add(settings)
        
        # Update fields
        if 'default_payment_terms' in settings_data:
            settings.default_payment_terms = settings_data['default_payment_terms']
        if 'auto_send_invoices' in settings_data:
            settings.auto_send_invoices = settings_data['auto_send_invoices']
        if 'invoice_reminder_days' in settings_data:
            settings.invoice_reminder_days = settings_data['invoice_reminder_days']
        if 'late_fee_percentage' in settings_data:
            settings.late_fee_percentage = Decimal(str(settings_data['late_fee_percentage']))
        if 'tax_rate' in settings_data:
            settings.tax_rate = Decimal(str(settings_data['tax_rate']))
        
        # Update service rates
        if 'consultation_rate' in settings_data:
            settings.consultation_rate = Decimal(str(settings_data['consultation_rate'])) if settings_data['consultation_rate'] else None
        if 'therapy_rate' in settings_data:
            settings.therapy_rate = Decimal(str(settings_data['therapy_rate'])) if settings_data['therapy_rate'] else None
        if 'medication_management_rate' in settings_data:
            settings.medication_management_rate = Decimal(str(settings_data['medication_management_rate'])) if settings_data['medication_management_rate'] else None
        if 'assessment_rate' in settings_data:
            settings.assessment_rate = Decimal(str(settings_data['assessment_rate'])) if settings_data['assessment_rate'] else None
        
        settings.updated_at = datetime.utcnow()
        db.commit()
        
        return {
            "success": True,
            "message": "Billing settings updated successfully"
        }
    
    def _generate_invoice_number(self) -> str:
        """Generate unique invoice number"""
        timestamp = datetime.utcnow().strftime("%Y%m%d")
        random_suffix = str(uuid.uuid4())[:8].upper()
        return f"INV-{timestamp}-{random_suffix}"
    
    def _generate_payment_number(self) -> str:
        """Generate unique payment number"""
        timestamp = datetime.utcnow().strftime("%Y%m%d")
        random_suffix = str(uuid.uuid4())[:8].upper()
        return f"PAY-{timestamp}-{random_suffix}"
    
    def _generate_claim_number(self) -> str:
        """Generate unique claim number"""
        timestamp = datetime.utcnow().strftime("%Y%m%d")
        random_suffix = str(uuid.uuid4())[:8].upper()
        return f"CLM-{timestamp}-{random_suffix}"
    
    def _parse_payment_terms(self, terms: str) -> int:
        """Parse payment terms to days"""
        if "Net 30" in terms:
            return 30
        elif "Net 15" in terms:
            return 15
        elif "Net 60" in terms:
            return 60
        else:
            return 30  # Default
    
    def _process_payment_gateway(self, payment_data: Dict[str, Any]) -> bool:
        """Process payment through gateway (simplified implementation)"""
        # In real implementation, integrate with Stripe, PayPal, etc.
        # For now, simulate success based on amount
        amount = float(payment_data.get('amount', 0))
        return amount > 0  # Simulate successful payment for positive amounts


# Global billing service instance
billing_service = BillingService()
