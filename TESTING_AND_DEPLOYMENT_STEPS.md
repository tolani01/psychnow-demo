# 🚀 TESTING & DEPLOYMENT - Dual Report System

**Implementation Status:** ✅ **COMPLETE**  
**Next Step:** Database migration, testing, and deployment

---

## ✅ **WHAT WAS IMPLEMENTED**

### **Backend (Complete)**
- ✅ FeedbackSubmission model (`backend/app/models/feedback.py`)
- ✅ Feedback schemas (`backend/app/schemas/feedback.py`)
- ✅ EmailService with HTML templates (`backend/app/services/email_service.py`)
- ✅ Clinician report generation prompt (in `system_prompts.py`)
- ✅ Dual report generation in ReportService
- ✅ Clinician PDF generation in PDFService
- ✅ Feedback API endpoint (`backend/app/api/v1/feedback.py`)
- ✅ Updated intake endpoint to return both PDFs and send emails
- ✅ Updated config for email settings
- ✅ Updated IntakeReport model with PDF path columns
- ✅ Updated IntakeSession model with feedback relationship

### **Frontend (Complete)**
- ✅ Updated DemoLanding with dual report explanation
- ✅ Created AssessmentComplete component with feedback form
- ✅ Updated PatientIntake to handle both PDFs
- ✅ Star rating component in feedback form
- ✅ Auto-navigation to feedback after assessment

---

## 🔧 **STEP 1: Database Migration** (5 minutes)

**You need to do this now:**

```powershell
cd "C:\Users\gbtol\PsychNow\backend"
.\venv\Scripts\Activate.ps1

# Create migration
alembic revision --autogenerate -m "Add dual reports and feedback system"

# Review the migration file in: backend/alembic/versions/XXXX_add_dual_reports_and_feedback_system.py
# Make sure it includes:
# - feedback_submissions table
# - Updates to intake_reports (patient_pdf_path, clinician_pdf_path, clinician_report_data, feedback_submitted)

# Apply migration
alembic upgrade head
```

**Verify it worked:**
```powershell
python
>>> from app.models.feedback import FeedbackSubmission
>>> from app.models.intake_report import IntakeReport
>>> print("Models imported successfully!")
>>> exit()
```

---

## 🧪 **STEP 2: Local Testing** (30 minutes)

### **2A: Test Backend**

**In backend terminal:**
```powershell
cd "C:\Users\gbtol\PsychNow\backend"
.\venv\Scripts\Activate.ps1
python main.py
```

**Verify endpoints exist:**
- Visit: http://127.0.0.1:8000/api/docs
- Look for:
  - `/api/v1/feedback/submit` - Should be there!
  - `/api/v1/feedback/stats` - Should be there!
  - `/api/v1/intake/chat` - Should have updated response schema

### **2B: Test Frontend**

**In demo terminal:**
```powershell
cd "C:\Users\gbtol\PsychNow\psychnow-demo"
npm run dev
```

**Complete E2E Test:**
1. ✅ Visit http://localhost:3001 (or 3002)
2. ✅ Click "Start Demo Assessment"
3. ✅ Complete conversation (or type `:finish` to skip)
4. ✅ Watch for "Two report versions have been generated"
5. ✅ Auto-navigate to feedback page
6. ✅ See both download buttons (Patient + Clinician)
7. ✅ Download both PDFs
8. ✅ Open both PDFs - verify they're different!
9. ✅ **Clinician PDF should be 2-3X longer**
10. ✅ Fill out feedback form
11. ✅ Submit feedback
12. ✅ See success message

### **2C: Verify Emails** (If SMTP Configured)

**Check backend terminal for email logs:**
- After completing assessment: Should see "Assessment completion email sent"
- After submitting feedback: Should see "Feedback email sent"

**If SMTP not configured:**
- Emails will be logged only
- This is fine for local testing
- Will configure for production deployment

---

## 📧 **STEP 3: Configure Email** (Optional for tomorrow)

### **Option A: Use Gmail** (Recommended for testing)

**Get Gmail App Password:**
1. Go to Google Account settings
2. Security → 2-Step Verification
3. App passwords → Generate
4. Copy the 16-character password

**Update backend/.env:**
```
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=xxxx-xxxx-xxxx-xxxx
ADMIN_EMAIL=your-email@gmail.com
FROM_EMAIL=noreply@psychnow.com
```

**Restart backend** and test again!

### **Option B: Skip Email for Now**

If short on time:
- Leave SMTP settings blank
- Emails will be logged in backend console
- You can manually check for demo completions
- Still fully functional for clinician testing!

---

## 🚢 **STEP 4: Deploy to Production** (45-60 minutes)

### **4A: Update Environment for Render**

**In Render dashboard, add these environment variables:**

```
ADMIN_EMAIL=your-email@domain.com
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-gmail-app-password
FROM_EMAIL=noreply@psychnow.com
```

### **4B: Deploy Backend**

```powershell
cd "C:\Users\gbtol\PsychNow"
git add backend/
git commit -m "Add dual report generation and feedback system"
git push origin main
```

**Render will auto-deploy!** Watch the logs in Render dashboard.

**After deployment, run migration on Render:**
- Render Dashboard → Your Service → Shell
- Run: `alembic upgrade head`

### **4C: Deploy Frontend**

**Create production .env:**
```powershell
cd "C:\Users\gbtol\PsychNow\psychnow-demo"
echo VITE_API_BASE_URL=https://your-backend.onrender.com > .env.production
```

**Build and deploy:**
```powershell
npm run build
firebase deploy --only hosting
```

### **4D: Update CORS**

In Render dashboard, update `ALLOWED_ORIGINS`:
```
https://your-project.web.app,https://your-project.firebaseapp.com
```

---

## ✅ **STEP 5: Production Testing** (15 minutes)

Visit your live demo URL and test:

1. ✅ Complete full assessment
2. ✅ Download both PDFs
3. ✅ Verify PDFs are different
4. ✅ Clinician PDF is more detailed
5. ✅ Submit feedback
6. ✅ Check your email for notifications
7. ✅ Test on mobile device

---

## 📧 **WHAT YOU'LL RECEIVE BY EMAIL**

### **After Each Assessment:**
```
Subject: ✅ New Demo Assessment Completed - Session abc12345

Session ID: abc12345
Completed: October 4, 2025 at 6:30 PM
Duration: 17 minutes

Attached:
📎 patient-report-abc12345.pdf
📎 clinician-report-abc12345.pdf

Feedback Status: Pending
```

### **After Each Feedback:**
```
Subject: 💬 Demo Feedback Received - Session abc12345

Ratings:
⭐⭐⭐⭐⭐ Conversation Flow (5/5)
⭐⭐⭐⭐☆ Patient Report (4/5)
⭐⭐⭐⭐⭐ Clinician Report (5/5)

Would Use: Yes, probably

Biggest Strength:
"Very natural conversation flow, clinically appropriate questions"

Biggest Concern:
"Would like more detail on trauma history"
```

---

## 🐛 **TROUBLESHOOTING**

### **Migration Fails**

```powershell
# If migration has issues, downgrade and try again
alembic downgrade -1
alembic upgrade head
```

### **Emails Not Sending**

**Check backend logs for:**
- "SMTP credentials not configured" → Add SMTP settings to .env
- "Failed to send email" → Check Gmail app password is correct
- Emails will be logged even if not sent

### **Both PDFs Identical**

**Issue:** Clinician report generation not working

**Fix:**
- Check backend logs for errors
- Verify `CLINICIAN_REPORT_GENERATION_PROMPT` exists in system_prompts.py
- Test report generation in isolation

### **Feedback Form Not Submitting**

**Check:**
- Browser console for errors
- All required fields filled (ratings and would_use)
- Backend `/api/v1/feedback/submit` endpoint accessible
- Session ID is being passed correctly

---

## 📋 **PRE-LAUNCH CHECKLIST**

**Before sending to 10 clinicians tomorrow:**

- [ ] Database migration applied (locally and production)
- [ ] Backend deployed to Render
- [ ] Frontend deployed to Firebase
- [ ] Complete test assessment end-to-end
- [ ] Download both PDFs - verify different content
- [ ] Clinician PDF is 2-3X more detailed
- [ ] Submit test feedback
- [ ] Receive email notifications (or verify logs)
- [ ] Test on mobile device
- [ ] No console errors
- [ ] CORS configured for production URLs
- [ ] Email template ready with your demo URL

---

## 🎯 **WHAT CLINICIANS WILL EXPERIENCE**

1. **Landing Page**
   - Clear explanation of dual reports
   - Understanding they'll provide feedback
   - Click "Start Demo Assessment"

2. **Assessment** (15-20 min)
   - Natural AI conversation
   - Validated screening tools
   - Complete psychiatric intake

3. **Completion**
   - Auto-redirect to feedback page
   - See both report download buttons
   - Download and review both PDFs

4. **Feedback** (2 min)
   - Rate conversation (1-5 stars)
   - Rate patient report (1-5 stars)
   - Rate clinician report (1-5 stars)
   - Indicate if they'd use it
   - Provide qualitative feedback
   - Optional: Add their email/name

5. **Confirmation**
   - Thank you message
   - Return to home

**Meanwhile, YOU receive:**
- ✉️ Email when assessment completes (with both PDFs)
- ✉️ Email when feedback is submitted (with all ratings and comments)

---

## 💡 **QUICK TEST SCRIPT**

**Run this end-to-end test:**

```
DEMO TEST CHECKLIST

□ Open demo URL
□ Read landing page - dual reports explained?
□ Start assessment
□ Answer a few questions (or type :finish)
□ See "Two report versions generated" message
□ Auto-redirect to feedback page
□ Click "Download Patient Report"
□ PDF downloads and opens? (patient version)
□ Click "Download Clinician Report"  
□ PDF downloads and opens? (clinician version)
□ Compare PDFs - clinician more detailed?
□ Fill out feedback: Rate 5, 4, 5 stars
□ Select "Yes, probably" for would use
□ Enter strength: "Great flow"
□ Enter concern: "Test concern"
□ Click "Submit Feedback"
□ See success message?
□ Check your email - 2 emails received?
□ Test on phone
```

**If all checks pass → READY TO SEND TO CLINICIANS! 🚀**

---

## 📞 **NEED HELP?**

### **Database Issues**
```powershell
# Check current migration
alembic current

# Check pending migrations
alembic heads

# If stuck, recreate DB (development only!)
# rm psychnow.db
# alembic upgrade head
```

### **Email Issues**
- Gmail app password instructions: https://support.google.com/accounts/answer/185833
- Test with simple Python script first
- Check spam folder
- Verify email in backend terminal logs

### **PDF Issues**
- Check backend logs for generation errors
- Verify OpenAI API has credits
- Test patient report generation first
- Then test clinician report

---

## 🎊 **YOU'RE READY!**

**Implementation complete!** Here's what to do:

**TODAY:**
1. Run database migration (5 min)
2. Test locally end-to-end (30 min)
3. Configure email settings (10 min)
4. Deploy to production (45 min)
5. Test production (15 min)

**TOMORROW MORNING:**
1. Send emails to 10 clinicians (8-9 AM)
2. Monitor inbox for completion/feedback emails
3. Track in spreadsheet

**NEXT WEEK:**
1. Collect all feedback
2. Analyze results
3. Plan improvements

---

## 📧 **SEND THIS EMAIL TOMORROW**

Subject: PsychNow Demo - Your Clinical Expertise Needed (20 min)

Dear [Clinician Name],

I'm reaching out to share a demo of PsychNow, an AI-guided psychiatric assessment platform, and would be grateful for your clinical feedback.

🔗 **Demo Link:** [YOUR-URL.web.app]  
⏱️ **Time:** 15-20 minutes  

**What You'll Do:**
1. Complete the AI-guided assessment as if you were a patient
2. Review TWO report versions:
   - Patient Report (compassionate, accessible)
   - Clinician Report (comprehensive, clinical detail)
3. Provide quick feedback via built-in form (2 minutes)

**What I Need:**
- Is the conversation clinically appropriate?
- Are the reports useful?
- Would you use this in your practice?
- What's missing?

The feedback form appears right after the assessment - super quick!

**Your input will directly shape whether this moves forward.**

Thank you for considering!

[Your Name]  
[Your Contact Info]

---

**Ready to go live! 🎉**

