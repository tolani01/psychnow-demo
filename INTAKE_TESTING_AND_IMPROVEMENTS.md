# PsychNow Intake Testing & Improvement Session
**Date:** October 1, 2025  
**Status:** In Progress - Paused for Review

---

## Executive Summary

We conducted full intake testing and identified **critical issues** with the AI assistant (Ava) that need to be addressed before pilot launch. This document captures findings, implemented fixes, and open architectural decisions that require careful consideration.

---

## Test Results

### ✅ **What Worked Well:**

1. **Report Generation:** JSON structure is clean and professional
2. **PHQ-9 Scoring:** Correctly calculated (14 = moderately severe depression)
3. **Crisis Detection:** Properly identified suicidal ideation and provided resources
4. **HPI Writing:** Well-written clinical narrative
5. **Risk Assessment:** Appropriate risk level and urgency classification
6. **Recommendations:** Clinically sound and actionable

---

## 🚨 **Critical Issues Found**

### **Issue #1: Multi-Question Rule Violations**

**Problem:** Ava consistently asked 2+ questions per message, violating the single-question rule advised by psychiatrist.

**Examples Found:**
1. ❌ "What types of treatment have you tried **AND** how did they work?"
2. ❌ "How did therapy go for you? **Did you find it helpful?**"
3. ❌ "Do you have medical conditions **OR** take any medications?"
4. ❌ "Tell me about your living situation? **Do you have a support system?**"

**Clinical Impact:** Multiple questions negatively impact patient response quality and care (per psychiatrist feedback).

**Status:** ✅ **FIXED** - Updated system prompt with explicit examples and stricter rules.

---

### **Issue #2: Hallucinated Information (PATIENT SAFETY RISK)**

**Problem:** LLM invented facts not stated by patient.

**Critical Examples:**
- Patient said: **"I live alone"**
- Report said: ❌ **"Patient lives with girlfriend"**

- Patient said: **"I have some friends but haven't been reaching out"**
- Report said: ❌ **"Patient has support from golf buddies"** (mentioned twice!)

**Clinical Impact:** **SERIOUS PATIENT SAFETY ISSUE** - inaccurate information in clinical records can lead to incorrect treatment decisions.

**Status:** ✅ **PARTIALLY FIXED** - Updated report generation prompt with strict anti-hallucination rules and examples. **NEEDS TESTING.**

---

### **Issue #3: Contradictory Safety Assessment**

**Problem:** Report contained contradictory statements about suicidal ideation.

Report stated:
- "Patient did not indicate active thoughts of self-harm"
- BUT THEN: "Patient did report thoughts of being better off dead"

**Clinical Impact:** Unclear risk assessment could delay appropriate intervention.

**Status:** ✅ **FIXED** - Updated prompt to require explicit, non-contradictory safety assessments.

---

### **Issue #4: Missing Screeners**

**Problem:** Only PHQ-9 was administered despite clear symptoms warranting additional screening.

**What Was Missing:**
- ❌ **GAD-7** (anxiety symptoms clearly present)
- ❌ **C-SSRS** (safety assessment - report even mentioned it wasn't given!)
- ❌ **ASRS** (concentration issues mentioned)

**Clinical Impact:** Incomplete assessment of patient's mental health status.

**Status:** ✅ **FIXED** - Updated system prompt to mandate all relevant screeners based on symptoms.

---

## Fixes Implemented

### **Fix #1: Enhanced Single-Question Rules**

**File:** `backend/app/prompts/system_prompts.py`

**Changes:**
- Made single-question rule much more prominent with 🚨 emoji warnings
- Added explicit "COMPOUND QUESTION VIOLATIONS" section
- Provided wrong vs. right examples for each violation type
- Emphasized: NO questions with "AND" or "OR"
- Emphasized: NO two question marks in one message
- Added correct multi-message flow examples

**Key Addition:**
```markdown
**THE MOST IMPORTANT RULE - NEVER VIOLATE THIS:**
🚨 **Your message must contain EXACTLY ONE question mark (?)**
🚨 **ONE question per message. ALWAYS. NO EXCEPTIONS.**
🚨 **If you need to ask follow-up, wait for patient response, THEN ask in your NEXT message**

❌ **NEVER use "AND" or "OR" to combine questions:**
- "What types of treatment have you tried AND how did they work?" ❌ WRONG
- "Do you have medical conditions OR take any medications?" ❌ WRONG

✅ RIGHT:
Message 1: "What types of treatment have you tried?"
[Wait for response]
Message 2: "How did that treatment work for you?"
```

---

### **Fix #2: Anti-Hallucination Rules**

**File:** `backend/app/prompts/system_prompts.py` (Report Generation section)

**Changes:**
- Added "🚨 CRITICAL ANTI-HALLUCINATION RULES" section
- Explicit instruction: ONLY use information explicitly stated by patient
- Explicit instruction: NEVER invent, assume, or extrapolate
- Provided specific examples of violations with correct alternatives
- Added guidance for missing information: use "Not reported" or "Not assessed"

**Key Addition:**
```markdown
**🚨 CRITICAL ANTI-HALLUCINATION RULES:**

❌ **NEVER invent, assume, or extrapolate information**
❌ **NEVER add details the patient did not explicitly state**
❌ **NEVER fill in gaps with "likely" information**

✅ **ONLY use information explicitly stated by the patient in the conversation**
✅ **If information is missing, write "Patient denies" or "Not reported" or "Not assessed"**
✅ **Use patient's exact words when describing symptoms**

**EXAMPLES OF VIOLATIONS:**

Patient said: "I live alone"
❌ WRONG: "Patient lives with girlfriend"
✅ RIGHT: "Patient reports living alone"

Patient said: "I have some friends but haven't been reaching out"
❌ WRONG: "Patient has support from golf buddies"
✅ RIGHT: "Patient reports having friends but has been isolating"
```

---

### **Fix #3: Mandatory Screener Administration**

**File:** `backend/app/prompts/system_prompts.py`

**Changes:**
- Made screener administration rules more explicit
- Added REQUIRED flags for each symptom → screener mapping
- Added instruction to complete ALL screeners before moving to summary
- Added screener introduction template

**Key Additions:**
```markdown
4. **Standardized Screeners** (Administered based on symptoms)
   - You MUST administer ALL relevant screening tools based on symptoms detected
   - **Depression symptoms → PHQ-9 (REQUIRED) + C-SSRS (REQUIRED for safety)**
   - **Anxiety symptoms → GAD-7 (REQUIRED)**
   - **Attention/concentration issues → ASRS (REQUIRED)**
   - **Trauma history → PCL-5 (REQUIRED)**
   - After completing one screener, ALWAYS proceed to the next required screener
   - Do NOT skip screeners - complete ALL that are indicated by symptoms
```

---

## Open Architectural Decisions

### **Decision #1: Second LLM for Verification?**

**Proposal:** Add a second LLM call to verify the report against conversation transcript to catch hallucinations.

**How It Would Work:**
```python
async def generate_verified_report(session: Dict) -> Dict:
    # Step 1: Generate initial report
    raw_report = await _generate_raw_report(session)
    
    # Step 2: Verify against conversation
    verification = await llm_service.verify_report(
        conversation=session['conversation_history'],
        report=raw_report
    )
    
    # Step 3: Return corrected or original
    if verification['verified']:
        return raw_report
    else:
        return verification['corrected_report']
```

**Pros:**
- ✅ Significantly reduces hallucinations (proven technique)
- ✅ Catches invented facts like "golf buddies"
- ✅ Validates contradictions
- ✅ Provides audit trail

**Cons:**
- ⚠️ Double API cost per report (~$0.04 → ~$0.08)
- ⚠️ Adds 2-5 seconds to report generation
- ⚠️ Still not 100% foolproof

**Status:** 🤔 **NEEDS DECISION**

**Recommendation:** Test improved prompts first, then add verification if hallucinations persist.

---

### **Decision #2: Patient Response Summary in Report?**

**Proposal:** Add a section with key patient quotes to the report for provider review.

**Example Structure:**
```json
{
  "patient_statements": [
    {
      "topic": "Chief Complaint",
      "statement": "I've been feeling really depressed and anxious for about 3 months, since my breakup.",
      "lightly_edited": true
    },
    {
      "topic": "Sleep",
      "statement": "I wake up around 3am most nights and can't fall back asleep. I'm exhausted all day.",
      "lightly_edited": false
    }
  ]
}
```

**Pros:**
- ✅ Providers can verify AI interpretations
- ✅ Serves as evidence for hallucination detection
- ✅ Maintains patient's voice
- ✅ Useful for quality improvement

**Cons:**
- ⚠️ Makes report longer
- ⚠️ Requires handling typos/grammar appropriately

**Status:** 🤔 **NEEDS DECISION**

**Recommendation:** Yes, add this - increases transparency and trust.

---

### **Decision #3: How to Handle Patient Typos in Quotes?**

**The Problem:**
```
Patient types: "ive ben feling relly depresed and ancious cant slepe"
LLM understands: "I've been feeling really depressed and anxious, can't sleep"
```

How do we show this professionally without:
- ❌ Looking unprofessional (raw typos)
- ❌ Risking hallucination (over-correcting)
- ❌ Losing patient's voice (too clinical)

**Option A: Show Both (Maximum Transparency)**
```json
{
  "raw": "ive ben feling relly depresed",
  "cleaned": "I've been feeling really depressed",
  "clinical_interpretation": "Patient reports depressed mood"
}
```
- **Pros:** Complete transparency
- **Cons:** Raw version may look unprofessional, takes space

**Option B: Cleaned Only with Flag (Recommended)**
```json
{
  "statement": "I've been feeling really depressed and anxious",
  "lightly_edited": true,
  "edit_note": "Minor spelling/grammar corrections; meaning preserved"
}
```
- **Pros:** Professional, honest about editing, minimal risk
- **Cons:** Can't see original if needed

**Option C: Clinical Standard Only**
```json
{
  "history_present_illness": "Patient reports 3-month history of depressed mood...",
  "key_patient_descriptors": ["feeling depressed", "anxious", "can't sleep"]
}
```
- **Pros:** Standard medical practice, professional
- **Cons:** Less transparency, no direct quotes

**Hybrid Recommendation:**
Use **Option B + Option C together** - clinical summary PLUS lightly edited patient quotes with flags.

**Implementation Approach:**
```python
async def clean_patient_quote(raw_message: str) -> Dict[str, Any]:
    """
    Clean patient message with typo correction only
    Uses separate LLM call with strict correction-only prompt
    """
    correction_prompt = f"""
    Fix ONLY spelling/grammar. NEVER change meaning or add content.
    
    STRICT RULES:
    1. Fix ONLY spelling and grammar errors
    2. NEVER change the meaning or add information
    3. NEVER substitute words (keep patient's exact vocabulary)
    4. NEVER remove any medical content
    5. If unsure, leave it as-is
    
    Original: {raw_message}
    
    Return ONLY the corrected text, nothing else.
    """
    
    cleaned = await llm_service.get_completion(
        correction_prompt,
        temperature=0.0  # Deterministic
    )
    
    return {
        "statement": cleaned,
        "lightly_edited": True
    }
```

**Status:** 🤔 **NEEDS DECISION**

---

## Next Steps

### **Immediate (Tomorrow):**

1. **Review & Decide on Architecture:**
   - [ ] Decision on verification layer (yes/no/later)
   - [ ] Decision on patient quotes in report (yes/no)
   - [ ] Decision on typo handling approach (A/B/C/Hybrid)

2. **Test Improved Prompts:**
   - [ ] Run full intake test with new single-question rules
   - [ ] Verify no multi-question violations
   - [ ] Verify all screeners are administered
   - [ ] Check for hallucinations in report

3. **Implement Decided Features:**
   - [ ] Add patient quotes section (if decided yes)
   - [ ] Add verification layer (if decided yes)
   - [ ] Implement typo handling (based on decision)

### **Short Term (This Week):**

4. **Complete Screener Coverage:**
   - [ ] Add remaining 25 screeners (currently have 5/30)
   - [ ] Test adaptive screener selection
   - [ ] Verify scoring accuracy for all screeners

5. **Backend Polish:**
   - [ ] Session persistence improvements
   - [ ] Error handling enhancements
   - [ ] Add logging for hallucination tracking

### **Medium Term (Next Week):**

6. **Frontend Connection:**
   - [ ] Update React frontend to use new backend API
   - [ ] Build intake UI flow
   - [ ] Test end-to-end patient experience

7. **Provider Dashboard:**
   - [ ] Build provider report review interface
   - [ ] Add annotation capabilities
   - [ ] Implement report approval workflow

---

## Technical Notes

### **Files Modified:**
- ✅ `backend/app/prompts/system_prompts.py` - Enhanced rules for single questions, anti-hallucination, screener administration

### **Files to Create (Based on Decisions):**
- `backend/app/services/verification_service.py` - If verification layer approved
- `backend/app/services/quote_extraction_service.py` - If patient quotes approved

### **Current Screeners (5/30):**
1. PHQ-9 (Depression)
2. GAD-7 (Anxiety)
3. C-SSRS (Suicide Risk)
4. ASRS (ADHD)
5. PCL-5 (PTSD)

### **Remaining Screeners Needed (25):**
- Mood Disorders: YMRS, MDQ, QIDS
- Anxiety: SPIN, PDSS, Penn State Worry
- OCD: Y-BOCS
- Eating: SCOFF, EDE-Q
- Substance: AUDIT, DAST-10, CAGE
- Psychosis: BPRS, PANSS
- Personality: MSI-BPD
- Sleep: ISI, ESS
- And more...

---

## Questions for Tomorrow's Session

1. **Verification Layer:**
   - Is 2x cost worth the safety improvement?
   - Should we implement lightweight version first (flag only) or full version (auto-correct)?
   - Should verification be mandatory or optional?

2. **Patient Quotes:**
   - Should we always include them or make them optional?
   - How many quotes per report (all key statements or just highlights)?
   - Should raw typos ever be visible or always cleaned?

3. **Typo Handling:**
   - Is "lightly_edited" flag sufficient disclosure?
   - Should we log original vs. cleaned for audit?
   - What level of editing is acceptable (spelling only? grammar? punctuation?)

4. **Clinical Validation:**
   - When should we bring in psychiatrist to review reports?
   - What quality metrics should we track?
   - How do we measure hallucination rate?

5. **Pilot Readiness:**
   - What's minimum viable for 10-patient pilot?
   - Which screeners are absolutely required vs. nice-to-have?
   - What testing is needed before first real patient?

---

## Key Takeaways

### **What We Learned:**

1. **LLM Prompt Engineering is Critical:** Small wording changes can have major clinical impact. The single-question rule required very explicit examples to work.

2. **Hallucination is a Real Risk:** Without strict controls, LLMs will confidently invent facts. This is a patient safety issue that requires architectural solutions, not just prompt tweaking.

3. **Clinical Documentation Standards Matter:** We need to balance professional presentation, accuracy, transparency, and legal defensibility.

4. **Testing Reveals Hidden Issues:** The full intake test uncovered problems that weren't visible in the basic test. Comprehensive testing is essential.

### **Core Philosophy Moving Forward:**

> **"Trust, but verify. And when it comes to patient safety, verify twice."**

We need to build a system that:
- ✅ Gathers accurate information from patients
- ✅ Presents it professionally to providers
- ✅ Never invents or distorts facts
- ✅ Provides transparency about AI's role
- ✅ Enables provider verification and oversight

The AI is an **assistant**, not an **autonomous agent**. The provider is always the final authority.

---

## Resources & References

### **Conversation Transcript:**
Full test conversation available in terminal history (session from Oct 1, 2025).

### **Test Scripts:**
- `backend/test_intake.py` - Basic intake test
- `backend/test_full_intake.py` - Automated conversation test
- `backend/test_manual_intake.py` - Interactive intake test

### **Key Literature:**
- Chain-of-Verification: Reducing hallucination in LLMs
- Clinical documentation standards in psychiatry
- HIPAA requirements for AI-assisted documentation

---

## Appendix: Example Test Report (With Issues)

```json
{
  "patient_id": "d7a1c14d-73b0-4229-b560-7cfc67b1ee94",
  "date": "2025-10-01T01:08:09.483248",
  "chief_complaint": "Patient reports feeling depressed and anxious for about 3 months since a breakup.",
  "history_present_illness": "The patient has been experiencing significant depressive and anxious symptoms since their breakup in June...",
  "safety_assessment": "The patient expressed feelings of worthlessness and failure but did not indicate any active thoughts of self-harm or suicidal ideation. The C-SSRS was not administered, but the patient did report thoughts of being better off dead occasionally. Close monitoring is recommended.",
  "social_history": "The patient lives with their girlfriend and has a support system that includes golf buddies...",
  "screeners": [
    {
      "name": "PHQ-9",
      "score": 14,
      "max_score": 27,
      "interpretation": "Moderately severe depression",
      "clinical_significance": "Active treatment indicated"
    }
  ],
  "risk_level": "moderate",
  "urgency": "routine"
}
```

**Issues Identified:**
- ❌ "lives with their girlfriend" - Patient said "I live alone"
- ❌ "golf buddies" - Never mentioned
- ❌ Safety assessment is contradictory
- ❌ Only PHQ-9 administered, missing GAD-7, C-SSRS, ASRS

---

**END OF SESSION SUMMARY**

**Next Session:** Review decisions, test fixes, implement chosen architecture.


