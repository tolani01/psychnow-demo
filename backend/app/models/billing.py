"""
Billing Models
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Numeric, Boolean, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.db.base import Base


class PaymentStatus(str, enum.Enum):
    """Payment status enumeration"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"
    CANCELLED = "cancelled"


class PaymentMethod(str, enum.Enum):
    """Payment method enumeration"""
    CREDIT_CARD = "credit_card"
    DEBIT_CARD = "debit_card"
    BANK_TRANSFER = "bank_transfer"
    INSURANCE = "insurance"
    CASH = "cash"
    PAYPAL = "paypal"
    STRIPE = "stripe"


class BillingStatus(str, enum.Enum):
    """Billing status enumeration"""
    DRAFT = "draft"
    SENT = "sent"
    PAID = "paid"
    OVERDUE = "overdue"
    CANCELLED = "cancelled"


class Invoice(Base):
    """Invoice model for billing"""
    __tablename__ = "invoices"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Invoice details
    invoice_number = Column(String(50), unique=True, nullable=False, index=True)
    patient_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    provider_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    appointment_id = Column(Integer, ForeignKey("appointments.id"), nullable=True)
    
    # Financial details
    subtotal = Column(Numeric(10, 2), nullable=False)
    tax_amount = Column(Numeric(10, 2), default=0.00)
    discount_amount = Column(Numeric(10, 2), default=0.00)
    total_amount = Column(Numeric(10, 2), nullable=False)
    
    # Status and dates
    status = Column(SQLEnum(BillingStatus), default=BillingStatus.DRAFT)
    issue_date = Column(DateTime, nullable=False)
    due_date = Column(DateTime, nullable=False)
    paid_date = Column(DateTime, nullable=True)
    
    # Additional details
    notes = Column(Text, nullable=True)
    payment_terms = Column(String(100), default="Net 30")
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    patient = relationship("User", foreign_keys=[patient_id], back_populates="patient_invoices")
    provider = relationship("User", foreign_keys=[provider_id], back_populates="provider_invoices")
    appointment = relationship("Appointment", back_populates="invoice")
    line_items = relationship("InvoiceLineItem", back_populates="invoice", cascade="all, delete-orphan")
    payments = relationship("Payment", back_populates="invoice", cascade="all, delete-orphan")


class InvoiceLineItem(Base):
    """Invoice line item model"""
    __tablename__ = "invoice_line_items"
    
    id = Column(Integer, primary_key=True, index=True)
    invoice_id = Column(Integer, ForeignKey("invoices.id"), nullable=False)
    
    # Item details
    description = Column(String(255), nullable=False)
    quantity = Column(Numeric(10, 2), nullable=False, default=1.00)
    unit_price = Column(Numeric(10, 2), nullable=False)
    line_total = Column(Numeric(10, 2), nullable=False)
    
    # Service details
    service_code = Column(String(50), nullable=True)  # CPT codes, etc.
    service_category = Column(String(100), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    invoice = relationship("Invoice", back_populates="line_items")


class Payment(Base):
    """Payment model"""
    __tablename__ = "payments"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Payment details
    payment_number = Column(String(50), unique=True, nullable=False, index=True)
    invoice_id = Column(Integer, ForeignKey("invoices.id"), nullable=False)
    patient_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Financial details
    amount = Column(Numeric(10, 2), nullable=False)
    payment_method = Column(SQLEnum(PaymentMethod), nullable=False)
    status = Column(SQLEnum(PaymentStatus), default=PaymentStatus.PENDING)
    
    # External payment details
    transaction_id = Column(String(255), nullable=True)  # Stripe, PayPal, etc.
    gateway_response = Column(Text, nullable=True)  # JSON response from payment gateway
    
    # Payment dates
    payment_date = Column(DateTime, nullable=True)
    processed_date = Column(DateTime, nullable=True)
    
    # Additional details
    notes = Column(Text, nullable=True)
    refund_amount = Column(Numeric(10, 2), default=0.00)
    refund_date = Column(DateTime, nullable=True)
    refund_reason = Column(String(255), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    invoice = relationship("Invoice", back_populates="payments")
    patient = relationship("User", foreign_keys=[patient_id], back_populates="patient_payments")


class InsuranceClaim(Base):
    """Insurance claim model"""
    __tablename__ = "insurance_claims"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Claim details
    claim_number = Column(String(50), unique=True, nullable=False, index=True)
    patient_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    provider_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    appointment_id = Column(Integer, ForeignKey("appointments.id"), nullable=True)
    invoice_id = Column(Integer, ForeignKey("invoices.id"), nullable=True)
    
    # Insurance details
    insurance_company = Column(String(255), nullable=False)
    policy_number = Column(String(100), nullable=False)
    group_number = Column(String(100), nullable=True)
    subscriber_id = Column(String(100), nullable=False)
    
    # Financial details
    billed_amount = Column(Numeric(10, 2), nullable=False)
    allowed_amount = Column(Numeric(10, 2), nullable=True)
    paid_amount = Column(Numeric(10, 2), nullable=True)
    patient_responsibility = Column(Numeric(10, 2), nullable=True)
    
    # Claim status
    status = Column(String(50), default="submitted")  # submitted, processing, paid, denied, appealed
    submission_date = Column(DateTime, nullable=False)
    response_date = Column(DateTime, nullable=True)
    denial_reason = Column(Text, nullable=True)
    
    # Additional details
    diagnosis_codes = Column(Text, nullable=True)  # JSON array of ICD-10 codes
    procedure_codes = Column(Text, nullable=True)  # JSON array of CPT codes
    notes = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    patient = relationship("User", foreign_keys=[patient_id])
    provider = relationship("User", foreign_keys=[provider_id])
    appointment = relationship("Appointment")
    invoice = relationship("Invoice")


class BillingSettings(Base):
    """Billing settings model"""
    __tablename__ = "billing_settings"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Provider settings
    provider_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    
    # Payment settings
    stripe_account_id = Column(String(255), nullable=True)
    stripe_public_key = Column(String(255), nullable=True)
    stripe_secret_key = Column(String(255), nullable=True)  # Encrypted
    paypal_client_id = Column(String(255), nullable=True)
    paypal_client_secret = Column(String(255), nullable=True)  # Encrypted
    
    # Billing preferences
    default_payment_terms = Column(String(100), default="Net 30")
    auto_send_invoices = Column(Boolean, default=True)
    invoice_reminder_days = Column(String(50), default="7,14,30")  # Comma-separated days
    late_fee_percentage = Column(Numeric(5, 2), default=1.50)  # 1.5%
    tax_rate = Column(Numeric(5, 2), default=0.00)
    
    # Service pricing
    consultation_rate = Column(Numeric(10, 2), nullable=True)
    therapy_rate = Column(Numeric(10, 2), nullable=True)
    medication_management_rate = Column(Numeric(10, 2), nullable=True)
    assessment_rate = Column(Numeric(10, 2), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    provider = relationship("User", back_populates="billing_settings")


class BillingNotification(Base):
    """Billing notification model"""
    __tablename__ = "billing_notifications"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Notification details
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    notification_type = Column(String(50), nullable=False)  # invoice_created, payment_received, payment_failed, etc.
    
    # Related entities
    invoice_id = Column(Integer, ForeignKey("invoices.id"), nullable=True)
    payment_id = Column(Integer, ForeignKey("payments.id"), nullable=True)
    
    # Notification content
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    is_read = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    read_at = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="billing_notifications")
    invoice = relationship("Invoice")
    payment = relationship("Payment")
