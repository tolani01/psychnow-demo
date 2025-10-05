"""
Consent Endpoints
User consent management for HIPAA compliance
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from app.db.session import get_db
from app.schemas.consent import ConsentCreate, ConsentResponse, ConsentStatus
from app.models.consent import Consent
from app.models.audit_log import AuditLog
from app.core.deps import get_current_user
from app.models.user import User

router = APIRouter()


@router.post("/accept", response_model=ConsentResponse, status_code=status.HTTP_201_CREATED)
async def accept_consent(
    consent_data: ConsentCreate,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Record user consent acceptance
    
    Required consents: hipaa, telehealth
    Optional: financial
    """
    # Check if already consented (prevent duplicates)
    existing = db.query(Consent).filter(
        Consent.user_id == current_user.id,
        Consent.consent_type == consent_data.consent_type,
        Consent.revoked_at == None
    ).first()
    
    if existing:
        return existing  # Already consented
    
    # Create consent record
    consent = Consent(
        user_id=current_user.id,
        consent_type=consent_data.consent_type,
        version=consent_data.version,
        content_hash=consent_data.content_hash,
        accepted_at=datetime.utcnow(),
        ip_address=consent_data.ip_address or request.client.host,
        user_agent=consent_data.user_agent or request.headers.get("user-agent")
    )
    
    db.add(consent)
    
    # Audit log
    audit = AuditLog(
        event_type="consent_accepted",
        action="create",
        user_id=current_user.id,
        resource_type="consent",
        resource_id=consent.id,
        ip_address=request.client.host,
        event_metadata={
            "consent_type": consent_data.consent_type,
            "version": consent_data.version
        },
        timestamp=datetime.utcnow()
    )
    db.add(audit)
    
    db.commit()
    db.refresh(consent)
    
    return consent


@router.get("/status", response_model=ConsentStatus)
async def get_consent_status(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get user's consent status
    
    Returns which consents have been accepted
    """
    consents = db.query(Consent).filter(
        Consent.user_id == current_user.id,
        Consent.revoked_at == None
    ).all()
    
    consent_types = {c.consent_type for c in consents}
    
    has_hipaa = "hipaa" in consent_types
    has_telehealth = "telehealth" in consent_types
    has_financial = "financial" in consent_types
    
    # Required consents: hipaa + telehealth
    all_required = has_hipaa and has_telehealth
    
    return ConsentStatus(
        hipaa=has_hipaa,
        telehealth=has_telehealth,
        financial=has_financial,
        all_required_consents_given=all_required
    )


@router.get("/list", response_model=List[ConsentResponse])
async def list_consents(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List all consents for current user
    """
    consents = db.query(Consent).filter(
        Consent.user_id == current_user.id
    ).order_by(Consent.accepted_at.desc()).all()
    
    return consents


@router.post("/revoke/{consent_type}")
async def revoke_consent(
    consent_type: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Revoke a specific consent
    
    Note: Revoking HIPAA or telehealth will prevent further care
    """
    consent = db.query(Consent).filter(
        Consent.user_id == current_user.id,
        Consent.consent_type == consent_type,
        Consent.revoked_at == None
    ).first()
    
    if not consent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No active {consent_type} consent found"
        )
    
    # Mark as revoked
    consent.revoked_at = datetime.utcnow()
    
    # Audit log
    audit = AuditLog(
        event_type="consent_revoked",
        action="update",
        user_id=current_user.id,
        resource_type="consent",
        resource_id=consent.id,
        event_metadata={"consent_type": consent_type},
        timestamp=datetime.utcnow()
    )
    db.add(audit)
    
    db.commit()
    
    return {"message": f"{consent_type} consent revoked", "revoked_at": consent.revoked_at}

