# Pause/Resume Functionality Implementation

## Overview
Implemented comprehensive pause/resume functionality for PsychNow intake assessments, allowing patients to take breaks during their assessment and continue later.

## Implementation Date
October 2, 2025

## Features Implemented

### 1. Database Schema
**Added to `IntakeSession` model:**
- `paused_at`: DateTime - When session was paused
- `expires_at`: DateTime - When paused session expires (24 hours)
- `resume_token`: String(100) - Secure token for resuming
- `completed_screeners`: JSON - List of completed screeners
- `current_screener`: String(50) - Current screener being worked on
- `screener_progress`: JSON - Progress within current screener

### 2. Backend API Endpoints

#### `/api/v1/intake/pause` (POST)
- Pauses an active intake session
- Validates session can be paused (not in middle of assessment)
- Generates secure resume token
- Sets 24-hour expiration
- Returns: `resume_token`, `expires_at`, `completed_screeners`

#### `/api/v1/intake/resume` (POST)
- Resumes a paused session using resume token
- Validates session hasn't expired
- Restores full conversation state
- Returns: `session_token`, `welcome_message`, `completed_screeners`

#### `/api/v1/intake/cleanup` (POST)
- Cleans up expired paused sessions
- Removes abandoned sessions from memory
- Returns: Statistics about cleaned sessions

#### `/api/v1/intake/stats` (GET)
- Returns session statistics
- Tracks: active, paused, completed, abandoned, total sessions

### 3. Pause/Resume Rules

#### When Pause is Allowed:
✅ Between conversations
✅ After completing symptom exploration
✅ After completing an entire screener (PHQ-9, GAD-7, etc.)

#### When Pause is NOT Allowed:
❌ In the middle of a screener question
❌ During C-SSRS safety assessment
❌ If the last AI message was asking a screener question

### 4. Session Expiration
- **Duration**: 24 hours from pause time
- **Expiration Handling**: Sessions marked as "abandoned" after expiration
- **Automatic Cleanup**: Cleanup service can be run periodically

### 5. Conversation Service Enhancements

#### New Methods:
- `restore_session(session_token, session_data)`: Restores paused session with full state
- `_track_screener_completion(session_token, response)`: Tracks when screeners are completed
- Screener completion indicators added for PHQ-9, GAD-7, C-SSRS

#### State Tracking:
- `completed_screeners`: List of fully completed screeners
- `current_screener`: Screener currently in progress
- `screener_progress`: Progress within current screener

### 6. Session Cleanup Service

**New Service: `session_cleanup_service.py`**

**Methods:**
- `cleanup_expired_sessions(db)`: Marks expired paused sessions as abandoned
- `cleanup_abandoned_sessions(db, hours_threshold)`: Cleans old abandoned sessions from memory
- `get_expiring_sessions(db, hours_ahead)`: Gets sessions expiring soon (for reminders)
- `get_session_stats(db)`: Returns session statistics

### 7. Frontend Implementation

#### UI Components Added:
1. **"Take a Break" Button**: In message input area
2. **Pause Status Banner**: Shows when session is paused with expiration time
3. **"Continue Assessment" Button**: Allows resuming paused session
4. **Progress Indicator**: Shows completed screeners

#### State Management:
- `paused`: Boolean - Session pause state
- `resumeToken`: String - Token for resuming
- `expiresAt`: String - Expiration timestamp
- `completedScreeners`: Array - List of completed screeners

#### Functions Added:
- `pauseSession()`: Calls pause endpoint
- `resumeSession(token)`: Calls resume endpoint with token
- Input area disabled when paused

### 8. User Experience Flow

**Pausing:**
1. Patient clicks "Take a Break" button
2. Backend validates pause is allowed
3. Generates secure resume token
4. Shows confirmation message with expiration time
5. Session state saved to database

**Resuming:**
1. Patient clicks "Continue Assessment"
2. Backend validates resume token
3. Checks expiration status
4. Restores full conversation state
5. Shows personalized welcome back message
6. Patient continues where they left off

### 9. Clinical Appropriateness

**Design Decisions:**
- ✅ Pause between natural break points
- ✅ Complete screeners before pausing (maintains clinical validity)
- ✅ 24-hour expiration (reasonable for clinical context)
- ✅ Progress tracking (patient knows what's completed)
- ❌ No pause during safety assessment (clinical continuity required)

### 10. Security Considerations

**Implemented:**
- Secure token generation (`secrets.token_urlsafe(32)`)
- Token stored uniquely in database
- Automatic expiration and cleanup
- Authorization required for all endpoints

### 11. Analytics Support

**Tracking Implemented:**
- Pause/resume events logged in session history
- Session statistics endpoint for monitoring
- Completed screeners tracked
- Session status transitions (active → paused → active/abandoned)

### 12. Future Enhancements (Not Yet Implemented)

**Dashboard Integration:**
- Display paused sessions on patient dashboard
- One-click resume from dashboard

**Email Reminders:**
- Email notification when session expires in 2 hours
- Reminder with resume link

**Provider Notifications:**
- Optional provider notification of paused sessions
- Analytics dashboard for session completion rates

## Testing Notes

To manually test:
1. Start backend server: `cd backend && uvicorn app.main:app --reload`
2. Start frontend: `cd "pychnow design" && npm run dev`
3. Start an assessment
4. Answer a few questions
5. Click "Take a Break"
6. Click "Continue Assessment"
7. Verify conversation continues where it left off

## Files Modified/Created

### Backend:
- `backend/app/models/intake_session.py` - Added pause/resume fields
- `backend/app/api/v1/intake.py` - Added pause/resume/cleanup/stats endpoints
- `backend/app/services/conversation_service.py` - Added restore and tracking methods
- `backend/app/services/session_cleanup_service.py` - New cleanup service
- `backend/alembic/versions/20251002_1233_2ec613c9177f_add_pause_resume_functionality.py` - Database migration

### Frontend:
- `pychnow design/src/components/PatientIntake.tsx` - Added pause/resume UI and logic

### Documentation:
- `PAUSE_RESUME_IMPLEMENTATION.md` - This document

## Benefits

1. **Reduced Abandonment**: Patients can take breaks without losing progress
2. **Improved Accessibility**: Accommodates patients with attention difficulties
3. **Better UX**: Handles real-world interruptions gracefully
4. **Clinical Validity**: Maintains assessment integrity by requiring screener completion
5. **Data Security**: Secure token-based resumption with expiration
6. **Analytics**: Comprehensive tracking of session states

## Implementation Complete

All core pause/resume functionality has been implemented and is ready for testing and deployment.
