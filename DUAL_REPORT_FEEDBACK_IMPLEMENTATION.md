# 🏗️ **PSYCHNOW DEMO - DUAL REPORT & FEEDBACK SYSTEM**
## Technical Implementation Specification v1.0

**Document Version:** 1.0  
**Date:** October 4, 2025  
**Developer:** Senior Backend/Frontend Developer  
**Timeline:** 3-4 hours  
**Priority:** HIGH - Required for clinician pilot tomorrow

---

## 📋 **EXECUTIVE SUMMARY**

**Objective:** Implement dual-report generation (Patient + Clinician versions), in-app feedback collection, and automated email notifications for clinical validation testing.

**Timeline:** 3-4 hours for senior developer  
**Priority:** HIGH - Required for tomorrow's clinician pilot  
**Quality Standard:** Production-ready, HIPAA-consideration compliant

---

## 🎯 **REQUIREMENTS**

### **Functional Requirements**

**FR1: Dual Report Generation**
- Generate two distinct PDF reports from single assessment
- Patient Report: Compassionate, accessible language
- Clinician Report: Full diagnostic reasoning, clinical detail
- Both reports downloadable independently
- Both reports emailed to administrator

**FR2: In-App Feedback Collection**
- Post-assessment feedback form (9 questions)
- Star ratings (1-5) for conversation, patient report, clinician report
- Multiple choice for practice adoption intent
- Open-text fields for qualitative feedback
- Submission validation and error handling

**FR3: Email Notification System**
- Assessment completion notification to admin
- Feedback submission notification to admin
- Attach both PDFs to completion email
- Professional email formatting
- Reliable delivery with error logging

**FR4: Homepage Enhancement**
- Add clear messaging about dual reports
- Explain feedback importance
- Set expectations for testers

### **Non-Functional Requirements**

**NFR1: Performance**
- Report generation: < 10 seconds
- Feedback submission: < 2 seconds
- Email delivery: Asynchronous, non-blocking

**NFR2: Security**
- Sanitize all user inputs
- Rate limiting on feedback submission
- Email validation
- No PII in logs

**NFR3: Reliability**
- Graceful degradation if email fails
- Retry logic for email delivery
- All errors logged for debugging

**NFR4: Maintainability**
- Clear code comments
- Separated concerns
- Reusable components
- TypeScript strict mode

---

## 🏛️ **ARCHITECTURE**

### **System Components**

```
┌─────────────────────────────────────────────────────┐
│                   FRONTEND (React)                   │
├─────────────────────────────────────────────────────┤
│  DemoLanding.tsx (Updated)                          │
│    └─ Add dual-report messaging                     │
│                                                      │
│  PatientIntake.tsx (Minor updates)                  │
│    └─ Navigate to feedback on completion            │
│                                                      │
│  AssessmentComplete.tsx (NEW - Major component)     │
│    ├─ Display both PDF download buttons             │
│    ├─ Feedback form (9 questions)                   │
│    ├─ Email copy request                            │
│    └─ Submission handling                           │
└─────────────────────────────────────────────────────┘
                           │
                           │ HTTPS/JSON
                           ▼
┌─────────────────────────────────────────────────────┐
│                 BACKEND (FastAPI)                    │
├─────────────────────────────────────────────────────┤
│  NEW: /api/v1/feedback/submit                       │
│    ├─ Validate feedback data                        │
│    ├─ Store in database                             │
│    └─ Trigger email notification                    │
│                                                      │
│  UPDATED: /api/v1/intake/chat (finish command)      │
│    ├─ Generate BOTH reports                         │
│    ├─ Store both PDFs                               │
│    ├─ Return both base64 PDFs                       │
│    └─ Trigger completion email                      │
│                                                      │
│  NEW: EmailService                                   │
│    ├─ Assessment completion emails                  │
│    ├─ Feedback submission emails                    │
│    ├─ Attach PDFs                                   │
│    └─ Queue-based delivery (Celery optional)        │
│                                                      │
│  UPDATED: ReportService                              │
│    ├─ generate_patient_report()                     │
│    ├─ generate_clinician_report()                   │
│    └─ Dual PDF generation                           │
└─────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────┐
│                    DATABASE                          │
├─────────────────────────────────────────────────────┤
│  NEW: feedback_submissions                           │
│    ├─ id (UUID)                                     │
│    ├─ session_id (FK)                               │
│    ├─ conversation_rating (1-5)                     │
│    ├─ patient_report_rating (1-5)                   │
│    ├─ clinician_report_rating (1-5)                 │
│    ├─ would_use (enum)                              │
│    ├─ strength (text)                               │
│    ├─ concern (text)                                │
│    ├─ missing_patient (text)                        │
│    ├─ missing_clinician (text)                      │
│    ├─ additional_comments (text)                    │
│    ├─ tester_email (optional)                       │
│    ├─ created_at (timestamp)                        │
│    └─ submitted_at (timestamp)                      │
│                                                      │
│  UPDATED: intake_reports                             │
│    ├─ Add: patient_pdf_path                         │
│    ├─ Add: clinician_pdf_path                       │
│    └─ Add: feedback_submitted (boolean)             │
└─────────────────────────────────────────────────────┘
```

---

## 📝 **DETAILED IMPLEMENTATION PLAN**

### **PHASE 1: Database Schema (15 minutes)**

#### **Task 1.1: Create Feedback Table Migration**

**File:** `backend/alembic/versions/XXXX_add_feedback_system.py`

```python
"""Add feedback system

Revision ID: XXXX
Revises: YYYY
Create Date: 2025-10-04
"""
from alembic import op
import sqlalchemy as sa
import uuid

def upgrade():
    # Create feedback_submissions table
    op.create_table(
        'feedback_submissions',
        sa.Column('id', sa.String(36), primary_key=True, default=lambda: str(uuid.uuid4())),
        sa.Column('session_id', sa.String(36), sa.ForeignKey('intake_sessions.id'), nullable=False),
        sa.Column('conversation_rating', sa.Integer, nullable=False),
        sa.Column('patient_report_rating', sa.Integer, nullable=False),
        sa.Column('clinician_report_rating', sa.Integer, nullable=False),
        sa.Column('would_use', sa.String(50), nullable=False),
        sa.Column('strength', sa.Text, nullable=True),
        sa.Column('concern', sa.Text, nullable=True),
        sa.Column('missing_patient', sa.Text, nullable=True),
        sa.Column('missing_clinician', sa.Text, nullable=True),
        sa.Column('additional_comments', sa.Text, nullable=True),
        sa.Column('tester_email', sa.String(255), nullable=True),
        sa.Column('tester_name', sa.String(255), nullable=True),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('submitted_at', sa.DateTime, server_default=sa.func.now()),
    )
    
    # Add indexes
    op.create_index('ix_feedback_session_id', 'feedback_submissions', ['session_id'])
    op.create_index('ix_feedback_created_at', 'feedback_submissions', ['created_at'])
    
    # Update intake_reports table
    op.add_column('intake_reports', sa.Column('patient_pdf_path', sa.String(500), nullable=True))
    op.add_column('intake_reports', sa.Column('clinician_pdf_path', sa.String(500), nullable=True))
    op.add_column('intake_reports', sa.Column('feedback_submitted', sa.Boolean, default=False))

def downgrade():
    op.drop_table('feedback_submissions')
    op.drop_column('intake_reports', 'patient_pdf_path')
    op.drop_column('intake_reports', 'clinician_pdf_path')
    op.drop_column('intake_reports', 'feedback_submitted')
```

**Action Items:**
- [ ] Create migration file
- [ ] Run `alembic upgrade head`
- [ ] Verify tables created in database
- [ ] Test rollback with `alembic downgrade -1`

---

### **PHASE 2: Backend Models (15 minutes)**

See full model implementations in supplementary files.

**Action Items:**
- [ ] Create `backend/app/models/feedback.py`
- [ ] Update `backend/app/models/intake_session.py` - add feedback relationship
- [ ] Update `backend/app/models/intake_report.py` - add PDF path columns
- [ ] Update `backend/app/db/base.py` - import FeedbackSubmission
- [ ] Test model relationships

---

### **PHASE 3: Backend Schemas (15 minutes)**

**File:** `backend/app/schemas/feedback.py`

Create Pydantic schemas for:
- `FeedbackSubmissionCreate` - Input validation
- `FeedbackSubmissionResponse` - API response
- Validators for ratings (1-5) and would_use enum

**Action Items:**
- [ ] Create feedback schemas
- [ ] Test validation with sample data
- [ ] Verify email validation
- [ ] Test rating range validation

---

### **PHASE 4: Email Service (45 minutes)**

**File:** `backend/app/services/email_service.py`

**Key Methods:**
- `send_email()` - Core email sending with SMTP
- `send_assessment_completion_email()` - With PDF attachments
- `send_feedback_submission_email()` - Formatted feedback
- `_attach_file()` - PDF attachment handler
- `_format_*()` - Email formatting helpers

**Configuration:**
- SMTP settings in `.env`
- Graceful degradation if SMTP not configured
- Email logging for debugging

**Action Items:**
- [ ] Create email_service.py
- [ ] Update config.py with email settings
- [ ] Test email sending (use Gmail app password for testing)
- [ ] Create fallback logging if SMTP not configured
- [ ] Test PDF attachments

---

### **PHASE 5: Dual Report Generation (60 minutes)**

#### **Task 5.1: Update System Prompts**

**File:** `backend/app/prompts/system_prompts.py`

Add new prompt: `CLINICIAN_REPORT_GENERATION_PROMPT`

**Key Differences from Patient Report:**
- Diagnostic reasoning section
- Detailed symptom analysis by cluster
- Comprehensive medication history analysis
- Treatment recommendations
- Mental status exam
- Clinical complexity assessment
- Treatment barriers
- 2-3X more detailed than patient version

#### **Task 5.2: Update Report Service**

**File:** `backend/app/services/report_service.py`

Add methods:
- `generate_clinician_report()` - Uses new prompt
- `generate_dual_reports()` - Generates both at once

#### **Task 5.3: Update PDF Service**

**File:** `backend/app/services/pdf_service.py`

Add method:
- `generate_clinician_pdf()` - Includes all new sections

**Action Items:**
- [ ] Add CLINICIAN_REPORT_GENERATION_PROMPT
- [ ] Implement generate_clinician_report()
- [ ] Implement generate_clinician_pdf()
- [ ] Test both reports generate correctly
- [ ] Verify no hallucinations
- [ ] Compare content depth (clinician should be 2-3x longer)

---

### **PHASE 6: Backend API Endpoints (30 minutes)**

#### **Task 6.1: Create Feedback Router**

**File:** `backend/app/api/v1/feedback.py`

```python
"""
Feedback API Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.feedback import FeedbackSubmissionCreate, FeedbackSubmissionResponse
from app.models.feedback import FeedbackSubmission
from app.models.intake_session import IntakeSession
from app.services.email_service import email_service
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/submit", response_model=FeedbackSubmissionResponse)
async def submit_feedback(
    feedback: FeedbackSubmissionCreate,
    db: Session = Depends(get_db)
):
    """Submit clinician feedback on demo assessment"""
    
    try:
        # Verify session exists
        session = db.query(IntakeSession).filter(
            IntakeSession.session_token == feedback.session_id
        ).first()
        
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found"
            )
        
        # Create feedback record
        db_feedback = FeedbackSubmission(
            session_id=feedback.session_id,
            conversation_rating=feedback.conversation_rating,
            patient_report_rating=feedback.patient_report_rating,
            clinician_report_rating=feedback.clinician_report_rating,
            would_use=feedback.would_use,
            strength=feedback.strength,
            concern=feedback.concern,
            missing_patient=feedback.missing_patient,
            missing_clinician=feedback.missing_clinician,
            additional_comments=feedback.additional_comments,
            tester_email=feedback.tester_email,
            tester_name=feedback.tester_name,
        )
        
        db.add(db_feedback)
        db.commit()
        db.refresh(db_feedback)
        
        # Send email notification
        email_service.send_feedback_submission_email(db_feedback.to_dict())
        
        logger.info(f"Feedback submitted for session {feedback.session_id}")
        
        return FeedbackSubmissionResponse(
            id=db_feedback.id,
            session_id=db_feedback.session_id,
            submitted_at=db_feedback.submitted_at,
            message="Thank you for your valuable feedback!"
        )
        
    except Exception as e:
        logger.error(f"Error submitting feedback: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to submit feedback"
        )
```

#### **Task 6.2: Update Intake Router**

**File:** `backend/app/api/v1/intake.py`

Update the `:finish` command handler to:
- Generate both reports
- Generate both PDFs
- Store both PDF paths
- Return both PDFs in response
- Send completion email with both PDFs

**Action Items:**
- [ ] Create feedback.py router
- [ ] Add to main.py router includes
- [ ] Update intake.py finish handler
- [ ] Test feedback submission endpoint
- [ ] Test dual PDF return
- [ ] Test email notifications

---

### **PHASE 7: Frontend Components (60 minutes)**

#### **Task 7.1: Update DemoLanding Component**

**File:** `psychnow-demo/src/components/DemoLanding.tsx`

Add section after hero:

```tsx
{/* NEW: Dual Report Explanation */}
<div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-2xl border-2 border-blue-200 p-8 mb-8">
  <h3 className="text-2xl font-bold text-gray-900 mb-4 flex items-center">
    <FileText className="w-6 h-6 mr-2 text-blue-600" />
    Two Report Versions for Your Review
  </h3>
  <div className="grid md:grid-cols-2 gap-6">
    <div className="bg-white rounded-lg p-6 border-2 border-blue-200">
      <h4 className="font-bold text-lg text-blue-900 mb-2">📋 Patient Report</h4>
      <p className="text-gray-700 text-sm mb-3">
        Compassionate, accessible summary written for patients. Focuses on:
      </p>
      <ul className="text-sm text-gray-600 space-y-1">
        <li>• Plain language explanations</li>
        <li>• Validation and hope</li>
        <li>• Self-care resources</li>
        <li>• Next steps</li>
      </ul>
    </div>
    
    <div className="bg-white rounded-lg p-6 border-2 border-indigo-200">
      <h4 className="font-bold text-lg text-indigo-900 mb-2">🩺 Clinician Report</h4>
      <p className="text-gray-700 text-sm mb-3">
        Comprehensive clinical assessment for providers. Includes:
      </p>
      <ul className="text-sm text-gray-600 space-y-1">
        <li>• Diagnostic reasoning</li>
        <li>• Treatment recommendations</li>
        <li>• Risk stratification</li>
        <li>• Clinical decision support</li>
      </ul>
    </div>
  </div>
  <p className="text-sm text-gray-600 mt-4 text-center italic">
    By reviewing both reports, you can evaluate patient communication AND clinical utility
  </p>
</div>
```

#### **Task 7.2: Create AssessmentComplete Component**

**File:** `psychnow-demo/src/components/AssessmentComplete.tsx`

**Major component with sections:**
1. Header with success message
2. Dual report download section
3. Feedback form (9 questions)
4. Optional email copy section
5. Submission handling

**Key Features:**
- Star rating component (1-5)
- Radio buttons for would_use
- Text areas for qualitative feedback
- Form validation
- Loading states
- Success/error messages

See full implementation in supplementary code file.

#### **Task 7.3: Update PatientIntake Component**

**File:** `psychnow-demo/src/components/PatientIntake.tsx`

Updates needed:
- Store both PDFs from backend response
- Navigate to AssessmentComplete with both PDFs
- Pass session_id for feedback submission

**Action Items:**
- [ ] Update DemoLanding.tsx
- [ ] Create AssessmentComplete.tsx (full component)
- [ ] Update PatientIntake.tsx navigation
- [ ] Create StarRating helper component
- [ ] Test feedback form validation
- [ ] Test PDF downloads
- [ ] Test form submission

---

### **PHASE 8: Integration & Testing (30 minutes)**

#### **Task 8.1: Backend Integration Tests**

```bash
# Test dual report generation
curl -X POST http://localhost:8000/api/v1/intake/chat \
  -H "Content-Type: application/json" \
  -d '{"session_token": "test123", "prompt": ":finish"}'

# Verify two PDFs returned
# Verify email sent (check logs if SMTP not configured)

# Test feedback submission
curl -X POST http://localhost:8000/api/v1/feedback/submit \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "test123",
    "conversation_rating": 5,
    "patient_report_rating": 4,
    "clinician_report_rating": 5,
    "would_use": "yes_probably",
    "strength": "Great flow"
  }'
```

#### **Task 8.2: Frontend Integration Tests**

1. Complete full assessment
2. Verify both PDFs download
3. Fill out feedback form
4. Submit feedback
5. Verify success message
6. Check email notifications

#### **Task 8.3: End-to-End Test**

- [ ] Complete assessment from start to finish
- [ ] Download both PDFs
- [ ] Verify both PDFs open and are different
- [ ] Clinician report is more detailed
- [ ] Submit feedback with all fields
- [ ] Verify admin receives both emails
- [ ] Test on mobile device
- [ ] Test with different browsers

---

## 📧 **EMAIL NOTIFICATION EXAMPLES**

### **Assessment Completion Email**

```
Subject: ✅ New Demo Assessment Completed - Session abc12345

A clinician has completed the PsychNow demo assessment.

Session ID: abc12345-def67890
Completed: October 4, 2025 at 5:30 PM
Duration: 18 minutes

Attached:
📎 patient-report-abc12345.pdf
📎 clinician-report-abc12345.pdf

Feedback Status: Pending
```

### **Feedback Submission Email**

```
Subject: 💬 Demo Feedback Received - Session abc12345

Ratings:
⭐⭐⭐⭐⭐ Conversation Flow (5/5)
⭐⭐⭐⭐☆ Patient Report (4/5)
⭐⭐⭐⭐⭐ Clinician Report (5/5)

Would Use: Yes, probably

Biggest Strength:
"The conversation flow was very natural and clinically appropriate."

Biggest Concern:
"Would like more detail in trauma history section."
```

---

## 🚀 **DEPLOYMENT CHECKLIST**

### **Backend Deployment**

- [ ] Run database migrations
- [ ] Configure SMTP settings (optional)
- [ ] Set ADMIN_EMAIL in environment
- [ ] Test email sending
- [ ] Deploy to Render/production
- [ ] Verify endpoints accessible

### **Frontend Deployment**

- [ ] Build production bundle
- [ ] Update API URL for production
- [ ] Deploy to Firebase
- [ ] Test on production URL
- [ ] Verify CORS configured

### **Pre-Launch Verification**

- [ ] Complete test assessment end-to-end
- [ ] Download both PDFs - verify different content
- [ ] Submit test feedback
- [ ] Verify admin receives emails
- [ ] Test on mobile
- [ ] Test on different browsers
- [ ] Verify no console errors

---

## 🐛 **TROUBLESHOOTING**

### **Email Not Sending**

**Issue:** SMTP not configured or credentials invalid

**Solution:**
- Check SMTP settings in `.env`
- Verify Gmail app password (not regular password)
- Check email_service logs
- Emails will still be logged even if not sent

### **Both PDFs Identical**

**Issue:** Clinician prompt not being used

**Solution:**
- Verify CLINICIAN_REPORT_GENERATION_PROMPT exists
- Check report_service is calling correct method
- Verify OpenAI response using correct prompt

### **Feedback Form Not Submitting**

**Issue:** Validation errors or API connection

**Solution:**
- Check browser console for errors
- Verify all required fields filled
- Check API endpoint is accessible
- Verify session_id is valid

---

## 📊 **SUCCESS METRICS**

**Technical Success:**
- Both PDFs generate < 10 seconds
- Feedback submits < 2 seconds
- Emails deliver within 1 minute
- Zero critical errors in logs
- Mobile responsive

**Content Success:**
- Clinician report 2-3X longer than patient
- Both reports clinically accurate
- No hallucinated information
- Clear diagnostic reasoning in clinician report

---

## 📝 **CONFIGURATION REFERENCE**

### **Environment Variables**

**Required:**
```
OPENAI_API_KEY=sk-...
SECRET_KEY=...
ADMIN_EMAIL=your-email@domain.com
```

**Optional (Email):**
```
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
FROM_EMAIL=noreply@psychnow.com
```

### **Database Tables**

**New:**
- `feedback_submissions` - Stores clinician feedback

**Updated:**
- `intake_reports` - Added PDF path columns

---

## 🎯 **TIMELINE BREAKDOWN**

| Phase | Task | Time | Dependencies |
|-------|------|------|--------------|
| 1 | Database schema | 15 min | None |
| 2 | Backend models | 15 min | Phase 1 |
| 3 | Backend schemas | 15 min | Phase 2 |
| 4 | Email service | 45 min | Phase 2, 3 |
| 5 | Dual reports | 60 min | Phase 2, 3 |
| 6 | API endpoints | 30 min | Phase 4, 5 |
| 7 | Frontend components | 60 min | Phase 6 |
| 8 | Testing | 30 min | Phase 7 |
| **TOTAL** | | **4 hours** | |

---

## ✅ **FINAL CHECKLIST**

**Before Sending to Clinicians:**

- [ ] All tests passing
- [ ] Both PDFs generate correctly
- [ ] Clinician report more detailed than patient
- [ ] Feedback form works
- [ ] Admin email configured
- [ ] Production deployment complete
- [ ] Mobile testing complete
- [ ] No console errors
- [ ] Demo URL accessible
- [ ] Email template ready for clinicians

---

## 📞 **SUPPORT & REFERENCES**

**Key Files:**
- Backend: `backend/app/services/email_service.py`
- Backend: `backend/app/prompts/system_prompts.py`
- Frontend: `psychnow-demo/src/components/AssessmentComplete.tsx`

**Documentation:**
- FastAPI: https://fastapi.tiangolo.com
- React: https://react.dev
- FPDF: https://pyfpdf.readthedocs.io

**Contact:**
- Technical issues: Check logs first
- Email not sending: Verify SMTP settings
- Report quality: Review system prompts

---

**END OF SPECIFICATION**

*This document provides complete implementation guidance for a senior developer to execute the dual-report and feedback system in 3-4 hours.*

