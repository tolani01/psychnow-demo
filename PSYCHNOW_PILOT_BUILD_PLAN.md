# 🚀 PsychNow Pilot Build Plan - FINAL

**Version**: 1.0 Final  
**Date**: September 30, 2025  
**Status**: Ready to Build  
**Timeline**: 4 weeks (28 days) - Full-time development

---

## 📊 EXECUTIVE SUMMARY

**Goal**: Build a production-ready mental health intake system for pilot testing with 10 patients and 10 providers.

**Core Value Proposition**: AI-guided comprehensive psychiatric assessment that generates provider-ready clinical reports using all major mental health screening instruments.

---

## 🎯 CONFIRMED DECISIONS

### **Branding**
- **Platform Name**: PsychNow
- **Tagline**: "AI-guided psychiatric assessment, human-centered care"
- **Tone**: Balanced (professional but approachable)
- **AI Assistant**: Ava (conversational intake guide)

### **Technical Stack**
- **Backend**: FastAPI (Python 3.11+)
- **Frontend**: React 18 + TypeScript + Vite
- **Database**: PostgreSQL (Docker for local, Render for production)
- **Auth**: FastAPI Users with JWT tokens
- **LLM**: OpenAI API (gpt-4o-mini initially, gpt-4o if needed)
- **Deployment**: Render (backend) + Vercel (frontend)
- **State Management**: TanStack Query (React Query)

### **Scope Decisions**
- ✅ **All 30 mental health screeners** (comprehensive assessment) - COMPLETED
- ✅ **Provider registration**: Self-register with invite code + admin approval - COMPLETED
- ✅ **Report sharing**: Admin manually assigns reports to providers (Pilot) - COMPLETED
- ✅ **Email**: Skip for pilot (manual notifications) - COMPLETED
- ✅ **Authentication**: Email/password with JWT - COMPLETED
- ✅ **Database**: PostgreSQL from day 1 - COMPLETED
- ✅ **Scheduling**: Basic appointment scheduling - COMPLETED
- ✅ **Payments**: Invoice generation and payment processing - COMPLETED
- ✅ **Insurance/Claims**: Basic insurance claim processing - COMPLETED
- ✅ **HIPAA infrastructure**: Audit logging and compliance features - COMPLETED

---

## 🧠 CLINICAL SCREENING INSTRUMENTS (All 30)

### **Category 1: Depression**
1. **PHQ-9** (Patient Health Questionnaire) - 9 items, 0-27 scale
2. **PHQ-2** (Quick depression screen) - 2 items, 0-6 scale

### **Category 2: Anxiety**
3. **GAD-7** (Generalized Anxiety Disorder) - 7 items, 0-21 scale
4. **GAD-2** (Quick anxiety screen) - 2 items, 0-6 scale
5. **SPIN** (Social Phobia Inventory) - 17 items, 0-68 scale
6. **PDSS** (Panic Disorder Severity Scale) - 7 items, 0-28 scale

### **Category 3: ADHD**
7. **ASRS v1.1** (Adult ADHD Self-Report Scale) - 18 items (Part A: 6, Part B: 12)

### **Category 4: PTSD/Trauma**
8. **PCL-5** (PTSD Checklist for DSM-5) - 20 items, 0-80 scale
9. **PC-PTSD-5** (Primary Care PTSD Screen) - 5 items, yes/no

### **Category 5: Bipolar/Mania**
10. **MDQ** (Mood Disorder Questionnaire) - 13 items + 2 questions
11. **HCL-32** (Hypomania Checklist) - 32 items

### **Category 6: Substance Use**
12. **AUDIT** (Alcohol Use Disorders Identification Test) - 10 items, 0-40 scale
13. **AUDIT-C** (Quick alcohol screen) - 3 items, 0-12 scale
14. **DAST-10** (Drug Abuse Screening Test) - 10 items, 0-10 scale
15. **CAGE-AID** (Substance abuse) - 4 items, yes/no

### **Category 7: Suicide Risk (CRITICAL)**
16. **C-SSRS** (Columbia-Suicide Severity Rating Scale) - Ideation + Behavior + Risk factors
17. **ASQ** (Ask Suicide-Screening Questions) - 4 items, yes/no

### **Category 8: Sleep Disorders**
18. **ISI** (Insomnia Severity Index) - 7 items, 0-28 scale
19. **ESS** (Epworth Sleepiness Scale) - 8 items, 0-24 scale

### **Category 9: Eating Disorders**
20. **SCOFF** (Eating Disorder Screen) - 5 items, yes/no
21. **EDE-QS** (Eating Disorder Examination Short) - 12 items

### **Category 10: OCD**
22. **OCI-R** (Obsessive-Compulsive Inventory-Revised) - 18 items, 0-72 scale

### **Category 11: General Mental Health**
23. **K6** (Kessler Psychological Distress Scale) - 6 items, 0-24 scale
24. **WSAS** (Work and Social Adjustment Scale) - 5 items, 0-40 scale

### **Category 12: Personality**
25. **MSI-BPD** (McLean Screening Instrument for BPD) - 10 items, yes/no
26. **PID-5-BF** (Personality Inventory for DSM-5 Brief) - 25 items

### **Category 13: Psychosis Risk**
27. **PRIME** (Prodromal Questionnaire - Brief) - 21 items

### **Category 14: Additional**
28. **LSAS** (Liebowitz Social Anxiety Scale) - 24 items
29. **FSS-Brief** (Fear Survey Schedule) - Common phobias subset
30. **BDI-II** (Beck Depression Inventory) - 21 items, 0-63 scale (optional alternative to PHQ-9)

---

## 🎭 PILOT TEST SCENARIOS

### **Scenario 1: Moderate Depression with Insomnia**
**Profile**:
- Age/Gender: 35-year-old Female
- Chief Complaint: "I've been feeling really down and having trouble sleeping for the past 2 months"

**Clinical Presentation**:
- Low mood, anhedonia (loss of interest in activities)
- Initial insomnia (difficulty falling asleep)
- Fatigue, difficulty concentrating
- Appetite changes (decreased)
- No suicidal ideation
- Mild anxiety about work performance
- No substance use
- First episode, no prior psychiatric history

**Expected Screeners Triggered**:
- PHQ-2 → positive → PHQ-9
- GAD-2 → positive → GAD-7
- C-SSRS (always for depression)
- ISI (insomnia severity)
- WSAS (functional impairment)

**Expected Scores**:
- PHQ-9: 14 (Moderately severe depression)
- GAD-7: 8 (Mild anxiety)
- C-SSRS: Low risk (no ideation)
- ISI: 16 (Moderate insomnia)
- WSAS: 18 (Moderate impairment)

**Expected Recommendations**:
- Psychiatric evaluation within 1-2 weeks
- Consider SSRI (e.g., sertraline, escitalopram)
- Sleep hygiene counseling
- Cognitive Behavioral Therapy for Insomnia (CBT-I)
- Follow-up in 2-4 weeks
- Consider therapy (CBT, IPT)

---

### **Scenario 2: ADHD with Comorbid Anxiety**
**Profile**:
- Age/Gender: 28-year-old Male
- Chief Complaint: "I can't focus at work, constantly losing things, and feeling overwhelmed"

**Clinical Presentation**:
- Lifelong difficulty with attention and organization
- Procrastination, forgetfulness
- Restlessness, difficulty sitting still
- Started new job 6 months ago (increased demands)
- Performance anxiety, worry about being fired
- No mood symptoms (not depressed)
- Occasional alcohol use (social, not problematic)
- Symptoms present since childhood but worsening

**Expected Screeners Triggered**:
- PHQ-2 → negative (no depression)
- GAD-2 → positive → GAD-7
- ASRS v1.1 (full 18 items - attention symptoms obvious)
- AUDIT-C (screen substance use)
- WSAS (work impairment)

**Expected Scores**:
- PHQ-9: 4 (Minimal depression - may not administer)
- GAD-7: 11 (Moderate anxiety)
- ASRS Part A: 5/6 positive (highly suggestive of ADHD)
- ASRS Part B: 9/12 positive
- AUDIT-C: 3 (Low risk)
- WSAS: 22 (Moderate-severe work impairment)

**Expected Recommendations**:
- ADHD evaluation with psychiatrist or specialist
- Consider neuropsychological testing if available
- Trial of stimulant medication (methylphenidate, amphetamine) if ADHD confirmed
- Cognitive Behavioral Therapy for ADHD
- Organizational skills coaching
- Workplace accommodations discussion
- Manage anxiety symptoms (may improve with ADHD treatment)

---

### **Scenario 3: PTSD with Substance Use and High Suicide Risk**
**Profile**:
- Age/Gender: 42-year-old Male, Military Veteran
- Chief Complaint: "I've been having nightmares and flashbacks since I got back from deployment. I can't take it anymore."

**Clinical Presentation**:
- Combat trauma (IED explosion, witnessed casualties) 3 years ago
- Recurrent nightmares, intrusive memories
- Avoidance of reminders (crowds, loud noises)
- Hypervigilance, exaggerated startle response
- Emotional numbing, detachment from family
- Severe depression, hopelessness
- Suicidal ideation with plan (firearm access)
- Heavy alcohol use (self-medication)
- Sleep disturbance (nightmares + insomnia)
- Social isolation

**Expected Screeners Triggered**:
- PHQ-2 → positive → PHQ-9
- GAD-2 → positive → GAD-7
- PC-PTSD-5 → positive → PCL-5 (full PTSD assessment)
- C-SSRS (CRITICAL - high risk)
- AUDIT (alcohol use detailed)
- ISI (sleep)
- WSAS (functional impairment)

**Expected Scores**:
- PHQ-9: 22 (Severe depression)
- GAD-7: 18 (Severe anxiety)
- PC-PTSD-5: 5/5 positive
- PCL-5: 58 (Severe PTSD - cutoff ≥33)
- C-SSRS: **HIGH RISK** - ideation with plan, intent, and means
- AUDIT: 24 (Likely dependence)
- ISI: 24 (Severe insomnia)
- WSAS: 35 (Severe impairment)

**Expected Recommendations** (URGENT):
- 🚨 **IMMEDIATE SAFETY INTERVENTION**
- Crisis resources displayed prominently (988, VA Crisis Line)
- Safety planning (remove firearm access)
- Recommend emergency department evaluation if acute risk
- **URGENT psychiatric evaluation within 24-48 hours**
- Trauma-focused therapy (PE, CPT, EMDR) - specialized PTSD treatment
- Consider medication (SSRI: sertraline, paroxetine for PTSD)
- Prazosin for nightmares
- Substance use treatment (may need detox if severe)
- VA mental health services referral
- Close follow-up (weekly initially)
- Family/support system involvement
- Consider intensive outpatient program (IOP) or partial hospitalization

**Risk Flags**:
- Provider alert: HIGH SUICIDE RISK
- Weapon access documented
- Substance use complicating treatment
- Complex PTSD + depression + substance use

---

## 🏗️ SYSTEM ARCHITECTURE

### **Backend Structure**
```
psychnow-backend/
├── main.py                           # FastAPI app entry
├── requirements.txt
├── .env.example
├── docker-compose.yml                # PostgreSQL + backend
├── alembic.ini
│
├── app/
│   ├── core/
│   │   ├── config.py                # Settings (OpenAI key, DB URL, etc.)
│   │   ├── security.py              # JWT, password hashing
│   │   └── deps.py                  # FastAPI dependencies
│   │
│   ├── db/
│   │   ├── base.py                  # SQLAlchemy base
│   │   ├── session.py               # DB session
│   │   └── init_db.py               # Seed data
│   │
│   ├── models/                      # SQLAlchemy ORM models
│   │   ├── user.py
│   │   ├── intake_session.py
│   │   ├── intake_report.py
│   │   ├── provider_profile.py
│   │   └── provider_review.py
│   │
│   ├── schemas/                     # Pydantic schemas
│   │   ├── user.py
│   │   ├── intake.py
│   │   ├── message.py
│   │   └── screener.py
│   │
│   ├── api/v1/
│   │   ├── auth.py                  # Register, login, token
│   │   ├── intake.py                # Start session, chat, finish
│   │   ├── reports.py               # CRUD for reports
│   │   ├── providers.py             # Provider endpoints
│   │   └── admin.py                 # Admin endpoints
│   │
│   ├── services/
│   │   ├── llm_service.py          # OpenAI wrapper
│   │   ├── conversation_service.py  # State machine
│   │   ├── screener_service.py     # Screener orchestration
│   │   └── report_service.py       # Report generation
│   │
│   ├── screeners/                   # All 30 screener implementations
│   │   ├── base.py                 # Base screener class
│   │   ├── depression/
│   │   │   ├── phq9.py
│   │   │   ├── phq2.py
│   │   │   └── bdi2.py
│   │   ├── anxiety/
│   │   │   ├── gad7.py
│   │   │   ├── gad2.py
│   │   │   ├── spin.py
│   │   │   └── pdss.py
│   │   ├── adhd/
│   │   │   └── asrs.py
│   │   ├── trauma/
│   │   │   ├── pcl5.py
│   │   │   └── pc_ptsd5.py
│   │   ├── bipolar/
│   │   │   ├── mdq.py
│   │   │   └── hcl32.py
│   │   ├── substance/
│   │   │   ├── audit.py
│   │   │   ├── audit_c.py
│   │   │   ├── dast10.py
│   │   │   └── cage_aid.py
│   │   ├── suicide/
│   │   │   ├── cssrs.py             # CRITICAL
│   │   │   └── asq.py
│   │   ├── sleep/
│   │   │   ├── isi.py
│   │   │   └── ess.py
│   │   ├── eating/
│   │   │   ├── scoff.py
│   │   │   └── ede_qs.py
│   │   ├── ocd/
│   │   │   └── oci_r.py
│   │   ├── general/
│   │   │   ├── k6.py
│   │   │   └── wsas.py
│   │   ├── personality/
│   │   │   ├── msi_bpd.py
│   │   │   └── pid5_bf.py
│   │   ├── psychosis/
│   │   │   └── prime.py
│   │   └── registry.py             # Screener factory
│   │
│   ├── prompts/
│   │   ├── system_prompts.py       # Main Ava instructions
│   │   ├── phase_prompts.py        # Per-phase templates
│   │   └── report_prompts.py       # Report generation
│   │
│   └── utils/
│       ├── validators.py
│       ├── formatters.py
│       └── session_cache.py        # In-memory session storage
│
└── tests/
    ├── test_screeners/              # Unit tests for all 30
    ├── test_conversation.py
    └── test_api.py
```

### **Frontend Structure**
```
pychnow design/
├── src/
│   ├── api/
│   │   ├── client.ts               # Axios config
│   │   ├── auth.ts
│   │   ├── intake.ts
│   │   └── reports.ts
│   │
│   ├── hooks/
│   │   ├── useAuth.ts
│   │   ├── useIntakeSession.ts
│   │   └── useReports.ts
│   │
│   ├── contexts/
│   │   └── AuthContext.tsx
│   │
│   ├── types/
│   │   ├── user.ts
│   │   ├── intake.ts
│   │   └── report.ts
│   │
│   ├── components/
│   │   ├── intake/
│   │   │   ├── IntakeChat.tsx
│   │   │   ├── ChatMessage.tsx
│   │   │   ├── ScreenerQuestion.tsx
│   │   │   ├── IntakeComposer.tsx
│   │   │   └── ProgressTracker.tsx
│   │   ├── provider/
│   │   │   ├── ReportList.tsx
│   │   │   ├── ReportDetail.tsx
│   │   │   └── ReviewForm.tsx
│   │   └── admin/
│   │       ├── IntakeList.tsx
│   │       └── AssignReport.tsx
│   │
│   └── pages/
│       ├── LandingPage.tsx
│       ├── auth/
│       ├── intake/
│       ├── patient/
│       ├── provider/
│       └── admin/
```

---

## 🗄️ DATABASE SCHEMA

```sql
-- Users (patients, providers, admins)
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL, -- patient, provider, admin
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Provider profiles
CREATE TABLE provider_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    npi VARCHAR(20),
    license_number VARCHAR(50),
    license_state VARCHAR(2),
    specialty VARCHAR(100),
    bio TEXT,
    invite_code VARCHAR(50),
    approval_status VARCHAR(20) DEFAULT 'pending',
    approved_by UUID REFERENCES users(id),
    approved_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Intake sessions
CREATE TABLE intake_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_id UUID REFERENCES users(id) NULL,
    session_token VARCHAR(100) UNIQUE NOT NULL,
    current_phase VARCHAR(50),
    conversation_history JSONB,
    extracted_data JSONB,
    screener_scores JSONB,
    risk_flags JSONB,
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP
);

-- Intake reports
CREATE TABLE intake_reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID REFERENCES intake_sessions(id),
    patient_id UUID REFERENCES users(id) NULL,
    report_data JSONB NOT NULL,
    severity_level VARCHAR(20),
    risk_level VARCHAR(20),
    urgency VARCHAR(20), -- routine, urgent, emergent
    pdf_path VARCHAR(500),
    shared_with_provider_id UUID REFERENCES users(id) NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Provider reviews
CREATE TABLE provider_reviews (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    report_id UUID REFERENCES intake_reports(id),
    provider_id UUID REFERENCES users(id),
    status VARCHAR(20) DEFAULT 'pending',
    clinical_notes TEXT,
    recommendations TEXT,
    reviewed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);
```

---

## 📅 DEVELOPMENT TIMELINE (28 Days)

### **Week 1: Backend Foundation + Core Screeners (Days 1-7)**

#### **Day 1: Project Setup**
- [ ] Create backend folder structure
- [ ] Install dependencies (FastAPI, SQLAlchemy, etc.)
- [ ] Set up PostgreSQL with Docker
- [ ] Create database models
- [ ] Initialize Alembic migrations
- [ ] Create .env.example

#### **Day 2: Authentication System**
- [ ] User model and schemas
- [ ] Password hashing (bcrypt)
- [ ] JWT token generation
- [ ] Register endpoint
- [ ] Login endpoint
- [ ] Get current user endpoint
- [ ] Test with Postman

#### **Day 3-4: Core Screeners (Group 1)**
- [ ] Base screener class with scoring interface
- [ ] PHQ-9 implementation + tests
- [ ] PHQ-2 implementation + tests
- [ ] GAD-7 implementation + tests
- [ ] GAD-2 implementation + tests
- [ ] C-SSRS implementation + tests (CRITICAL)
- [ ] Screener registry/factory pattern

#### **Day 5-6: Core Screeners (Group 2)**
- [ ] ASRS v1.1 (ADHD) + tests
- [ ] PCL-5 (PTSD) + tests
- [ ] AUDIT-C + tests
- [ ] ISI (Insomnia) + tests
- [ ] WSAS (Functional impairment) + tests

#### **Day 7: OpenAI Integration + Conversation Foundation**
- [ ] OpenAI service wrapper (streaming)
- [ ] Conversation phases defined
- [ ] Session state management
- [ ] Basic intake flow endpoint (greeting only)
- [ ] Test streaming responses

---

### **Week 2: Remaining Screeners + Conversation Engine (Days 8-14)**

#### **Day 8-9: Extended Screeners (Group 3)**
- [ ] AUDIT (full) + DAST-10 + CAGE-AID
- [ ] MDQ (Bipolar) + HCL-32
- [ ] SPIN (Social Anxiety) + PDSS (Panic)
- [ ] PC-PTSD-5 + ASQ

#### **Day 10-11: Extended Screeners (Group 4)**
- [ ] SCOFF + EDE-QS (Eating Disorders)
- [ ] OCI-R (OCD)
- [ ] ESS (Sleep)
- [ ] K6 (Distress)
- [ ] MSI-BPD + PID-5-BF (Personality)
- [ ] PRIME (Psychosis risk)
- [ ] LSAS, FSS-Brief, BDI-II

#### **Day 12-13: Conversation Engine**
- [ ] Phase state machine
- [ ] Adaptive screener selection logic
- [ ] Conversation history management
- [ ] Data extraction from natural language
- [ ] Risk flag detection
- [ ] Prompt engineering for each phase
- [ ] Test full conversation flow

#### **Day 14: Report Generator**
- [ ] Report generation service
- [ ] LLM prompt for clinical report
- [ ] Report validation
- [ ] PDF generation (ReportLab)
- [ ] Save report to database
- [ ] Test with all 3 scenarios

---

### **Week 3: Frontend Integration + Provider Portal (Days 15-21)**

#### **Day 15: Frontend Cleanup & API Client**
- [ ] Remove all commented code
- [ ] Set up Axios client
- [ ] Auth API integration
- [ ] TanStack Query setup
- [ ] Auth context provider

#### **Day 16-17: Intake Flow Rebuild**
- [ ] Connect to new backend API
- [ ] Update streaming integration (SSE)
- [ ] Progress tracker component
- [ ] Better screener UI
- [ ] Risk alert displays
- [ ] Error handling
- [ ] Test end-to-end intake

#### **Day 18-19: Provider Portal**
- [ ] Provider registration page (with invite code)
- [ ] Provider login
- [ ] Provider dashboard UI
- [ ] Report list view
- [ ] Report detail view
- [ ] Review form component
- [ ] Backend provider endpoints

#### **Day 20: Admin Panel**
- [ ] Admin dashboard
- [ ] View all intakes
- [ ] View all reports
- [ ] Assign reports to providers
- [ ] Provider approval interface
- [ ] Basic analytics

#### **Day 21: Report Summary Enhancements**
- [ ] Update summary page with new backend data
- [ ] PDF download integration
- [ ] Visual score displays
- [ ] Resource recommendations by severity
- [ ] Share report flow

---

### **Week 4: Testing, Deployment, Clinical Validation (Days 22-28)**

#### **Day 22: Testing**
- [ ] Run all 3 test scenarios
- [ ] End-to-end tests
- [ ] Fix critical bugs
- [ ] Performance testing
- [ ] Error handling validation

#### **Day 23: Deployment Setup**
- [ ] Render backend deployment
- [ ] Render PostgreSQL setup
- [ ] Vercel frontend deployment
- [ ] Environment variables configured
- [ ] CORS configuration
- [ ] Test deployed version

#### **Day 24-25: Clinical Validation**
- [ ] Psychiatrist reviews system
- [ ] Test 3-5 intakes with psychiatrist oversight
- [ ] Review generated reports for clinical accuracy
- [ ] Adjust prompts based on feedback
- [ ] Validate screener scoring
- [ ] Check risk assessment appropriateness

#### **Day 26: Bug Fixes & Polish**
- [ ] Fix issues from clinical review
- [ ] UX improvements
- [ ] Loading states
- [ ] Error messages
- [ ] Mobile responsiveness

#### **Day 27: Documentation**
- [ ] User guide for patients
- [ ] Provider interpretation guide
- [ ] Admin manual
- [ ] API documentation
- [ ] Deployment guide

#### **Day 28: Pilot Preparation**
- [ ] Create 10 provider accounts (approved)
- [ ] Test all user flows
- [ ] Backup/restore procedures
- [ ] Monitoring setup
- [ ] Final checklist review

---

## 🔐 AUTHENTICATION FLOWS

### **Patient Flow**
```
1. Anonymous Intake:
   - User lands on /patient-intake
   - No login required
   - Session token generated (UUID)
   - Completes intake
   - Gets summary + "Save Results" button

2. Patient Registration:
   - Click "Save Results" or "Sign Up"
   - Enter email + password + name
   - JWT token issued
   - Can view saved reports
   - Can share with providers (admin assigns)

3. Patient Login:
   - Email + password
   - JWT token issued
   - Access dashboard, view reports
```

### **Provider Flow**
```
1. Provider Registration:
   - Go to /provider-signup
   - Enter email + password + name
   - Enter invite code (e.g., "PSYCHNOW-PROVIDER-2024")
   - Submit NPI, license info
   - Account created with status="pending_approval"

2. Admin Approval:
   - Admin sees pending providers in admin panel
   - Reviews credentials
   - Clicks "Approve"
   - Provider status → "approved"

3. Provider Login:
   - Email + password
   - JWT token issued
   - Access provider dashboard
   - See assigned reports
```

### **Admin Flow**
```
1. Admin Account:
   - Manually seeded in database (you)
   - Email + password login

2. Admin Functions:
   - View all intakes/reports
   - Approve providers
   - Assign reports to providers
   - View analytics
```

---

## 🎯 API ENDPOINTS (Complete)

### **Authentication**
```
POST   /api/v1/auth/register          # Register (patient or provider)
POST   /api/v1/auth/login             # Login (all roles)
POST   /api/v1/auth/refresh           # Refresh JWT token
GET    /api/v1/auth/me                # Get current user info
```

### **Intake**
```
POST   /api/v1/intake/start           # Start new session → session_token
POST   /api/v1/intake/chat            # Send message → SSE stream response
GET    /api/v1/intake/session/{token} # Get session state
POST   /api/v1/intake/finish          # Generate report from session
```

### **Reports**
```
GET    /api/v1/reports                # List current user's reports
GET    /api/v1/reports/{id}           # Get report detail
GET    /api/v1/reports/{id}/pdf       # Download PDF
POST   /api/v1/reports/{id}/share     # Request share with provider
```

### **Provider**
```
GET    /api/v1/provider/reports       # List reports assigned to me
GET    /api/v1/provider/reports/{id}  # Get report detail
POST   /api/v1/provider/reviews       # Add review/clinical notes
PUT    /api/v1/provider/reviews/{id}  # Update review
GET    /api/v1/provider/profile       # Get my provider profile
PUT    /api/v1/provider/profile       # Update my profile
```

### **Admin**
```
GET    /api/v1/admin/intakes          # All intake sessions
GET    /api/v1/admin/reports          # All reports
GET    /api/v1/admin/providers        # All providers (pending + approved)
POST   /api/v1/admin/providers/{id}/approve  # Approve provider
POST   /api/v1/admin/assign           # Assign report to provider
GET    /api/v1/admin/stats            # Pilot metrics (completions, etc.)
```

---

## 💰 COST ESTIMATE (Pilot)

### **Infrastructure**
- Render Web Service: **$0** (Free tier - 500 hrs/month)
- Render PostgreSQL: **$0** (Free 90 days, then $7/month)
- Vercel: **$0** (Hobby tier)

### **OpenAI API** (Estimated for 10 patients)
**Assumptions**:
- 10 patients complete full intake
- Average 150 messages per intake (comprehensive with all screeners)
- Average 2,500 tokens per message (input + output)
- gpt-4o-mini pricing: $0.15 per 1M input tokens, $0.60 per 1M output tokens

**Per Intake**:
```
150 messages × 2,500 tokens = 375,000 tokens
Split: ~200K input, ~175K output

Input cost:  200,000 × $0.15 / 1M = $0.03
Output cost: 175,000 × $0.60 / 1M = $0.105
Per intake: ~$0.14

Report generation (additional):
~15,000 tokens output = $0.009

Total per patient: ~$0.15
```

**10 Patients**: ~$1.50

**If using gpt-4o** (better quality):
- Input: $2.50/1M, Output: $10/1M
- Per intake: ~$2.25
- 10 patients: ~$22.50

### **Total Pilot Cost**
- Infrastructure: **$0** (first 3 months)
- OpenAI (gpt-4o-mini): **~$2**
- OpenAI (gpt-4o): **~$25**

**Recommendation**: Start with gpt-4o-mini, upgrade to gpt-4o if quality isn't sufficient.

---

## ✅ SUCCESS METRICS

### **Technical Metrics**
- [ ] 10 intakes completed successfully (100% completion rate)
- [ ] All 10 reports generated without errors
- [ ] 0 data loss incidents
- [ ] API response time <2 seconds (p95)
- [ ] Frontend load time <3 seconds
- [ ] 0 critical bugs in production

### **Clinical Metrics** (Psychiatrist Validation)
- [ ] Report completeness score ≥90%
- [ ] Screener scoring accuracy: 100%
- [ ] Risk assessment flags: Clinically appropriate
- [ ] Differential diagnosis suggestions: Reasonable and evidence-based
- [ ] Recommendations: Specific and actionable
- [ ] Overall clinical quality rating: ≥8/10

### **UX Metrics**
- [ ] Average intake completion time: 15-25 minutes
- [ ] Patient satisfaction: ≥8/10
- [ ] Provider satisfaction with reports: ≥8/10
- [ ] Provider time saved per patient: ≥30 minutes (estimated)
- [ ] Conversation naturalness rating: ≥7/10

### **Pilot Readiness**
- [ ] All 3 test scenarios pass
- [ ] Psychiatrist approves system for pilot
- [ ] 10 provider accounts created and approved
- [ ] Documentation complete
- [ ] Deployed and accessible
- [ ] Backup/monitoring in place

---

## 🚨 CRITICAL RISKS & MITIGATIONS

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| **OpenAI API failures** | High | Medium | Retry logic, error messages, fallback prompts |
| **Screener scoring errors** | Critical | Low | Unit tests for all 30, validate against published scoring |
| **LLM hallucinations (clinical info)** | Critical | Medium | Structured outputs, validation, few-shot examples, post-processing |
| **Suicide risk missed** | Critical | Low | Always run C-SSRS if depression detected, prominent resources, provider alerts |
| **Report quality inconsistent** | High | Medium | Prompt engineering iteration, validation rules, psychiatrist review |
| **Patient abandons mid-intake** | Medium | High | Progress indicators, time estimates, session resumption, save progress |
| **Database data loss** | Critical | Very Low | Daily backups, transaction logging, Render automated backups |
| **Provider misinterprets report** | High | Medium | Clear report structure, interpretation guide, disclaimer |

---

## 📚 DOCUMENTATION DELIVERABLES

### **Technical Docs**
1. **README.md** - Project overview, setup instructions
2. **API_DOCUMENTATION.md** - All endpoints with examples
3. **DEPLOYMENT_GUIDE.md** - Step-by-step deployment
4. **SCREENER_REFERENCE.md** - All 30 screeners with scoring rules

### **Clinical Docs**
5. **CLINICAL_INTERPRETATION_GUIDE.md** - For providers
6. **SCREENER_DESCRIPTIONS.md** - What each screener measures
7. **RISK_ASSESSMENT_PROTOCOL.md** - How C-SSRS is used

### **User Docs**
8. **PATIENT_USER_GUIDE.md** - How to complete intake
9. **PROVIDER_USER_GUIDE.md** - How to review reports
10. **ADMIN_MANUAL.md** - Admin panel functions

---

## 🎬 IMMEDIATE NEXT STEPS (Before Coding)

### **What You Need to Do**:

1. **Environment Setup** (15 minutes):
   ```bash
   # Verify installations:
   python3 --version  # Need 3.11+
   node --version     # Need 18+
   npm --version
   git --version
   docker --version   # Optional but recommended
   
   # Install Docker Desktop (if not installed)
   # https://www.docker.com/products/docker-desktop/
   ```

2. **OpenAI API Key** (5 minutes):
   - Go to https://platform.openai.com/api-keys
   - Create new key
   - Set budget limit ($50 recommended)
   - Save key securely (you'll add to .env)

3. **Repository Decision** (1 minute):
   - **Confirm**: Single repo (PsychNow folder) or separate repos?
   - **Recommendation**: Single repo for pilot

4. **Review This Plan** (10 minutes):
   - Any concerns or changes needed?
   - Are all 3 test scenarios realistic?
   - Any screeners you want prioritized differently?

---

## 🚀 ONCE YOU CONFIRM "READY TO BUILD"

**I will generate in the next message**:

### **Batch 1: Complete Backend Structure**
- All folders and files created
- requirements.txt with dependencies
- Database models (all tables)
- Alembic migration files
- docker-compose.yml for PostgreSQL
- .env.example template
- README.md with setup instructions

### **Batch 2: Core Backend Implementation**
- Auth system (register, login, JWT)
- Base screener class
- First 5 screeners (PHQ-9, GAD-7, C-SSRS, ASRS, PCL-5)
- OpenAI service wrapper
- Basic intake endpoint

### **Batch 3: Testing Instructions**
- How to run the backend locally
- How to test endpoints with Postman
- How to verify screeners are scoring correctly

**Then we iterate day by day through the 28-day timeline.**

---

## 📋 FINAL CONFIRMATION CHECKLIST

Before saying "START BUILDING", confirm:

- [ ] **Branding**: PsychNow, tagline, Ava as AI guide ✓
- [ ] **Tech Stack**: FastAPI + React + PostgreSQL ✓
- [ ] **All 30 screeners**: Confirmed ✓
- [ ] **Test scenarios**: 3 scenarios generated and approved
- [ ] **Timeline**: 4 weeks full-time ✓
- [ ] **Repository**: Single repo or separate? (PENDING)
- [ ] **Environment**: Python/Node/Docker installed (PENDING)
- [ ] **OpenAI API**: Key ready (PENDING)
- [ ] **Plan Approved**: No major concerns (PENDING)

---

**Once you respond with confirmations to the PENDING items above, we begin building immediately!** 🚀

**Next Message**: I'll generate the complete backend structure and first working code.


