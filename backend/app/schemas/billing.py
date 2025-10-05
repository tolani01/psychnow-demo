"""
Billing Pydantic schemas
"""

from datetime import datetime
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from decimal import Decimal


class InvoiceLineItemRequest(BaseModel):
    """Schema for invoice line item request"""
    description: str = Field(..., description="Description of the service")
    quantity: float = Field(default=1.0, ge=0.01, description="Quantity of the service")
    unit_price: float = Field(..., ge=0, description="Price per unit")
    service_code: Optional[str] = Field(None, description="Service code (CPT, etc.)")
    service_category: Optional[str] = Field(None, description="Category of the service")


class InvoiceCreateRequest(BaseModel):
    """Schema for creating an invoice"""
    patient_id: int = Field(..., description="ID of the patient")
    appointment_id: Optional[int] = Field(None, description="ID of the related appointment")
    line_items: List[InvoiceLineItemRequest] = Field(..., description="Line items for the invoice")


class InvoiceLineItemResponse(BaseModel):
    """Schema for invoice line item response"""
    id: int
    description: str
    quantity: str
    unit_price: str
    line_total: str
    service_code: Optional[str] = None
    service_category: Optional[str] = None


class InvoiceResponse(BaseModel):
    """Schema for invoice response"""
    success: bool
    invoice_id: Optional[int] = None
    invoice_number: Optional[str] = None
    total_amount: Optional[str] = None
    due_date: Optional[str] = None
    message: Optional[str] = None


class InvoiceSummary(BaseModel):
    """Schema for invoice summary"""
    id: int
    invoice_number: str
    status: str
    total_amount: str
    issue_date: str
    due_date: str
    paid_date: Optional[str] = None
    provider_name: str
    appointment_date: Optional[str] = None
    line_items: List[InvoiceLineItemResponse]


class InvoiceListResponse(BaseModel):
    """Schema for invoice list response"""
    invoices: List[InvoiceSummary]
    total_count: int


class PaymentRequest(BaseModel):
    """Schema for payment request"""
    amount: Optional[float] = Field(None, description="Payment amount (defaults to invoice total)")
    payment_method: str = Field(..., description="Payment method")
    transaction_id: Optional[str] = Field(None, description="Transaction ID from payment gateway")
    gateway_response: Optional[Dict[str, Any]] = Field(None, description="Gateway response data")
    notes: Optional[str] = Field(None, description="Payment notes")


class PaymentResponse(BaseModel):
    """Schema for payment response"""
    success: bool
    payment_id: Optional[int] = None
    payment_number: Optional[str] = None
    status: Optional[str] = None
    message: str


class BillingSettingsRequest(BaseModel):
    """Schema for billing settings request"""
    default_payment_terms: Optional[str] = Field(None, description="Default payment terms")
    auto_send_invoices: Optional[bool] = Field(None, description="Auto-send invoices")
    invoice_reminder_days: Optional[str] = Field(None, description="Reminder days (comma-separated)")
    late_fee_percentage: Optional[float] = Field(None, ge=0, le=100, description="Late fee percentage")
    tax_rate: Optional[float] = Field(None, ge=0, le=100, description="Tax rate percentage")
    consultation_rate: Optional[float] = Field(None, ge=0, description="Consultation rate")
    therapy_rate: Optional[float] = Field(None, ge=0, description="Therapy session rate")
    medication_management_rate: Optional[float] = Field(None, ge=0, description="Medication management rate")
    assessment_rate: Optional[float] = Field(None, ge=0, description="Assessment rate")


class BillingSettingsResponse(BaseModel):
    """Schema for billing settings response"""
    provider_id: int
    default_payment_terms: str
    auto_send_invoices: bool
    invoice_reminder_days: str
    late_fee_percentage: str
    tax_rate: str
    consultation_rate: Optional[str] = None
    therapy_rate: Optional[str] = None
    medication_management_rate: Optional[str] = None
    assessment_rate: Optional[str] = None
    has_stripe: bool
    has_paypal: bool


class BillingSummaryPeriod(BaseModel):
    """Schema for billing summary period"""
    start_date: str
    end_date: str


class BillingSummaryStats(BaseModel):
    """Schema for billing summary statistics"""
    total_invoiced: str
    total_paid: str
    total_outstanding: str
    invoice_count: int
    status_breakdown: Dict[str, int]


class RecentPayment(BaseModel):
    """Schema for recent payment"""
    id: int
    amount: str
    payment_date: Optional[str] = None
    patient_name: str
    invoice_number: str


class BillingSummaryResponse(BaseModel):
    """Schema for billing summary response"""
    period: BillingSummaryPeriod
    summary: BillingSummaryStats
    recent_payments: List[RecentPayment]


class InsuranceClaimRequest(BaseModel):
    """Schema for insurance claim request"""
    appointment_id: int = Field(..., description="ID of the appointment")
    insurance_company: str = Field(..., description="Insurance company name")
    policy_number: str = Field(..., description="Policy number")
    group_number: Optional[str] = Field(None, description="Group number")
    subscriber_id: str = Field(..., description="Subscriber ID")
    billed_amount: float = Field(..., ge=0, description="Amount billed")
    diagnosis_codes: Optional[List[str]] = Field(None, description="ICD-10 diagnosis codes")
    procedure_codes: Optional[List[str]] = Field(None, description="CPT procedure codes")
    notes: Optional[str] = Field(None, description="Additional notes")


class InsuranceClaimResponse(BaseModel):
    """Schema for insurance claim response"""
    success: bool
    claim_id: Optional[int] = None
    claim_number: Optional[str] = None
    message: str


class PaymentMethod(BaseModel):
    """Schema for payment method"""
    id: str
    name: str
    description: str
    enabled: bool


class PaymentMethodsResponse(BaseModel):
    """Schema for payment methods response"""
    payment_methods: List[PaymentMethod]


class BillingNotification(BaseModel):
    """Schema for billing notification"""
    id: int
    type: str
    title: str
    message: str
    priority: str
    is_read: bool
    created_at: str
    data: Optional[Dict[str, Any]] = None


class BillingNotificationsResponse(BaseModel):
    """Schema for billing notifications response"""
    notifications: List[BillingNotification]
    total_count: int
