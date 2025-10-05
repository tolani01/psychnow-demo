# 🎯 **PSYCHNOW PLATFORM IMPROVEMENTS: DEVELOPER IMPLEMENTATION GUIDE**

## **⚠️ CRITICAL: READ THIS FIRST**

**Implementation Priority:** Complete phases in order. Each phase builds on the previous one.

**Testing Strategy:** Test thoroughly after each phase before moving to the next.

**Rollback Plan:** Each phase is independently reversible. Keep git commits granular.

**Estimated Timeline:** 
- Phase 1 (Infrastructure): 2-3 days
- Phase 2 (Safety Critical): 1-2 days  
- Phase 3 (Clinical Enhancements): 3-4 days
- Phase 4 (Provider Tools): 2-3 days
- **Total: 8-12 days for full implementation**

---

## **📋 PRE-IMPLEMENTATION CHECKLIST**

### **Before You Start:**
- [ ] Create a new feature branch: `git checkout -b feature/clinical-improvements`
- [ ] Back up the current database
- [ ] Document current system behavior (run test assessments and save outputs)
- [ ] Set up a staging environment for testing
- [ ] Review all three source files:
  - `backend/app/prompts/system_prompts.py`
  - `backend/app/services/conversation_service.py`
  - `backend/app/screeners/registry.py`
- [ ] Ensure you have access to test the complete flow (frontend + backend)

---

## **PHASE 1: CORE INFRASTRUCTURE (Days 1-3)**
**Goal:** Add deterministic parsing, flow control, and options handling

### **Step 1.1: Update system_prompts.py - Add OPTIONS Contract**

**File:** `backend/app/prompts/system_prompts.py`

**Location:** Inside `INTAKE_SYSTEM_PROMPT`, at the very beginning (after the opening `"""` but before any other content)

**What to Add:**
```
### OPTIONS FORMATTING CONTRACT (STRICT)
When you offer multiple-choice answers, you **must** include them between these exact delimiters and use dash bullets:
BEGIN_OPTIONS
- Option A
- Option B
- Option C
END_OPTIONS

Each bullet is a **human label** only. Do not add numbers, letters, or extra commentary inside this block.

### FINISH COMMAND
If the user types **:finish** (exact token) at any time, immediately stop asking new questions and proceed to generate the final report.

### ONE QUESTION PER MESSAGE (SERVER-ENFORCED)
Ask exactly **one** question per turn (only one `?` in your reply). If you need multiple follow-ups, ask them one at a time across subsequent turns.
```

**Validation:**
- [ ] Read through the entire prompt - ensure no duplication
- [ ] If these sections already exist elsewhere, remove the old ones
- [ ] Ensure proper indentation matches the surrounding prompt style

---

### **Step 1.2: Add Utility Constants to conversation_service.py**

**File:** `backend/app/services/conversation_service.py`

**Location:** Near the top of the file, after imports but before class definitions

**What to Add:**
```python
# ============================================================================
# FINISH TOKENS AND UTILITY SETS
# ============================================================================
_FINISH_TOKENS = {":finish", "/finish"}

_YES_SET = {
    "yes", "y", "yea", "yeah", "yep", "affirmative", 
    "sure", "ok", "okay", "correct", "right"
}

_NO_SET = {
    "no", "n", "nope", "nah", "negative", "incorrect", "wrong"
}
```

**Validation:**
- [ ] Ensure these are at module level (not inside a class)
- [ ] Check that variable names don't conflict with existing code
- [ ] Run: `python -c "from app.services.conversation_service import _FINISH_TOKENS; print(_FINISH_TOKENS)"`

---

### **Step 1.3: Add Core Helper Functions to conversation_service.py**

**File:** `backend/app/services/conversation_service.py`

**Location:** After the constants you just added, before any class definitions

**What to Add (4 functions in this exact order):**

#### **Function 1: is_finish_message**
```python
def is_finish_message(text: str) -> bool:
    """
    Return True if user explicitly signals finish via reserved token or strong finish phrases.
    
    Examples:
        >>> is_finish_message(":finish")
        True
        >>> is_finish_message("I'm done")
        True
        >>> is_finish_message("I don't know")
        False
    """
    if not text:
        return False
    t = text.strip().lower()
    
    # Check for explicit tokens
    if t in _FINISH_TOKENS:
        return True
    
    # Check for finish phrases
    FINISH_PHRASES = [
        "i'm done",
        "i am done",
        "that's all",
        "thats all",
        "that is all",
        "complete the assessment",
        "finish the assessment",
        "generate my report",
        "generate the report",
        "can i be done",
        "can we finish",
    ]
    
    return any(phrase in t for phrase in FINISH_PHRASES)
```

#### **Function 2: enforce_single_question**
```python
def enforce_single_question(model_text: str) -> str:
    """
    Ensure only one '?' appears. If multiple, keep through the first '?' and strip trailing.
    
    Examples:
        >>> enforce_single_question("How are you? What's your name?")
        "How are you?"
        >>> enforce_single_question("Tell me more")
        "Tell me more"
    """
    if not model_text:
        return model_text
    
    # Find first question mark
    q_idx = model_text.find("?")
    if q_idx == -1:
        # No question mark - this is OK (might be validation or statement)
        return model_text
    
    # Check for second question mark
    extra_q = model_text.find("?", q_idx + 1)
    if extra_q == -1:
        # Only one question mark - perfect
        return model_text
    
    # Multiple question marks - truncate after first
    return model_text[: q_idx + 1]
```

#### **Function 3: normalize_yes_no**
```python
def normalize_yes_no(text: str):
    """
    Return True for yes, False for no, or None if ambiguous.
    
    Examples:
        >>> normalize_yes_no("yes")
        True
        >>> normalize_yes_no("nope")
        False
        >>> normalize_yes_no("maybe")
        None
    """
    if text is None:
        return None
    
    t = text.strip().lower()
    
    # Clean to letters only
    t_clean = "".join(ch for ch in t if ch.isalpha() or ch.isspace()).strip()
    
    if t_clean in _YES_SET:
        return True
    if t_clean in _NO_SET:
        return False
    
    return None
```

#### **Function 4: parse_options_block**
```python
def parse_options_block(text: str) -> list:
    """
    Extract options between BEGIN_OPTIONS ... END_OPTIONS.
    Accept bullets starting with -, *, 1), 1., a), etc.
    Return list of {label, value, code}.
    
    Examples:
        >>> parse_options_block("BEGIN_OPTIONS\\n- Yes\\n- No\\nEND_OPTIONS")
        [{'label': 'Yes', 'value': 'Yes', 'code': 'yes'}, {'label': 'No', 'value': 'No', 'code': 'no'}]
    """
    import re
    
    if not text:
        return []
    
    lowered = text.lower()
    start = lowered.find("begin_options")
    end = lowered.find("end_options")
    
    if start != -1 and end != -1 and end > start:
        # Extract text between delimiters
        block = text[start + len("begin_options"):end]
    else:
        # Fallback: scan last 20 lines for bullets
        lines = text.splitlines()[-20:]
        block = "\n".join(lines)
    
    # Extract bulleted items
    bullets = []
    for line in block.splitlines():
        line = line.strip()
        if not line:
            continue
        
        # Match various bullet formats: -, *, 1), 1., a), a.
        if re.match(r"^(-|\*|\d+[.)]|[a-zA-Z][.)])\s+", line):
            item = re.sub(r"^(-|\*|\d+[.)]|[a-zA-Z][.)])\s+", "", line).strip()
            if item:
                bullets.append(item)
    
    # Deduplicate
    seen = set()
    cleaned = []
    for b in bullets:
        if b.lower() in seen:
            continue
        seen.add(b.lower())
        cleaned.append(b)
    
    # Create slugs for codes
    def slug(s: str) -> str:
        s = s.lower().strip()
        s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
        return s[:40] or "option"
    
    return [{"label": b, "value": b, "code": slug(b)} for b in cleaned]
```

**Validation:**
- [ ] Run Python tests for each function (use the docstring examples)
- [ ] Test `is_finish_message()` with: ":finish", "I'm done", "I don't know"
- [ ] Test `enforce_single_question()` with: "How are you? What's next?"
- [ ] Test `normalize_yes_no()` with: "yes", "nope", "maybe"
- [ ] Test `parse_options_block()` with sample BEGIN_OPTIONS/END_OPTIONS text

---

### **Step 1.4: Add C-SSRS Helper Functions**

**File:** `backend/app/services/conversation_service.py`

**Location:** After the functions from Step 1.3

**What to Add:**

```python
# ============================================================================
# C-SSRS BRANCHING HELPERS
# ============================================================================
CSSRS_QUESTIONS = [
    "In the past month, have you wished you were dead or wished you could go to sleep and not wake up?",
    "Have you actually had any thoughts of killing yourself?",
    "Have you been thinking about how you might do this?",
    "Have you had these thoughts and had some intention of acting on them?",
    "Have you started to work out or worked out the details of how to kill yourself? Do you intend to carry out this plan?",
    "In the past 3 months, have you done anything, started to do anything, or prepared to do anything to end your life?",
]

def cssrs_next_question(answers: dict) -> tuple:
    """
    Return (next_question_text, is_high_risk).
    
    Clinical branching logic:
    - Q1 No → STOP (low risk)
    - Q1 Yes, Q2 No → Continue briefly (passive ideation)
    - Q2 Yes → MUST complete all questions
    - Q4 or Q5 Yes → HIGH RISK FLAG
    
    Args:
        answers: Dict like {"Q1": True, "Q2": False, ...}
    
    Returns:
        (question_text or None, high_risk_boolean)
    """
    # Q1: Passive death wish
    if "Q1" not in answers:
        return (CSSRS_QUESTIONS[0], False)
    
    # If Q1 is No, we're done (no ideation)
    if not answers.get("Q1"):
        return (None, False)
    
    # Q1 was Yes, need Q2
    if "Q2" not in answers:
        return (CSSRS_QUESTIONS[1], False)
    
    # If Q2 is No (passive only), we can stop here
    if not answers.get("Q2"):
        return (None, False)
    
    # Q2 is Yes (active SI) - MUST complete all remaining questions
    for i in range(3, 7):  # Q3 through Q6
        key = f"Q{i}"
        if key not in answers:
            # Check if we've already detected high risk
            high_risk = any(answers.get(f"Q{j}") for j in range(4, i))
            return (CSSRS_QUESTIONS[i-1], high_risk)
    
    # All questions answered - determine final risk
    high_risk = any(answers.get(f"Q{i}") for i in range(4, 7))
    return (None, high_risk)


def cssrs_risk_flag(answers: dict) -> bool:
    """
    Return True if any high-risk C-SSRS answers are present.
    High risk = Q4, Q5, or Q6 answered "Yes"
    """
    return any(answers.get(f"Q{i}") for i in range(4, 7))


def crisis_message() -> str:
    """Return the standard crisis intervention message."""
    return (
        "🚨 **IMMEDIATE SAFETY RESOURCES** 🚨\n\n"
        "If you're in immediate danger or thinking about harming yourself:\n\n"
        "• **Call 988** - Suicide & Crisis Lifeline (24/7)\n"
        "• **Text HOME to 741741** - Crisis Text Line\n"
        "• **Call 911** - If you're in immediate danger\n"
        "• **Go to your nearest Emergency Department**\n\n"
        "Your safety is the absolute priority. Help is available right now."
    )
```

**Validation:**
- [ ] Test `cssrs_next_question()` with various answer combinations
- [ ] Verify Q1=No stops immediately
- [ ] Verify Q2=Yes requires all questions
- [ ] Test `cssrs_risk_flag()` returns True when Q4/Q5/Q6 are Yes
- [ ] Verify `crisis_message()` returns formatted text with all resources

---

### **Step 1.5: Add Helper to registry.py**

**File:** `backend/app/screeners/registry.py`

**Location:** After imports, before the ScreenerRegistry class definition

**What to Add:**

```python
import re as _re

def parse_screener_options(text: str) -> list:
    """
    Parse options from screener question text.
    Looks for BEGIN_OPTIONS/END_OPTIONS blocks.
    
    Returns:
        List of dicts with {label, value, code}
    """
    if not text:
        return []
    
    lowered = text.lower()
    s = lowered.find("begin_options")
    e = lowered.find("end_options")
    
    if s != -1 and e != -1 and e > s:
        block = text[s + len("begin_options"):e]
    else:
        block = text
    
    items = []
    for line in block.splitlines():
        line = line.strip()
        if _re.match(r"^(-|\*|\d+[.)]|[a-zA-Z][.)])\s+", line):
            item = _re.sub(r"^(-|\*|\d+[.)]|[a-zA-Z][.)])\s+", "", line).strip()
            if item:
                items.append(item)
    
    # Deduplicate
    seen = set()
    cleaned = []
    for it in items:
        k = it.lower()
        if k in seen:
            continue
        seen.add(k)
        cleaned.append(it)
    
    # Create code slugs
    def slug(s: str) -> str:
        s = s.lower().strip()
        s = _re.sub(r"[^a-z0-9]+", "-", s).strip("-")
        return s[:40] or "option"
    
    return [{"label": it, "value": it, "code": slug(it)} for it in cleaned]
```

**Validation:**
- [ ] Test with sample BEGIN_OPTIONS/END_OPTIONS block
- [ ] Verify deduplication works
- [ ] Verify slug generation produces valid codes
- [ ] Run: `from app.screeners.registry import parse_screener_options; print(parse_screener_options("BEGIN_OPTIONS\n- Yes\n- No\nEND_OPTIONS"))`

---

### **Step 1.6: Wire Up the Infrastructure (CRITICAL)**

**File:** `backend/app/services/conversation_service.py`

**Location:** Find the main method that handles user messages and generates AI responses. This is typically something like `send_message()` or `process_message()`

**What to Do:**

1. **Find where the AI model's response is assembled** (search for where the LLM returns text)

2. **Add BEFORE saving/returning the response:**
   ```python
   # Enforce single question rule
   ai_response = enforce_single_question(ai_response)
   
   # Parse options if present
   options = parse_options_block(ai_response)
   ```

3. **Find where user messages are received** (beginning of the message handler)

4. **Add at the VERY START of the user message handler:**
   ```python
   # Check if user wants to finish
   if is_finish_message(user_message):
       session["is_finished"] = True
       # TODO: Call report generation function here
       # return generate_final_report(session)
       pass  # For now, add TODO comment
   ```

**IMPORTANT Notes:**
- Don't break existing flow - add these as enhancements
- If the code structure is different, add TODO comments showing where these should go
- Test that messages still flow correctly after adding these hooks

**Validation:**
- [ ] Send a test message - verify single question enforcement works
- [ ] Send ":finish" - verify it's detected (check logs)
- [ ] Verify options are parsed when present
- [ ] Ensure normal conversation flow isn't broken

---

### **Phase 1 Completion Checklist:**
- [ ] All 4 helper functions added to conversation_service.py
- [ ] C-SSRS helpers added
- [ ] Helper added to registry.py
- [ ] OPTIONS contract added to system prompt
- [ ] Infrastructure wired up (even if with TODO comments)
- [ ] All unit tests pass
- [ ] Manual test: Start conversation, verify messages work
- [ ] Manual test: Send ":finish", verify detection
- [ ] Manual test: See options in response, verify parsing works
- [ ] Git commit: "Phase 1: Add core infrastructure for options, finish, and enforcement"

---

## **PHASE 2: SAFETY CRITICAL ENHANCEMENTS (Days 4-5)**
**Goal:** Add safety protocols that prevent harm

### **Step 2.1: Enhance :finish Handler with Safety Check**

**File:** `backend/app/services/conversation_service.py`

**Location:** Where you added the `:finish` detection in Step 1.6

**What to Replace:**
Change the TODO from Step 1.6 to:

```python
# Check if user wants to finish
if is_finish_message(user_message):
    # SAFETY CHECK: Don't let high-risk patients finish without intervention
    cssrs_answers = session.get("cssrs_answers", {})
    
    if cssrs_risk_flag(cssrs_answers):
        # High risk detected - override finish, provide crisis resources
        crisis_response = crisis_message()
        crisis_response += "\n\nBefore we can complete the assessment, I need to make sure you're safe right now. Are you in a safe place?"
        
        session["requires_safety_check"] = True
        # Don't finish yet - return crisis message
        return {
            "message": crisis_response,
            "blocked_finish": True
        }
    
    # Safe to finish
    session["is_finished"] = True
    # TODO: Call actual report generation
    return {"message": "Generating your report...", "finished": True}
```

**Validation:**
- [ ] Create test session with high-risk C-SSRS answers
- [ ] Send ":finish" - verify it's blocked
- [ ] Verify crisis message is shown
- [ ] Create test session with low-risk answers
- [ ] Send ":finish" - verify it proceeds

---

### **Step 2.2: Add Real-Time C-SSRS Risk Detection**

**File:** `backend/app/services/conversation_service.py`

**Location:** After the C-SSRS helper functions

**What to Add:**

```python
def handle_cssrs_response(session_data: dict, question_number: int, answer: bool) -> dict:
    """
    Handle C-SSRS response with immediate intervention for high risk.
    
    Args:
        session_data: Current session
        question_number: Which C-SSRS question (1-6)
        answer: True (Yes) or False (No)
    
    Returns:
        Dict with {should_intervene, message, next_question}
    """
    # Store answer
    if "cssrs_answers" not in session_data:
        session_data["cssrs_answers"] = {}
    
    session_data["cssrs_answers"][f"Q{question_number}"] = answer
    
    # Get next question and risk status
    next_q, high_risk = cssrs_next_question(session_data["cssrs_answers"])
    
    # If HIGH RISK detected, immediate intervention
    if high_risk:
        session_data["cssrs_high_risk"] = True
        
        return {
            "should_intervene": True,
            "message": crisis_message() + "\n\nI'm pausing the assessment to make sure you get immediate support. Would you like me to help you create a safety plan?",
            "next_question": None,
            "requires_immediate_action": True
        }
    
    # Continue with next question or finish
    return {
        "should_intervene": False,
        "message": None,
        "next_question": next_q,
        "requires_immediate_action": False
    }
```

**Validation:**
- [ ] Test C-SSRS flow with Q1=Yes, Q2=Yes, Q4=Yes
- [ ] Verify intervention message appears
- [ ] Verify assessment pauses
- [ ] Test normal flow (all No answers) - verify no intervention

---

### **Step 2.3: Add Safety Check to System Prompt**

**File:** `backend/app/prompts/system_prompts.py`

**Location:** In the C-SSRS section (search for "C-SSRS")

**What to Add/Update:**

Find the C-SSRS instructions and add this CRITICAL section:

```
**🚨 CRITICAL: C-SSRS HIGH-RISK PROTOCOL 🚨**

If the patient answers "Yes" to Q4, Q5, or Q6 (intent, plan, or recent behavior):

1. **IMMEDIATELY stop the normal assessment flow**
2. **Present crisis resources** (988, Crisis Text Line, ER information)
3. **Do NOT continue with other screeners** until safety is addressed
4. **Ask about immediate safety:** "Are you in a safe place right now? Is there someone with you?"
5. **Offer safety planning:** "Would you like help creating a safety plan?"

**YOU MUST PAUSE ALL OTHER QUESTIONS UNTIL SAFETY IS ESTABLISHED.**

This overrides all other instructions. Patient safety is the absolute priority.
```

**Validation:**
- [ ] Read through the updated prompt
- [ ] Verify the HIGH-RISK protocol is clear and prominent
- [ ] Test with AI: provide high-risk C-SSRS answers, see if flow changes

---

### **Phase 2 Completion Checklist:**
- [ ] :finish blocked for high-risk patients
- [ ] Real-time C-SSRS risk detection added
- [ ] Safety protocol added to system prompt
- [ ] Manual test: Complete C-SSRS with high-risk answers, verify intervention
- [ ] Manual test: Try to :finish with high risk, verify blocked
- [ ] Manual test: Low-risk C-SSRS, verify normal flow continues
- [ ] Git commit: "Phase 2: Add critical safety protocols for high-risk patients"

---

## **PHASE 3: CLINICAL ENHANCEMENTS (Days 6-9)**
**Goal:** Add missing clinical components

### **Step 3.1: Add Mental Status Exam to System Prompt**

**File:** `backend/app/prompts/system_prompts.py`

**Location:** After "Symptom Exploration" section, before "Standardized Screeners"

**What to Add:**

```
3.5. **Mental Status Exam (MSE) - CRITICAL COMPONENT**
   After exploring chief complaint and main symptoms, conduct brief MSE:
   
   **A. Perceptual Screening (Hallucinations):**
   "Have you been seeing, hearing, or experiencing anything unusual that other people around you don't seem to notice?"
   
   If YES: "Can you describe what you're experiencing?"
   
   **B. Thought Organization:**
   "How would you describe your thinking lately?"
   
   BEGIN_OPTIONS
   - My thoughts are clear and organized
   - Sometimes my thoughts race or jump around
   - My thoughts feel disconnected or hard to follow
   - I'm not sure how to describe it
   END_OPTIONS
   
   **C. Orientation Check (Quick):**
   "Just to make sure I have your information correct - what's today's date?"
   
   **D. Memory (If cognitive concerns):**
   "Have you noticed any changes in your memory lately?"
   
   **CLINICAL NOTE:** The MSE helps distinguish between subjective symptoms and observable signs. It's essential for detecting psychosis, cognitive impairment, and thought disorders.
```

**Validation:**
- [ ] Read through the MSE section
- [ ] Verify it's placed logically in the flow
- [ ] Test conversation - verify MSE questions appear

---

### **Step 3.2: Add Medical Rule-Out Screening**

**File:** `backend/app/prompts/system_prompts.py`

**Location:** In the "History Gathering" section

**What to Add:**

```
6. **History Gathering**
   - Past psychiatric treatment
   - Medical conditions and current medications
   
   **🔬 MEDICAL RULE-OUTS (CRITICAL - Ask these specifically):**
   
   **Thyroid:**
   "Have you ever been told you have thyroid problems, or had abnormal thyroid blood tests?"
   
   **Vitamin Deficiencies:**
   "Have you had recent blood work? Were you told you're low in vitamins like B12, folate, or vitamin D?"
   
   **Head Injury/Neurological:**
   "Have you ever had a concussion, head injury, or been knocked unconscious?"
   
   **Hormonal (for women ages 18-55):**
   "Are your menstrual periods regular? Any hormonal conditions like PCOS or endometriosis?"
   
   **Recent Infections:**
   "Have you had COVID-19 or any other serious infections in the past 6 months?"
   
   **Current Medications:**
   "Are you taking any medications right now - prescription, over-the-counter, supplements, or herbal remedies?"
   
   **Caffeine/Nicotine:**
   "How much caffeine do you typically have per day? Do you use nicotine?"
   
   **WHY THIS MATTERS:** 15-20% of psychiatric symptoms are caused by medical conditions. These questions help identify medical causes that need treatment.
```

**Validation:**
- [ ] Medical screening questions added
- [ ] Questions are specific and actionable
- [ ] Test conversation - verify medical questions appear

---

### **Step 3.3: Add Progress Indicators**

**File:** `backend/app/services/conversation_service.py`

**Location:** After existing helper functions

**What to Add:**

```python
def generate_progress_update(session_data: dict) -> str:
    """
    Generate progress indicator showing where patient is in assessment.
    
    Returns:
        Progress message or empty string if not applicable
    """
    completed = session_data.get("completed_screeners", [])
    total = session_data.get("required_screeners", [])
    
    if not total:
        return ""
    
    completed_count = len(completed)
    total_count = len(total)
    
    if completed_count == 0:
        return ""  # Don't show progress before first screener
    
    percent = int((completed_count / total_count) * 100)
    remaining = total_count - completed_count
    
    return f"\n\n📊 **Progress:** {completed_count} of {total_count} assessments completed ({percent}%) - {remaining} remaining"


def should_offer_break(session_data: dict) -> bool:
    """
    Determine if we should offer a break.
    Offer after every 2 screeners.
    """
    completed = len(session_data.get("completed_screeners", []))
    
    # Offer break after 2nd, 4th, 6th screener, etc.
    if completed > 0 and completed % 2 == 0:
        # Check if we already offered a break at this point
        break_key = f"break_offered_after_{completed}"
        if not session_data.get(break_key):
            return True
    
    return False


def generate_break_offer() -> str:
    """Generate the break offer message with options."""
    return """
You're doing great! This is a lot of questions.

Would you like to take a short break (2-3 minutes) before we continue, or would you prefer to keep going?

BEGIN_OPTIONS
- Take a 2-minute break
- Continue with the next assessment
END_OPTIONS"""
```

**Validation:**
- [ ] Functions added successfully
- [ ] Test `generate_progress_update()` with various completion states
- [ ] Test `should_offer_break()` logic
- [ ] Verify break offers appear at right times

---

### **Step 3.4: Wire Up Progress Indicators**

**File:** `backend/app/services/conversation_service.py`

**Location:** Find where screeners complete and next screener starts

**What to Add:**

After a screener completes, before starting the next one:

```python
# After screener completion is detected
completed_screeners = session.get("completed_screeners", [])
required_screeners = session.get("required_screeners", [])

# Add progress update to response
progress_msg = generate_progress_update(session)
if progress_msg:
    ai_response += progress_msg

# Check if we should offer a break
if should_offer_break(session):
    break_offer = generate_break_offer()
    session[f"break_offered_after_{len(completed_screeners)}"] = True
    # Return break offer instead of next screener
    return break_offer
```

**Validation:**
- [ ] Complete 2 screeners, verify progress message appears
- [ ] Verify break offer appears after 2nd screener
- [ ] Test declining break - verify next screener starts
- [ ] Test accepting break - verify appropriate pause

---

### **Step 3.5: Add Severity-Adaptive Responses**

**File:** `backend/app/services/conversation_service.py`

**Location:** After screener scoring

**What to Add:**

```python
def get_severity_adaptive_response(screener_name: str, score: int, max_score: int, session_data: dict) -> str:
    """
    Generate follow-up based on screener severity.
    Severe cases get immediate deep questions; mild cases move on quickly.
    
    Args:
        screener_name: Name of completed screener
        score: Raw score
        max_score: Maximum possible score
        session_data: Current session
    
    Returns:
        Adaptive follow-up message
    """
    severity_percent = (score / max_score) * 100
    
    if screener_name == "PHQ-9":
        if severity_percent < 20:  # Minimal (0-4)
            return "Thank you for completing that assessment."
        
        elif severity_percent < 40:  # Mild (5-9)
            return "I can see you're experiencing some symptoms. Have you felt this way before?"
        
        elif severity_percent >= 70:  # Severe (20+)
            return """I can see you're really struggling right now, and I want to make sure we understand what's happening so we can get you the help you need.

Have you been hospitalized for mental health before?"""
    
    elif screener_name == "GAD-7":
        if severity_percent >= 70:  # Severe anxiety
            return "That level of anxiety must be really difficult. How is this affecting your daily life right now?"
    
    # Default: no special follow-up
    return ""
```

**Validation:**
- [ ] Test with high PHQ-9 score (20+), verify deeper questions
- [ ] Test with low PHQ-9 score (0-4), verify quick transition
- [ ] Test with high GAD-7, verify appropriate follow-up

---

### **Phase 3 Completion Checklist:**
- [ ] MSE questions added to system prompt
- [ ] Medical rule-outs added to system prompt
- [ ] Progress indicators implemented
- [ ] Break offers implemented
- [ ] Severity-adaptive responses implemented
- [ ] Manual test: Complete full assessment, verify MSE appears
- [ ] Manual test: Verify medical questions appear
- [ ] Manual test: See progress indicators
- [ ] Manual test: Receive break offer after 2 screeners
- [ ] Git commit: "Phase 3: Add clinical enhancements (MSE, medical screening, progress)"

---

## **PHASE 4: PROVIDER TOOLS (Days 10-12)**
**Goal:** Transform reports into decision-support tools

### **Step 4.1: Create Clinical Action Dashboard Generator**

**File:** `backend/app/services/report_service.py`

**Location:** Add new function near report generation

**What to Add:**

```python
def generate_clinical_action_dashboard(report_data: dict) -> str:
    """
    Generate the priority dashboard for top of clinician report.
    Shows immediate actions and critical flags.
    """
    # Determine urgency
    cssrs_risk = report_data.get("cssrs_risk_level", "none")
    phq9_score = report_data.get("phq9_score", 0)
    gad7_score = report_data.get("gad7_score", 0)
    
    # Set urgency level
    if cssrs_risk in ["high", "imminent"]:
        urgency = "EMERGENT"
        urgency_action = "Contact patient IMMEDIATELY - Active suicide risk"
    elif cssrs_risk == "moderate" or phq9_score >= 20:
        urgency = "URGENT"
        urgency_action = "Schedule within 24-48 hours - Severe symptoms"
    elif phq9_score >= 15 or gad7_score >= 15:
        urgency = "URGENT"
        urgency_action = "Schedule within 1 week - Moderate-severe symptoms"
    else:
        urgency = "ROUTINE"
        urgency_action = "Schedule within 1-2 weeks - Standard follow-up"
    
    # Collect critical flags
    flags = []
    if cssrs_risk != "none":
        flags.append(f"⚠️ Suicide Risk: {cssrs_risk.upper()} (C-SSRS)")
    if phq9_score >= 15:
        flags.append(f"⚠️ Severe Depression (PHQ-9: {phq9_score}/27)")
    if gad7_score >= 15:
        flags.append(f"⚠️ Severe Anxiety (GAD-7: {gad7_score}/21)")
    if report_data.get("prior_suicide_attempt"):
        flags.append(f"⚠️ Prior suicide attempt: {report_data.get('prior_attempt_details')}")
    
    flags_text = "\n║  ".join(flags) if flags else "None identified"
    
    # Generate recommended actions
    actions = generate_immediate_actions(report_data)
    actions_text = "\n║  ".join([f"{i+1}. {a}" for i, a in enumerate(actions)])
    
    # Build dashboard
    dashboard = f"""
╔══════════════════════════════════════════════════════════════╗
║  🚨 CLINICAL ACTION DASHBOARD                                 ║
╠══════════════════════════════════════════════════════════════╣
║  URGENCY: {urgency:<53}║
║  → {urgency_action:<57}║
║                                                               ║
║  CRITICAL RED FLAGS:                                          ║
║  {flags_text:<60}║
║                                                               ║
║  RECOMMENDED IMMEDIATE ACTIONS:                               ║
║  {actions_text:<60}║
║                                                               ║
║  TRIAGE LEVEL: {get_triage_level(report_data):<45}║
╚══════════════════════════════════════════════════════════════╝
"""
    
    return dashboard


def generate_immediate_actions(report_data: dict) -> list:
    """Generate list of immediate action recommendations."""
    actions = []
    
    cssrs_risk = report_data.get("cssrs_risk_level", "none")
    phq9_score = report_data.get("phq9_score", 0)
    
    # Safety actions
    if cssrs_risk in ["high", "imminent"]:
        actions.append("IMMEDIATE safety assessment and safety planning (PRIORITY)")
        actions.append("Consider same-day evaluation or ED referral")
        actions.append("Remove access to lethal means")
    elif cssrs_risk == "moderate":
        actions.append("Safety assessment and safety planning within 24 hours")
    
    # Treatment actions
    if phq9_score >= 15:
        actions.append("Initiate antidepressant therapy (consider SSRI)")
        actions.append("Refer for psychotherapy (CBT for depression)")
    
    # Lab work
    if phq9_score >= 10 or report_data.get("fatigue"):
        actions.append("Order labs: TSH, CBC, CMP, Vitamin D, B12")
    
    # Follow-up
    if cssrs_risk != "none":
        actions.append("Schedule close follow-up (within 1 week)")
    
    return actions[:5]  # Return top 5 actions


def get_triage_level(report_data: dict) -> str:
    """Determine triage level for scheduling priority."""
    cssrs_risk = report_data.get("cssrs_risk_level", "none")
    phq9_score = report_data.get("phq9_score", 0)
    
    if cssrs_risk in ["high", "imminent"]:
        return "Level 1 - Critical (Emergency)"
    elif cssrs_risk == "moderate" or phq9_score >= 20:
        return "Level 2 - High Acuity (Urgent)"
    elif phq9_score >= 10:
        return "Level 3 - Moderate Acuity"
    else:
        return "Level 4 - Standard"
```

**Validation:**
- [ ] Test with high-risk data, verify EMERGENT urgency
- [ ] Test with moderate data, verify URGENT urgency
- [ ] Verify flags appear correctly
- [ ] Verify actions are appropriate for severity

---

### **Step 4.2: Add Treatment Recommendations Section**

**File:** `backend/app/prompts/system_prompts.py` (in CLINICIAN_REPORT_GENERATION_PROMPT)

**Location:** In the clinician report structure, add a new section

**What to Add:**

```python
  "treatment_recommendations": "CONCISE ACTION PLAN:
    
    IMMEDIATE (24-48hr):
    • [Action #1]
    • [Action #2]
    
    PHARMACOTHERAPY:
    • 1st line: [Medication + dose] - [Brief rationale]
    • 2nd line: [Alternative if 1st fails/contraindicated]
    • Avoid: [Meds to avoid] - [Why]
    • Monitoring: [Labs/vitals needed]
    
    PSYCHOTHERAPY:
    • Modality: [CBT/DBT/IPT/etc] [frequency]
    • Rationale: [1 sentence - why this type]
    
    ADDITIONAL:
    • Labs: [Which and why]
    • Referrals: [To whom and why]
    
    FOLLOW-UP:
    • Timing: [Emergent/urgent/routine - be specific]
    • Frequency: [How often initially]
    • Monitor: [Specific symptoms or side effects]",
```

**Validation:**
- [ ] Generate a test report
- [ ] Verify treatment recommendations section appears
- [ ] Check that recommendations are specific and actionable

---

### **Step 4.3: Wire Up Dashboard to Report**

**File:** `backend/app/services/report_service.py`

**Location:** In the clinician report generation function

**What to Change:**

Find where the clinician report is assembled and add the dashboard at the very beginning:

```python
def generate_clinician_report(session_data: dict) -> dict:
    """Generate comprehensive clinician report."""
    
    # Generate dashboard first
    dashboard = generate_clinical_action_dashboard(session_data)
    
    # ... existing report generation ...
    
    # Add dashboard to the beginning of the report
    final_report = {
        "action_dashboard": dashboard,
        # ... rest of report sections ...
    }
    
    return final_report
```

**Validation:**
- [ ] Generate test report
- [ ] Verify dashboard appears at top
- [ ] Verify dashboard content is accurate
- [ ] Check formatting is preserved

---

### **Step 4.4: Add Strengths & Barriers Section**

**File:** `backend/app/prompts/system_prompts.py`

**Location:** Add to system prompt for collecting this data

**What to Add:**

```
**STRENGTHS & BARRIERS ASSESSMENT**
Before finishing, briefly assess:

**Strengths/Protective Factors:**
"What helps you cope when things are difficult?"
"Who can you turn to for support?"
"What motivates you to seek help right now?"

**Treatment Barriers:**
"Do you have health insurance?"
"Are medication costs a concern?"
"Do you have reliable transportation to appointments?"
"Does your work schedule make appointments difficult?"

**Patient Preferences:**
"Do you have a preference for therapy, medication, or both?"
"Have you had experiences with treatment that influence your preferences?"
```

**Then in clinician report structure, add:**

```python
  "strengths_and_barriers": "
    PROTECTIVE FACTORS:
    • [List specific strengths]
    • [Support system details]
    • [Motivation/insight]
    
    BARRIERS TO TREATMENT:
    • Financial: [Insurance status, cost concerns]
    • Logistical: [Transportation, scheduling]
    • Other: [Work, childcare, etc.]
    
    PATIENT PREFERENCES:
    • Treatment type: [Preference for therapy/meds/both]
    • Previous experiences: [What influences preferences]
    • Concerns: [Any treatment-specific concerns]",
```

**Validation:**
- [ ] Test conversation - verify strengths/barriers questions appear
- [ ] Generate report - verify section is populated
- [ ] Check that information is clinically useful

---

### **Phase 4 Completion Checklist:**
- [ ] Clinical Action Dashboard implemented
- [ ] Treatment recommendations section added
- [ ] Dashboard wired into report generation
- [ ] Strengths & barriers assessment added
- [ ] Manual test: Generate report, verify dashboard appears
- [ ] Manual test: Verify treatment recommendations are specific
- [ ] Manual test: Verify strengths/barriers section is populated
- [ ] Git commit: "Phase 4: Add provider decision-support tools to reports"

---

## **FINAL TESTING & VALIDATION (Day 12-13)**

### **Step 5.1: End-to-End Testing**

**Test Cases to Run:**

1. **Low-Risk Patient:**
   - [ ] Complete full assessment with mild symptoms
   - [ ] Verify normal flow
   - [ ] Check report generation
   - [ ] Verify routine urgency

2. **High-Risk Patient:**
   - [ ] Answer C-SSRS with high risk (Q4 or Q5 = Yes)
   - [ ] Verify crisis intervention appears
   - [ ] Verify `:finish` is blocked
   - [ ] Check report shows EMERGENT urgency

3. **Complex Case:**
   - [ ] Multiple symptoms (depression + anxiety + ADHD)
   - [ ] Complete all required screeners
   - [ ] Verify progress indicators
   - [ ] Accept break offer
   - [ ] Check comprehensive report

4. **Early Termination:**
   - [ ] Start assessment
   - [ ] Send `:finish` early
   - [ ] Verify report generation with partial data

5. **Options Parsing:**
   - [ ] Verify clickable options appear
   - [ ] Select options
   - [ ] Verify selections are recorded

### **Step 5.2: Performance Testing**

- [ ] Test with 30+ screeners (full battery)
- [ ] Verify no timeout issues
- [ ] Check memory usage
- [ ] Verify database writes are working

### **Step 5.3: Edge Cases**

- [ ] Empty/null responses
- [ ] Very long responses
- [ ] Special characters in responses
- [ ] Rapid-fire messages
- [ ] Multiple question marks in response (verify enforcement)

### **Step 5.4: Documentation**

- [ ] Update README with new features
- [ ] Document the `:finish` command
- [ ] Document safety protocols
- [ ] Add troubleshooting guide

---

## **ROLLBACK PROCEDURES**

If something breaks, rollback by phase:

**Phase 4 Rollback:**
```bash
git revert <phase-4-commit-hash>
```

**Phase 3 Rollback:**
```bash
git revert <phase-3-commit-hash>
```

**Phase 2 Rollback (CAREFUL - safety critical):**
```bash
git revert <phase-2-commit-hash>
# Then re-deploy Phase 1 immediately
```

**Phase 1 Rollback:**
```bash
git revert <phase-1-commit-hash>
# System returns to original state
```

---

## **DEPLOYMENT CHECKLIST**

Before deploying to production:

- [ ] All phases tested in staging
- [ ] All unit tests pass
- [ ] End-to-end tests pass
- [ ] Performance tests pass
- [ ] Documentation updated
- [ ] Backup current production database
- [ ] Deploy Phase 1 first, monitor for 24 hours
- [ ] Deploy Phase 2, monitor for 24 hours
- [ ] Deploy Phase 3, monitor for 48 hours
- [ ] Deploy Phase 4, monitor for 48 hours
- [ ] Monitor error logs daily for first week
- [ ] Collect feedback from first 10 provider users

---

## **SUCCESS METRICS**

Track these metrics post-implementation:

- [ ] Completion rate (% who finish assessment)
- [ ] Average time to complete
- [ ] C-SSRS high-risk detection rate
- [ ] :finish command usage
- [ ] Break offer acceptance rate
- [ ] Provider report review time
- [ ] Provider satisfaction with reports
- [ ] Time from assessment to treatment start

---

## **SUPPORT & TROUBLESHOOTING**

Common issues and solutions:

**Issue:** Options not parsing
- **Solution:** Check for BEGIN_OPTIONS/END_OPTIONS in AI response
- **Debug:** Print raw AI response, verify format

**Issue:** Single question enforcement not working
- **Solution:** Verify `enforce_single_question()` is called
- **Debug:** Add logging before/after enforcement

**Issue:** C-SSRS not detecting risk
- **Solution:** Check answer storage format
- **Debug:** Print `cssrs_answers` dict, verify Q4/Q5/Q6 values

**Issue:** :finish not detected
- **Solution:** Check message normalization
- **Debug:** Print normalized message, verify lowercase/strip

---

## **NOTES**

This implementation guide provides a complete, step-by-step path to implementing all improvements. Follow phases in order, test thoroughly after each phase, and maintain granular git commits for easy rollback if needed.

**Key Principles:**
- ✅ Safety first - Phase 2 is critical
- ✅ Test after each step
- ✅ Keep commits granular
- ✅ Document as you go
- ✅ Monitor closely after deployment

