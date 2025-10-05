# Rate Limit and PDF Download Fixes - October 3, 2025

## Issues Identified

### 1. Rate Limit Too Restrictive
**Problem:** 
- Chat endpoint limited to 10 requests/minute
- Patients clicking through screener options (PHQ-9, GAD-7) hit limit during normal use
- Results in "Sorry, I encountered an error" messages

**Impact:**
- Disrupts clinical assessment flow
- Poor user experience during legitimate use
- Patients think the app is broken

### 2. PDF Download Button Not Appearing
**Problem:**
- Backend was generating PDF and sending via SSE with `pdf_report` field
- Frontend was not capturing/handling the `pdf_report` field
- Only `content`, `options`, and `done` were being processed

**Impact:**
- Patients couldn't download their completed assessment report
- Had to manually navigate to dashboard

### 3. Outstanding Issues (Logged, Not Fixed Yet)
**Energy Level Options:**
- Currently only shows low options (Slightly/Moderately/Severely low)
- Missing high/normal options needed for bipolar/mania screening

**Screener Introduction Flow:**
- Ava explains screeners but doesn't wait for "Are you ready?" acknowledgment
- Should pause and wait for patient response before starting first screener question

## Fixes Implemented

### Rate Limiting Improvements

**File:** `backend/app/core/rate_limit.py`
- Added environment-aware rate limit functions
- Development: 300/minute (for testing)
- Production: 15/10seconds;60/minute (burst-aware: 15 rapid clicks allowed, 60/min sustained)
- Staging: 10/10seconds;45/minute

**File:** `backend/app/api/v1/intake.py`
- Updated all endpoints to use dynamic rate limits:
  - `/start`: Uses `get_start_rate_limit()` - 100/min dev, 10/min prod
  - `/chat`: Uses `get_chat_rate_limit()` - 300/min dev, burst-aware prod
  - `/pause`: Uses `get_pause_resume_rate_limit()` - 100/min dev, 20/min prod
  - `/resume`: Uses `get_pause_resume_rate_limit()` - 100/min dev, 20/min prod

**Benefits:**
- ✅ Smooth screener completion without false errors
- ✅ Still protected against abuse in production
- ✅ Burst support allows rapid button clicks
- ✅ Development environment has high limits for testing

### PDF Download Fix

**File:** `pychnow design/src/components/PatientIntake.tsx`
- Added handler for `pdf_report` field in SSE stream parsing (lines 345-356)
- Now properly attaches PDF data to the message when received
- Download button will appear when `msg.pdf_report` exists

**Flow:**
1. Backend generates PDF and sends with `pdf_report` field in final message
2. Frontend captures `pdf_report` and attaches to last system message
3. UI renders download button when `msg.pdf_report` is present
4. Patient clicks button to download PDF

## Testing Required

1. **Rate Limits:** Run automated test and verify no "encountered an error" messages
2. **PDF Download:** Complete full assessment and verify download button appears
3. **Environment:** Confirm ENVIRONMENT is set to "development" in config for testing

## Cost Protection (Already in Place)

- Using `gpt-4o-mini` (cost-effective model)
- 24-hour session expiry for paused sessions
- Can add OpenAI dashboard spending limits
- Can monitor per-session token usage

## Next Steps (Not Implemented Yet)

1. Fix energy level options (add High/Normal ranges)
2. Fix screener introduction flow (enforce "Are you ready?" wait)
3. Consider enhanced rate limiting by user ID for authenticated users
4. Add frontend retry logic with backoff for 429 errors

