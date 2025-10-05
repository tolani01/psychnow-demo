"""
Billing API endpoints
"""

from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.billing import (
    InvoiceCreateRequest,
    InvoiceResponse,
    InvoiceListResponse,
    PaymentRequest,
    PaymentResponse,
    BillingSettingsRequest,
    BillingSettingsResponse,
    BillingSummaryResponse,
    InsuranceClaimRequest,
    InsuranceClaimResponse
)
from app.services.billing_service import billing_service
from app.core.rate_limit import limiter

router = APIRouter()


@router.post("/invoices", response_model=InvoiceResponse)
@limiter.limit("10/minute")
async def create_invoice(
    request: Request,
    invoice_request: InvoiceCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new invoice"""
    
    if current_user.role not in ["provider", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Provider or admin role required."
        )
    
    try:
        result = billing_service.create_invoice(
            patient_id=invoice_request.patient_id,
            provider_id=current_user.id,
            appointment_id=invoice_request.appointment_id,
            line_items=invoice_request.line_items,
            db=db
        )
        
        return InvoiceResponse(**result)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create invoice: {str(e)}"
        )


@router.get("/invoices", response_model=InvoiceListResponse)
async def get_invoices(
    status: Optional[str] = Query(None, description="Filter by invoice status"),
    limit: int = Query(50, ge=1, le=100, description="Number of invoices to return"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get invoices for current user"""
    
    try:
        if current_user.role == "patient":
            invoices = billing_service.get_patient_invoices(
                patient_id=current_user.id,
                status=status,
                limit=limit,
                db=db
            )
        elif current_user.role == "provider":
            # Get invoices created by provider
            invoices = billing_service.get_patient_invoices(
                patient_id=current_user.id,  # This should be modified to get provider's invoices
                status=status,
                limit=limit,
                db=db
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied. Patient or provider role required."
            )
        
        return InvoiceListResponse(
            invoices=invoices,
            total_count=len(invoices)
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get invoices: {str(e)}"
        )


@router.post("/invoices/{invoice_id}/send", response_model=InvoiceResponse)
@limiter.limit("10/minute")
async def send_invoice(
    request: Request,
    invoice_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Send invoice to patient"""
    
    if current_user.role not in ["provider", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Provider or admin role required."
        )
    
    try:
        result = billing_service.send_invoice(
            invoice_id=invoice_id,
            db=db
        )
        
        return InvoiceResponse(**result)
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send invoice: {str(e)}"
        )


@router.post("/invoices/{invoice_id}/payments", response_model=PaymentResponse)
@limiter.limit("10/minute")
async def process_payment(
    request: Request,
    invoice_id: int,
    payment_request: PaymentRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Process payment for invoice"""
    
    if current_user.role != "patient":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Patient role required."
        )
    
    try:
        result = billing_service.process_payment(
            invoice_id=invoice_id,
            payment_data=payment_request.dict(),
            db=db
        )
        
        return PaymentResponse(**result)
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process payment: {str(e)}"
        )


@router.get("/billing-summary", response_model=BillingSummaryResponse)
async def get_billing_summary(
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get billing summary for provider"""
    
    if current_user.role != "provider":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Provider role required."
        )
    
    try:
        # Default to last 30 days if no dates provided
        if not start_date:
            start_date = (datetime.utcnow() - timedelta(days=30)).strftime("%Y-%m-%d")
        if not end_date:
            end_date = datetime.utcnow().strftime("%Y-%m-%d")
        
        start_dt = datetime.fromisoformat(start_date)
        end_dt = datetime.fromisoformat(end_date)
        
        summary = billing_service.get_provider_billing_summary(
            provider_id=current_user.id,
            start_date=start_dt,
            end_date=end_dt,
            db=db
        )
        
        return BillingSummaryResponse(**summary)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get billing summary: {str(e)}"
        )


@router.get("/settings", response_model=BillingSettingsResponse)
async def get_billing_settings(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get billing settings for provider"""
    
    if current_user.role != "provider":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Provider role required."
        )
    
    try:
        settings = billing_service.get_billing_settings(
            provider_id=current_user.id,
            db=db
        )
        
        if not settings:
            # Return default settings
            settings = {
                "provider_id": current_user.id,
                "default_payment_terms": "Net 30",
                "auto_send_invoices": True,
                "invoice_reminder_days": "7,14,30",
                "late_fee_percentage": "1.50",
                "tax_rate": "0.00",
                "has_stripe": False,
                "has_paypal": False
            }
        
        return BillingSettingsResponse(**settings)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get billing settings: {str(e)}"
        )


@router.put("/settings", response_model=BillingSettingsResponse)
@limiter.limit("10/minute")
async def update_billing_settings(
    request: Request,
    settings_request: BillingSettingsRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update billing settings for provider"""
    
    if current_user.role != "provider":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Provider role required."
        )
    
    try:
        result = billing_service.update_billing_settings(
            provider_id=current_user.id,
            settings_data=settings_request.dict(),
            db=db
        )
        
        # Get updated settings
        updated_settings = billing_service.get_billing_settings(
            provider_id=current_user.id,
            db=db
        )
        
        return BillingSettingsResponse(**updated_settings)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update billing settings: {str(e)}"
        )


@router.post("/insurance-claims", response_model=InsuranceClaimResponse)
@limiter.limit("10/minute")
async def create_insurance_claim(
    request: Request,
    claim_request: InsuranceClaimRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create insurance claim for appointment"""
    
    if current_user.role not in ["provider", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Provider or admin role required."
        )
    
    try:
        result = billing_service.create_insurance_claim(
            appointment_id=claim_request.appointment_id,
            claim_data=claim_request.dict(),
            db=db
        )
        
        return InsuranceClaimResponse(**result)
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create insurance claim: {str(e)}"
        )


@router.get("/payment-methods")
async def get_payment_methods(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get available payment methods"""
    
    return {
        "payment_methods": [
            {
                "id": "credit_card",
                "name": "Credit Card",
                "description": "Visa, MasterCard, American Express",
                "enabled": True
            },
            {
                "id": "debit_card",
                "name": "Debit Card",
                "description": "Bank debit card",
                "enabled": True
            },
            {
                "id": "bank_transfer",
                "name": "Bank Transfer",
                "description": "Direct bank transfer",
                "enabled": True
            },
            {
                "id": "paypal",
                "name": "PayPal",
                "description": "PayPal account",
                "enabled": True
            },
            {
                "id": "insurance",
                "name": "Insurance",
                "description": "Insurance claim",
                "enabled": True
            }
        ]
    }


@router.get("/billing-notifications")
async def get_billing_notifications(
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get billing notifications for user"""
    
    try:
        notifications = billing_service.notification_service.get_user_notifications(
            user_id=current_user.id,
            limit=limit,
            notification_types=["invoice_created", "payment_received", "payment_failed", "invoice_sent"],
            db=db
        )
        
        return {
            "notifications": [
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
            ],
            "total_count": len(notifications)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get billing notifications: {str(e)}"
        )
