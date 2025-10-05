# Pause/Resume Session Enhancement - Complete

## Overview
Implemented comprehensive pause/resume functionality that persists across page navigation and browser sessions, allowing patients to pause their assessment and return to it from the dashboard.

## Implementation Summary

### ✅ Part 1: Backend API Enhancement

**New Endpoint:** `GET /api/v1/intake/sessions/me`
- Returns all active and paused sessions for the authenticated user
- Includes session details: status, phase, resume_token, expiration, progress
- Handles both authenticated and anonymous users

**File Modified:** `backend/app/api/v1/intake.py`

### ✅ Part 2: Frontend PatientIntake Component

**Changes Made:**

1. **Pause Persistence** (Line ~354-361)
   - When user pauses assessment, saves to `localStorage`:
     ```typescript
     localStorage.setItem('paused_session', JSON.stringify({
       session_token,
       resume_token,
       expires_at,
       paused_at,
       completed_screeners
     }));
     ```

2. **Auto-Resume on Mount** (Line ~32-74)
   - On component load, checks `localStorage` for paused session
   - Validates expiration (24-hour window)
   - Prompts user: "You have a paused assessment. Would you like to continue where you left off?"
   - If yes → automatically resumes with saved progress
   - If no or expired → clears localStorage and starts fresh

3. **Cleanup on Completion** (Line ~493)
   - Clears `paused_session` from localStorage when assessment finishes
   - Also clears on successful resume (Line ~444)
   - Also clears on expired session (Line ~453)

**File Modified:** `pychnow design/src/components/PatientIntake.tsx`

### ✅ Part 3: Patient Dashboard Integration

**New Features:**

1. **Fetch Paused Sessions** (fetchPausedSessions function)
   - Checks localStorage for anonymous sessions
   - Calls backend API for authenticated users
   - Validates expiration automatically
   - Clears expired sessions

2. **Visual Display** (In-Progress Assessment Card)
   - Prominent blue card at top of dashboard
   - Animated pulsing indicator
   - Shows:
     - When paused (timestamp)
     - Progress (# of screeners completed)
     - Expiration time
   - Clear "Resume Assessment" button

3. **Seamless Navigation**
   - Click "Resume Assessment" → navigates to `/patient-intake`
   - PatientIntake auto-detects paused session
   - Continues exactly where they left off

**File Modified:** `pychnow design/src/components/PatientDashboard.tsx`

## User Flow

### Scenario 1: Anonymous User Pauses
1. User starts assessment (no login)
2. Clicks "Take a Break" → paused, saved to localStorage
3. Navigates to dashboard
4. Dashboard shows "Assessment In Progress" card
5. Clicks "Resume" → auto-resumes with all progress intact

### Scenario 2: Authenticated User Pauses
1. User starts assessment (logged in)
2. Clicks "Take a Break" → paused, saved to localStorage + backend
3. Closes browser completely
4. Returns later, signs in
5. Dashboard fetches from backend
6. Shows paused session, clicks Resume → continues

### Scenario 3: Returning to Intake Page
1. User has paused session
2. Navigates directly to `/patient-intake`
3. Automatically prompted: "Continue or start fresh?"
4. Choose continue → resumes immediately
5. Choose fresh → clears paused session, starts new

### Scenario 4: Expiration Handling
1. Session paused for > 24 hours
2. Returns to dashboard → expired session removed
3. No prompt shown, can start fresh assessment

## Technical Details

### Data Structure (localStorage)
```typescript
{
  session_token: string;      // UUID of session
  resume_token: string;       // Token for resume endpoint
  expires_at: string;         // ISO timestamp (24hr from pause)
  paused_at: string;          // When user paused
  completed_screeners: string[]; // Progress indicator
}
```

### Backend Response (GET /sessions/me)
```json
{
  "sessions": [
    {
      "id": "uuid",
      "session_token": "uuid",
      "status": "paused",
      "current_phase": "screening",
      "resume_token": "uuid",
      "paused_at": "2025-10-03T10:00:00",
      "expires_at": "2025-10-04T10:00:00",
      "completed_screeners": ["PHQ-9", "GAD-7"]
    }
  ]
}
```

## Benefits

✅ **No Lost Progress** - Users can safely navigate away
✅ **Cross-Device** - Authenticated users can resume from any device
✅ **Automatic Cleanup** - Expired sessions auto-deleted
✅ **User Choice** - Clear prompts, no forced resume
✅ **Visual Feedback** - Clear dashboard indicator
✅ **Graceful Degradation** - Works for anonymous users via localStorage
✅ **Error Handling** - Handles expired tokens, network errors

## Testing Checklist

- [ ] Pause assessment → navigate to dashboard → see "In Progress" card
- [ ] Click "Resume" from dashboard → continues correctly
- [ ] Navigate directly to intake with paused session → prompted
- [ ] Choose "Continue" → resumes with full history
- [ ] Choose "Start Fresh" → begins new assessment
- [ ] Complete assessment → paused session cleared from dashboard
- [ ] Wait 24+ hours → expired session auto-removed
- [ ] Authenticated user → sessions persist after logout/login

## Future Enhancements

- Add "Start New Assessment" button next to "Resume" for choice
- Show multiple paused sessions if user has more than one
- Add "Discard Paused Session" option in dashboard
- Email reminder for paused sessions (before expiration)
- Mobile notifications for paused assessments

## Files Changed

1. `backend/app/api/v1/intake.py` - Added GET /sessions/me endpoint
2. `pychnow design/src/components/PatientIntake.tsx` - localStorage persistence + auto-resume
3. `pychnow design/src/components/PatientDashboard.tsx` - Display and resume functionality

