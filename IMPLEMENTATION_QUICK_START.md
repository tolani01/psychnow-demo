# ⚡ QUICK START - Dual Report & Feedback Implementation

**Time:** 3-4 hours | **Priority:** HIGH | **For:** Tomorrow's pilot

---

## 🚀 **QUICK EXECUTION CHECKLIST**

### **Step 1: Database (5 min)**
```bash
cd backend
alembic revision --autogenerate -m "Add feedback system"
alembic upgrade head
```

### **Step 2: Create New Files (45 min)**

**Backend:**
```bash
# Create these files:
backend/app/models/feedback.py
backend/app/schemas/feedback.py
backend/app/services/email_service.py
backend/app/api/v1/feedback.py
```

**Frontend:**
```bash
# Create this file:
psychnow-demo/src/components/AssessmentComplete.tsx
```

### **Step 3: Update Existing Files (60 min)**

**Backend:**
- `backend/app/prompts/system_prompts.py` - Add CLINICIAN_REPORT_GENERATION_PROMPT
- `backend/app/services/report_service.py` - Add generate_clinician_report()
- `backend/app/services/pdf_service.py` - Add generate_clinician_pdf()
- `backend/app/api/v1/intake.py` - Update :finish handler
- `backend/app/core/config.py` - Add email settings
- `backend/.env` - Add SMTP and ADMIN_EMAIL

**Frontend:**
- `psychnow-demo/src/components/DemoLanding.tsx` - Add dual report section
- `psychnow-demo/src/components/PatientIntake.tsx` - Handle both PDFs

### **Step 4: Test (30 min)**
```bash
# Backend
pytest backend/tests/test_feedback.py
pytest backend/tests/test_dual_reports.py

# Frontend
npm run build
npm run preview

# End-to-end
# 1. Complete assessment
# 2. Download both PDFs
# 3. Submit feedback
# 4. Check email
```

### **Step 5: Deploy (30 min)**
```bash
# Backend
git push origin main  # Render auto-deploys

# Frontend
cd psychnow-demo
npm run build
firebase deploy --only hosting
```

---

## 📋 **CRITICAL COMPONENTS**

### **1. Email Service** (MUST IMPLEMENT)
- Sends completion email with 2 PDFs
- Sends feedback email with ratings
- Graceful if SMTP not configured

### **2. Clinician Report Generation** (MUST IMPLEMENT)
- 2-3X more detailed than patient report
- Includes diagnostic reasoning
- Treatment recommendations

### **3. Feedback Form** (MUST IMPLEMENT)
- 9 questions
- Star ratings
- Text areas
- Validation

---

## ⚠️ **GOTCHAS**

1. **SMTP Setup:** Use Gmail app password, not regular password
2. **Report Prompt:** Clinician prompt must prevent hallucinations
3. **PDF Handling:** Both PDFs must be base64 encoded
4. **Session ID:** Pass from intake → complete → feedback
5. **CORS:** Update for production frontend URL

---

## 🎯 **MINIMUM VIABLE DEMO**

If short on time, MUST HAVE:
- ✅ Both PDFs generate (even if clinician report is same for now)
- ✅ Feedback form works
- ✅ Email notifications (even if just logged)

NICE TO HAVE:
- Enhanced clinician report with full detail
- Email with PDF attachments
- Email copy feature

---

## 📞 **QUICK HELP**

**Email not sending?**
→ Check logs, it will still work without email

**PDFs identical?**
→ Check you're using CLINICIAN_REPORT_GENERATION_PROMPT

**Feedback not submitting?**
→ Check session_id is being passed correctly

---

**Full details:** See `DUAL_REPORT_FEEDBACK_IMPLEMENTATION.md`

