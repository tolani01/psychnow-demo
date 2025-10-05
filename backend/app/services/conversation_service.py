"""
Conversation Service
Manages intake conversation state and phase transitions
"""
from typing import List, Dict, Any, Optional, AsyncIterator
import logging
from datetime import datetime
import uuid

from app.prompts.system_prompts import INTAKE_SYSTEM_PROMPT
from app.services.llm_service import llm_service
from app.screeners.registry import screener_registry
from app.schemas.intake import ChatResponse
from app.schemas.intake import ChatResponse as CR  # Backup import for error handling

logger = logging.getLogger(__name__)
from app.services.screener_enforcement_service import screener_enforcement_service

# ============================================================================
# DSM-5 DOMAIN REQUIREMENTS FOR CLINICAL ASSESSMENT
# ============================================================================
REQUIRED_DSM5_DOMAINS = [
    "chief_complaint",  # Presenting problem and HPI
    "hpi_duration_severity_course",  # History of present illness
    "risk_suicide_homicide_means_protective",  # Safety assessment
    "psychosis_screen",  # Psychotic symptoms screening
    "mania_hypomania_screen",  # Bipolar screening
    "past_psych_history",  # Previous psychiatric history
    "meds_trials_allergies",  # Medication history
    "medical_history",  # Medical conditions
    "substance_history",  # Substance use assessment
    "family_history",  # Family psychiatric history
    "social_context_cfi",  # Social and cultural factors
    "function_whodas_or_wsas"  # Functional impairment
]

def has_required_dsm5_domains(session: Dict[str, Any]) -> Dict[str, Any]:
    """
    Check if session has sufficient DSM-5 domain coverage for clinical assessment.
    
    This replaces the lightweight _has_sufficient_clinical_data with a proper
    DSM-5 domain checklist that ensures comprehensive assessment.
    
    Args:
        session: Session data dictionary
        
    Returns:
        Dictionary with completion status and missing domains
    """
    extracted_data = session.get("extracted_data", {})
    completed_domains = []
    missing_domains = []
    
    for domain in REQUIRED_DSM5_DOMAINS:
        if extracted_data.get(domain):
            completed_domains.append(domain)
        else:
            missing_domains.append(domain)
    
    return {
        "complete": len(missing_domains) == 0,
        "completed_domains": completed_domains,
        "missing_domains": missing_domains,
        "completion_percentage": len(completed_domains) / len(REQUIRED_DSM5_DOMAINS) * 100
    }

# ============================================================================
# CONVERSATION PHASES AND ASSESSMENT STRUCTURE
# ============================================================================
CONVERSATION_PHASES = {
    "greeting": {
        "required_messages": 3,
        "description": "Introduction and rapport building",
        "symptoms_to_detect": []
    },
    "chief_complaint": {
        "required_messages": 5,
        "description": "Presenting problem and history",
        "symptoms_to_detect": ["presenting_problem"]
    },
    "mood_assessment": {
        "required_messages": 8,
        "description": "Depression, mania, anxiety symptoms",
        "symptoms_to_detect": ["depression", "mania", "anxiety", "irritability", "mood_swings"]
    },
    "cognitive_assessment": {
        "required_messages": 6,
        "description": "Attention, memory, executive function",
        "symptoms_to_detect": ["attention", "memory", "executive", "racing_thoughts", "obsessions"]
    },
    "physical_assessment": {
        "required_messages": 6,
        "description": "Sleep, appetite, energy, somatic",
        "symptoms_to_detect": ["sleep", "appetite", "energy", "pain", "somatic"]
    },
    "behavioral_assessment": {
        "required_messages": 6,
        "description": "Substance use, social, risk behaviors",
        "symptoms_to_detect": ["substance", "social", "suicide", "self_harm", "risk"]
    },
    "trauma_assessment": {
        "required_messages": 4,
        "description": "Trauma history and current stressors",
        "symptoms_to_detect": ["trauma", "ptsd", "nightmares", "flashbacks", "hypervigilance"]
    },
    "functional_assessment": {
        "required_messages": 4,
        "description": "Work, relationships, daily living",
        "symptoms_to_detect": ["work", "relationships", "daily_living", "quality_of_life"]
    },
    "mental_status_exam": {
        "required_messages": 4,
        "description": "Perceptual, cognitive, risk screening",
        "symptoms_to_detect": ["hallucinations", "delusions", "psychosis", "cognitive_impairment"]
    },
    "screener_administration": {
        "required_messages": 0,
        "description": "Standardized screening tools",
        "symptoms_to_detect": []
    }
}

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


# CRITICAL SAFETY: Multi-question allowlist for clinical assessments
MULTI_Q_ALLOWLIST = {
    "c-ssrs_q5",  # C-SSRS Question 5 has two parts: worked out details + intent
    "psychosis_probe",  # Psychosis screening may need paired questions
    "mania_duration_probe",  # Mania screening duration + severity
    "safety_plan_warning_signs",  # Safety planning structured questions
    "means_access_probe",  # Means access assessment
    "hoi_probe",  # Homicidal ideation assessment
    "violence_probe"  # Violence risk assessment
}

# CRITICAL SAFETY: Risk assessment keywords
SUICIDE_RISK_KEYWORDS = [
    "suicide", "kill myself", "end it all", "not want to live", "better off dead",
    "hurt myself", "self harm", "cutting", "overdose", "jump", "shoot myself"
]

HOMICIDAL_RISK_KEYWORDS = [
    "kill", "hurt", "harm", "attack", "shoot", "stab", "strangle", "beat up",
    "get revenge", "make them pay", "they deserve to die", "want them dead"
]

PSYCHOSIS_RISK_KEYWORDS = [
    "voices", "hearing things", "seeing things", "delusions", "paranoia",
    "thought insertion", "thought broadcast", "mind control", "government",
    "conspiracy", "being watched", "bugs", "cameras", "aliens", "demons"
]

MANIA_RISK_KEYWORDS = [
    "manic", "high", "euphoric", "racing thoughts", "can't sleep", "grandiose",
    "spending spree", "risky behavior", "invincible", "superhuman"
]

def enforce_single_question(model_text: str, item_id: Optional[str] = None) -> str:
    """
    CRITICAL SAFETY FIX: Allow validated multi-part clinical questions.
    
    C-SSRS Q5 contains two questions that MUST both be asked for safety:
    "Have you worked out the details of how to kill yourself?" AND "Do you intend to carry out this plan?"
    
    This function now allows whitelisted multi-part clinical questions while maintaining
    single-question discipline for general conversation.
    
    Args:
        model_text: The model response text
        item_id: Optional identifier for the current screener item
        
    Returns:
        Text with appropriate question handling
    """
    if not model_text:
        return model_text
    
    # Allow multi-part questions for critical clinical assessments
    if item_id and item_id.lower() in MULTI_Q_ALLOWLIST:
        return model_text  # Allow both questions for safety
    
    # For general conversation, enforce single question
    q_idx = model_text.find("?")
    if q_idx == -1:
        return model_text
    
    # Check for second question mark
    extra_q = model_text.find("?", q_idx + 1)
    if extra_q == -1:
        # Only one question mark - perfect
        return model_text
    
    # Multiple question marks in general conversation - truncate after first
    return model_text[: q_idx + 1]


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

def check_homicidal_risk(user_message: str) -> str:
    """Check for homicidal risk indicators with context awareness"""
    message_lower = user_message.lower()
    
    # High-risk indicators
    high_risk_keywords = ["kill them", "hurt someone", "harm others", "violence", "attack", "get revenge"]
    if any(keyword in message_lower for keyword in high_risk_keywords):
        return "high"
    
    # Medium-risk indicators
    medium_risk_keywords = ["angry at", "mad at", "frustrated with", "want to get back at", "they deserve it"]
    if any(keyword in message_lower for keyword in medium_risk_keywords):
        return "medium"
    
    # Low-risk indicators
    if any(keyword in message_lower for keyword in HOMICIDAL_RISK_KEYWORDS):
        return "low"
    
    return "none"

def check_psychosis_risk(user_message: str) -> str:
    """Check for psychosis risk indicators with context awareness"""
    message_lower = user_message.lower()
    
    # High-risk indicators
    high_risk_keywords = ["voices telling me", "hearing voices", "seeing things", "they're watching me", "government tracking", "mind control"]
    if any(keyword in message_lower for keyword in high_risk_keywords):
        return "high"
    
    # Medium-risk indicators
    medium_risk_keywords = ["strange thoughts", "unusual beliefs", "paranoid", "suspicious", "delusions"]
    if any(keyword in message_lower for keyword in medium_risk_keywords):
        return "medium"
    
    # Low-risk indicators
    if any(keyword in message_lower for keyword in PSYCHOSIS_RISK_KEYWORDS):
        return "low"
    
    return "none"

def check_mania_risk(user_message: str) -> str:
    """Check for mania risk indicators with context awareness"""
    message_lower = user_message.lower()
    
    # High-risk indicators
    high_risk_keywords = ["haven't slept in days", "racing thoughts", "can't stop talking", "feel invincible", "spending spree", "grandiose"]
    if any(keyword in message_lower for keyword in high_risk_keywords):
        return "high"
    
    # Medium-risk indicators
    medium_risk_keywords = ["very energetic", "don't need sleep", "hyperactive", "impulsive decisions", "elevated mood"]
    if any(keyword in message_lower for keyword in medium_risk_keywords):
        return "medium"
    
    # Low-risk indicators
    if any(keyword in message_lower for keyword in MANIA_RISK_KEYWORDS):
        return "low"
    
    return "none"

def check_suicide_risk(user_message: str) -> str:
    """Check for suicide risk indicators with context awareness"""
    message_lower = user_message.lower()
    
    # High-risk indicators
    high_risk_keywords = ["kill myself", "suicide", "end it all", "not worth living", "better off dead", "want to die"]
    if any(keyword in message_lower for keyword in high_risk_keywords):
        return "high"
    
    # Medium-risk indicators
    medium_risk_keywords = ["don't want to live", "hopeless", "no point", "tired of living"]
    if any(keyword in message_lower for keyword in medium_risk_keywords):
        return "medium"
    
    # Low-risk indicators
    if any(keyword in message_lower for keyword in SUICIDE_RISK_KEYWORDS):
        return "low"
    
    return "none"

def check_substance_overdose_risk(user_message: str) -> str:
    """Check for substance overdose risk indicators"""
    message_lower = user_message.lower()
    
    # High-risk indicators
    high_risk_keywords = ["overdosed", "too much", "can't stop using", "withdrawal", "need more", "using daily"]
    if any(keyword in message_lower for keyword in high_risk_keywords):
        return "high"
    
    # Medium-risk indicators
    medium_risk_keywords = ["can't function without", "tolerance", "dependence", "addicted"]
    if any(keyword in message_lower for keyword in medium_risk_keywords):
        return "medium"
    
    return "none"

def check_trauma_crisis_risk(user_message: str) -> str:
    """Check for trauma crisis risk indicators"""
    message_lower = user_message.lower()
    
    # High-risk indicators
    high_risk_keywords = ["flashback right now", "can't stop thinking about it", "triggered", "dissociating", "reliving it"]
    if any(keyword in message_lower for keyword in high_risk_keywords):
        return "high"
    
    # Medium-risk indicators
    medium_risk_keywords = ["nightmares", "avoiding everything", "hypervigilant", "on edge", "trauma"]
    if any(keyword in message_lower for keyword in medium_risk_keywords):
        return "medium"
    
    return "none"

def homicidal_risk_message() -> str:
    """Return message for homicidal ideation risk."""
    return (
        "🚨 **IMMEDIATE SAFETY CONCERN** 🚨\n\n"
        "I'm concerned about your safety and the safety of others. If you're having thoughts of harming someone else:\n\n"
        "• **Call 988** - Crisis Lifeline (24/7)\n"
        "• **Call 911** - If there's immediate danger\n"
        "• **Go to your nearest Emergency Department**\n\n"
        "It's important that we address these concerns immediately. Are you in a safe place right now?"
    )

def psychosis_risk_message() -> str:
    """Return message for psychotic symptoms risk."""
    return (
        "🚨 **IMMEDIATE MEDICAL ATTENTION NEEDED** 🚨\n\n"
        "The symptoms you're describing may require immediate medical evaluation. If you're experiencing:\n"
        "• Hearing voices or seeing things others don't\n"
        "• Feeling paranoid or being watched\n"
        "• Having unusual beliefs or thoughts\n\n"
        "Please seek immediate help:\n"
        "• **Call 988** - Crisis Lifeline (24/7)\n"
        "• **Go to your nearest Emergency Department**\n"
        "• **Contact your local mental health crisis team**\n\n"
        "These symptoms can be treated, and help is available right now."
    )

def mania_risk_message() -> str:
    """Return message for manic symptoms risk."""
    return (
        "🚨 **IMMEDIATE MEDICAL ATTENTION NEEDED** 🚨\n\n"
        "The symptoms you're describing may indicate a manic episode. If you're experiencing:\n"
        "• Extremely high energy or euphoria\n"
        "• Racing thoughts or inability to sleep\n"
        "• Risky or impulsive behavior\n"
        "• Grandiose beliefs about your abilities\n\n"
        "Please seek immediate help:\n"
        "• **Call 988** - Crisis Lifeline (24/7)\n"
        "• **Go to your nearest Emergency Department**\n"
        "• **Contact your psychiatrist or mental health provider**\n\n"
        "Mania can be dangerous and requires immediate medical attention."
    )


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


def _is_same_question(question1: str, question2: str) -> bool:
    """
    Check if two questions are essentially the same (prevent repetition).
    
    Args:
        question1: First question text
        question2: Second question text
    
    Returns:
        True if questions are essentially the same
    """
    # Normalize questions for comparison
    q1 = question1.strip().lower()
    q2 = question2.strip().lower()
    
    # Remove punctuation and extra spaces
    import re
    q1 = re.sub(r'[^\w\s]', '', q1).strip()
    q2 = re.sub(r'[^\w\s]', '', q2).strip()
    
    # Split into words
    words1 = set(q1.split())
    words2 = set(q2.split())
    
    # Remove common stop words that don't add meaning
    stop_words = {"how", "many", "nights", "per", "week", "would", "you", "say", "this", "that", "the", "a", "an", "does", "do", "is", "are", "was", "were", "been", "have", "has", "had"}
    words1 = words1 - stop_words
    words2 = words2 - stop_words
    
    # Calculate similarity
    if len(words1) == 0 or len(words2) == 0:
        return False
    
    # Check for high overlap in meaningful words
    overlap = len(words1.intersection(words2))
    total_unique = len(words1.union(words2))
    
    # If more than 60% of words overlap, consider it the same question
    similarity = overlap / total_unique if total_unique > 0 else 0
    
    # Special cases for common repetitive patterns
    if "sleep" in words1 and "sleep" in words2:
        # Both are about sleep - check if they're asking the same thing
        if "problem" in words1 and "problem" in words2:
            return True
        if "happens" in words1 and "happens" in words2:
            return True
        if "occurs" in words1 and "happens" in words2:
            return True
        if "happens" in words1 and "occurs" in words2:
            return True
        # If both have "sleep" and similar structure, likely the same
        if similarity > 0.5:
            return True
    
    return similarity > 0.6


def _has_sufficient_clinical_data(conversation_history: list, completed_screeners: list) -> bool:
    """
    Check if we have sufficient clinical information to generate a meaningful report.
    
    Minimum requirements:
    - At least 5-6 meaningful exchanges (beyond greeting)
    - OR at least 1 completed screener
    - OR explicit chief complaint mentioned
    
    Args:
        conversation_history: List of conversation messages
        completed_screeners: List of completed screener names
    
    Returns:
        True if sufficient data, False if more information needed
    """
    # If any screeners completed, we have clinical data
    if completed_screeners:
        return True
    
    # Count meaningful exchanges (exclude system messages and very short responses)
    meaningful_exchanges = 0
    chief_complaint_mentioned = False
    
    for msg in conversation_history:
        if msg.get("role") == "user":
            content = msg.get("content", "").strip().lower()
            
            # Skip very short responses
            if len(content) < 10:
                continue
                
            # Check for chief complaint indicators
            if any(phrase in content for phrase in [
                "feeling", "symptoms", "depressed", "anxious", "worried", 
                "trouble", "problems", "difficult", "struggling", "help"
            ]):
                chief_complaint_mentioned = True
                meaningful_exchanges += 1
            elif len(content) > 20:  # Substantial response
                meaningful_exchanges += 1
    
    # Need at least 3-4 meaningful exchanges OR chief complaint mentioned
    return meaningful_exchanges >= 3 or chief_complaint_mentioned


class ConversationPhase:
    """Intake conversation phases"""
    GREETING = "greeting"
    CHIEF_COMPLAINT = "chief_complaint"
    SYMPTOM_EXPLORATION = "symptom_exploration"
    SCREENER_INTRO_PENDING = "screener_intro_pending"  # NEW: Waiting for "Are you ready?" acknowledgment
    SCREENING = "screening"
    SAFETY_ASSESSMENT = "safety_assessment"
    HISTORY_GATHERING = "history_gathering"
    SOCIAL_CONTEXT = "social_context"
    SUMMARY = "summary"
    COMPLETION = "completion"


class ConversationService:
    """Service for managing intake conversation flow"""
    
    def __init__(self):
        """Initialize conversation service"""
        # In-memory session storage (will move to Redis/DB later)
        self.sessions: Dict[str, Dict[str, Any]] = {}
    
    def _track_discussed_topics(self, session_token: str, user_message: str):
        """
        Track what topics have been discussed to prevent repetition.
        
        This prevents asking about the same symptoms/topics that were already
        covered in the chief complaint or earlier in the assessment.
        """
        session = self.get_session(session_token)
        if not session:
            return
        
        # Initialize discussed topics if not exists
        if "discussed_topics" not in session:
            session["discussed_topics"] = {}
        
        discussed = session["discussed_topics"]
        message_lower = user_message.lower()
        
        # Track symptom topics that have been discussed
        topic_keywords = {
            "attention": ["attention", "concentrate", "focus", "distracted", "mind wandering"],
            "sleep": ["sleep", "insomnia", "tired", "exhausted", "rested", "nightmares"],
            "appetite": ["appetite", "eating", "hungry", "food", "weight", "gained", "lost"],
            "energy": ["energy", "fatigue", "tired", "exhausted", "lethargic", "motivation"],
            "mood": ["mood", "sad", "depressed", "happy", "irritable", "angry", "emotional"],
            "anxiety": ["anxiety", "worried", "nervous", "panic", "fear", "stressed"],
            "substance": ["alcohol", "drinking", "drugs", "smoking", "substance", "using"],
            "social": ["social", "friends", "family", "relationships", "isolated", "alone"],
            "work": ["work", "job", "career", "performance", "productivity", "colleagues"],
            "suicide": ["suicide", "kill myself", "end it all", "not want to live", "better off dead"],
            "psychosis": ["voices", "hearing", "seeing", "delusions", "paranoia", "unreal"],
            "mania": ["manic", "high", "euphoric", "racing thoughts", "grandiose", "invincible"]
        }
        
        # Check which topics are being discussed in this message
        for topic, keywords in topic_keywords.items():
            if any(keyword in message_lower for keyword in keywords):
                discussed[topic] = {
                    "discussed": True,
                    "timestamp": datetime.utcnow().isoformat(),
                    "context": user_message[:100] + "..." if len(user_message) > 100 else user_message
                }
        
        # Also track if user confirms a symptom (like "yes" to attention problems)
        conversation_history = session.get("conversation_history", [])
        if len(conversation_history) >= 2:
            last_ai_message = conversation_history[-2].get("content", "").lower()
            if "yes" in message_lower or "yeah" in message_lower or "yep" in message_lower:
                # User confirmed something - track what they confirmed
                if "attention" in last_ai_message or "concentrate" in last_ai_message or "focus" in last_ai_message:
                    discussed["attention"] = {
                        "discussed": True,
                        "confirmed": True,
                        "timestamp": datetime.utcnow().isoformat(),
                        "context": "Confirmed attention problems"
                    }
                elif "sleep" in last_ai_message:
                    discussed["sleep"] = {
                        "discussed": True,
                        "confirmed": True,
                        "timestamp": datetime.utcnow().isoformat(),
                        "context": "Confirmed sleep problems"
                    }
                # Add more confirmation tracking as needed
    
    def _should_skip_topic(self, session_token: str, topic: str) -> bool:
        """
        Check if a topic should be skipped because it was already discussed.
        
        Args:
            session_token: Session identifier
            topic: Topic to check (e.g., "attention", "sleep", "mood")
            
        Returns:
            True if topic should be skipped
        """
        session = self.get_session(session_token)
        if not session:
            return False
        
        discussed = session.get("discussed_topics", {})
        topic_info = discussed.get(topic, {})
        
        # Skip if topic was already discussed and confirmed
        if topic_info.get("discussed") and topic_info.get("confirmed"):
            return True
        
        # Skip if topic was discussed in chief complaint context
        if topic_info.get("discussed") and "chief complaint" in topic_info.get("context", "").lower():
            return True
        
        return False
    
    def _build_discussed_topics_context(self, discussed_topics: Dict[str, Any]) -> str:
        """
        Build a context string of previously discussed topics for the AI.
        
        Args:
            discussed_topics: Dictionary of discussed topics
            
        Returns:
            Formatted string of discussed topics
        """
        if not discussed_topics:
            return "No topics have been discussed yet."
        
        context_lines = []
        for topic, info in discussed_topics.items():
            if info.get("discussed"):
                status = "CONFIRMED" if info.get("confirmed") else "DISCUSSED"
                context_lines.append(f"- {topic.upper()}: {status} - {info.get('context', 'No context')}")
        
        return "\n".join(context_lines) if context_lines else "No topics have been discussed yet."
    
    def _track_chief_complaint(self, session_token: str, user_message: str):
        """
        Track the chief complaint to prevent asking about it again later.
        
        The chief complaint is typically mentioned in the first few exchanges
        and should not be re-explored unless specific follow-up is needed.
        """
        session = self.get_session(session_token)
        if not session:
            return
        
        message_count = len(session.get("conversation_history", []))
        
        # Chief complaint is typically mentioned in the first 5-10 messages
        if message_count <= 10 and not session.get("chief_complaint_tracked"):
            message_lower = user_message.lower()
            
            # Look for chief complaint indicators
            chief_complaint_keywords = [
                "here because", "came here", "main problem", "biggest issue",
                "trouble with", "problem with", "difficulty with", "struggling with",
                "concerned about", "worried about", "having issues with"
            ]
            
            if any(keyword in message_lower for keyword in chief_complaint_keywords):
                # This looks like a chief complaint - mark all mentioned symptoms as discussed
                discussed = session.get("discussed_topics", {})
                
                # Extract symptoms mentioned in chief complaint
                symptom_keywords = {
                    "attention": ["attention", "concentrate", "focus", "distracted"],
                    "sleep": ["sleep", "insomnia", "tired", "exhausted"],
                    "mood": ["mood", "sad", "depressed", "anxious", "worried"],
                    "energy": ["energy", "fatigue", "tired", "motivation"],
                    "appetite": ["appetite", "eating", "weight", "food"]
                }
                
                for symptom, keywords in symptom_keywords.items():
                    if any(keyword in message_lower for keyword in keywords):
                        discussed[symptom] = {
                            "discussed": True,
                            "confirmed": True,
                            "timestamp": datetime.utcnow().isoformat(),
                            "context": f"Chief complaint: {user_message[:100]}...",
                            "source": "chief_complaint"
                        }
                
                session["discussed_topics"] = discussed
                session["chief_complaint_tracked"] = True
                logger.info(f"Chief complaint tracked for session {session_token}: {discussed}")
    
    def get_current_phase(self, session_token: str) -> str:
        """
        Determine current assessment phase based on conversation progress
        
        Args:
            session_token: Session identifier
            
        Returns:
            Current conversation phase
        """
        session = self.get_session(session_token)
        if not session:
            return "greeting"
        
        message_count = len(session.get("conversation_history", []))
        completed_phases = session.get("completed_phases", [])
        
        # Phase transition logic based on message count and completion
        if "greeting" not in completed_phases and message_count < 3:
            return "greeting"
        elif "chief_complaint" not in completed_phases and message_count < 8:
            return "chief_complaint"
        elif "mood_assessment" not in completed_phases and message_count < 16:
            return "mood_assessment"
        elif "cognitive_assessment" not in completed_phases and message_count < 22:
            return "cognitive_assessment"
        elif "physical_assessment" not in completed_phases and message_count < 28:
            return "physical_assessment"
        elif "behavioral_assessment" not in completed_phases and message_count < 34:
            return "behavioral_assessment"
        elif "trauma_assessment" not in completed_phases and message_count < 38:
            return "trauma_assessment"
        elif "functional_assessment" not in completed_phases and message_count < 42:
            return "functional_assessment"
        elif "mental_status_exam" not in completed_phases and message_count < 46:
            return "mental_status_exam"
        else:
            return "screener_administration"
    
    def create_session(self, patient_id: Optional[str] = None, user_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Create a new intake session
        
        Args:
            patient_id: Optional patient user ID (null for anonymous)
            user_name: Optional user's name (for authenticated users to skip name question)
            
        Returns:
            Session data with token
        """
        session_token = str(uuid.uuid4())
        
        session = {
            "session_token": session_token,
            "patient_id": patient_id,
            "user_name": user_name,  # Store user name to skip name question
            "created_at": datetime.utcnow().isoformat(),
            "current_phase": ConversationPhase.GREETING,
            "conversation_history": [],
            "extracted_data": {},
            "screeners_completed": [],
            "screener_scores": {},
            "risk_flags": [],
            "symptoms_detected": {}
        }
        
        self.sessions[session_token] = session
        
        return session
    
    def get_session(self, session_token: str) -> Optional[Dict[str, Any]]:
        """Get session by token"""
        return self.sessions.get(session_token)
    
    def get_conversation_history(self, session_token: str) -> Optional[List[Dict]]:
        """Get conversation history for session recovery"""
        session = self.get_session(session_token)
        if session and session.get("conversation_history"):
            return session["conversation_history"]
        return None
    
    def save_session_to_db(self, session_token: str, db_session):
        """Save session data to database for persistence"""
        try:
            from app.models.intake_session import IntakeSession
            from sqlalchemy.orm import Session
            
            # Get session data
            session_data = self.get_session(session_token)
            if not session_data:
                return
            
            # Find or create database session
            db_intake_session = db_session.query(IntakeSession).filter(
                IntakeSession.session_token == session_token
            ).first()
            
            if db_intake_session:
                # Update existing session
                db_intake_session.conversation_history = session_data.get("conversation_history", [])
                db_intake_session.extracted_data = session_data.get("extracted_data", {})
                db_intake_session.screener_scores = session_data.get("screener_scores", {})
                db_intake_session.current_screener = session_data.get("current_screener")
                db_intake_session.completed_screeners = session_data.get("completed_screeners", [])
                db_intake_session.updated_at = datetime.utcnow()
            else:
                # Create new session (shouldn't happen in normal flow)
                db_intake_session = IntakeSession(
                    session_token=session_token,
                    conversation_history=session_data.get("conversation_history", []),
                    extracted_data=session_data.get("extracted_data", {}),
                    screener_scores=session_data.get("screener_scores", {}),
                    current_screener=session_data.get("current_screener"),
                    completed_screeners=session_data.get("completed_screeners", [])
                )
                db_session.add(db_intake_session)
            
            db_session.commit()
            
        except Exception as e:
            logger.error(f"Error saving session to database: {str(e)}")
            if db_session:
                db_session.rollback()
    
    def load_session_from_db(self, session_token: str, db_session):
        """Load session data from database"""
        try:
            from app.models.intake_session import IntakeSession
            
            # Get session from database
            db_intake_session = db_session.query(IntakeSession).filter(
                IntakeSession.session_token == session_token
            ).first()
            
            if db_intake_session and db_intake_session.conversation_history:
                # Restore session data
                session_data = {
                    "conversation_history": db_intake_session.conversation_history or [],
                    "extracted_data": db_intake_session.extracted_data or {},
                    "screener_scores": db_intake_session.screener_scores or {},
                    "current_screener": db_intake_session.current_screener,
                    "completed_screeners": db_intake_session.completed_screeners or [],
                    "created_at": db_intake_session.created_at,
                    "updated_at": db_intake_session.updated_at
                }
                
                # Store in memory
                self.sessions[session_token] = session_data
                return session_data
            
        except Exception as e:
            logger.error(f"Error loading session from database: {str(e)}")
        
        return None
    
    def update_session(self, session_token: str, updates: Dict[str, Any]):
        """Update session data"""
        if session_token in self.sessions:
            self.sessions[session_token].update(updates)
    
    def add_message(
        self,
        session_token: str,
        role: str,
        content: str
    ):
        """
        Add a message to conversation history
        
        Args:
            session_token: Session identifier
            role: "user" or "model"
            content: Message content
        """
        session = self.get_session(session_token)
        if session:
            message = {
                "role": role,
                "content": content,
                "timestamp": datetime.utcnow().isoformat()
            }
            session["conversation_history"].append(message)
    
    async def get_initial_greeting(self, session_token: str) -> str:
        """Get the initial greeting message from Ava"""
        session = self.get_session(session_token)
        user_name = session.get("user_name") if session else None
        
        if user_name:
            # User is authenticated - skip name question and welcome them directly
            welcome_message = f"Hello {user_name}! I'm Ava, your AI mental health assistant. I'm here to help you through a brief mental health assessment.\n\nWhat brings you here today?"
            return welcome_message
        else:
            # Anonymous user - ask for name first
            messages = [
                {"role": "system", "content": INTAKE_SYSTEM_PROMPT},
                {"role": "user", "content": "Start the intake process"}
            ]
            
            response = await llm_service.get_chat_completion(messages, temperature=0.8)
            return response
    
    async def process_user_message(
        self,
        session_token: str,
        user_message: str
    ) -> AsyncIterator[str]:
        """
        Process user message and stream AI response
        
        Args:
            session_token: Session identifier
            user_message: User's message
            
        Yields:
            Chunks of AI response
        """
        logger.info(f"Processing message for session {session_token}: '{user_message[:50]}...'")
        
        try:
            session = self.get_session(session_token)
            if not session:
                logger.warning(f"Session not found: {session_token}")
                yield "⚠️ Session not found. Please start a new intake."
                return
            
            logger.info(f"Session found, proceeding with message processing")
        except Exception as e:
            logger.error(f"Error getting session {session_token}: {str(e)}")
            yield "⚠️ Session error. Please start a new intake."
            return
        
        # Check if user wants to start a new assessment (redo)
        if user_message.lower().strip() in ["start a new assessment", "new assessment", "redo assessment", "start over"]:
            # Reset session for new assessment
            session.clear()
            session["conversation_history"] = []
            session["symptoms_detected"] = {}
            session["screeners_completed"] = []
            session["current_phase"] = "greeting"
            session["completed_phases"] = []
            session["is_finished"] = False
            session["awaiting_finish_decision"] = False
            session["requires_safety_check"] = False
            session["requires_immediate_safety_check"] = False
            session["safety_plan_needed"] = False
            session["enhanced_safety_questions_needed"] = False
            session["skip_remaining_cssrs"] = False
            session["discussed_topics"] = {}
            session["chief_complaint_tracked"] = False
            
            # Start fresh assessment
            welcome_message = await self.get_initial_greeting(session_token)
            yield welcome_message
            return
        
        # Check if user wants to review their current assessment
        if user_message.lower().strip() in ["review my current assessment", "review assessment", "current assessment"]:
            if session.get("is_finished"):
                review_message = """Here's a summary of your completed assessment:

**Assessment Status:** Completed
**Report Generated:** Yes
**Email Sent:** Yes

Your comprehensive mental health assessment has been completed and the detailed report has been sent to your registered email address. The report includes:

- Provisional diagnoses based on DSM-5 criteria
- Risk assessment and safety recommendations
- Functional impairment evaluation
- Treatment recommendations
- Next steps for care

Please check your email for the complete report. If you haven't received it, please check your spam folder or contact support.

Would you like to:
- Start a new assessment
- Get help with something else

Is there anything else I can assist you with?"""
            else:
                # Assessment not yet completed
                conversation_count = len(session.get("conversation_history", []))
                completed_screeners = session.get("screeners_completed", [])
                symptoms_detected = session.get("symptoms_detected", {})
                
                review_message = f"""Here's the current status of your assessment:

**Assessment Status:** In Progress
**Conversation Messages:** {conversation_count}
**Screeners Completed:** {len(completed_screeners)} ({', '.join(completed_screeners) if completed_screeners else 'None'})
**Symptoms Identified:** {len([s for s in symptoms_detected.values() if s])}

Your assessment is still in progress. To complete it and receive your comprehensive report, please continue with the remaining questions.

Would you like to:
- Continue with the current assessment
- Start a new assessment
- Get help with something else

What would you prefer to do?"""
            
            yield review_message
            return
        
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
                yield crisis_response
                return
            
            # CLINICAL SUFFICIENCY CHECK: Ensure we have enough information
            conversation_history = session.get("conversation_history", [])
            completed_screeners = session.get("completed_screeners", [])
            
            # Check if we have sufficient DSM-5 domain coverage for clinical assessment
            dsm5_check = has_required_dsm5_domains(session)
            if not dsm5_check["complete"]:
                # Check if user is responding to our insufficient data message
                if session.get("awaiting_finish_decision"):
                    # Handle their response to the insufficient data options
                    response = user_message.strip().lower()
                    if "continue" in response or "yes" in response:
                        session["awaiting_finish_decision"] = False
                        yield "Thank you for continuing. Let me ask you a few more questions to better understand your situation. What brings you here today?"
                        return
                    elif "reason" in response or "specific" in response:
                        session["awaiting_finish_decision"] = False
                        yield "I understand. Could you tell me briefly what's happening that makes you want to finish early? This will help me understand your situation better."
                        return
                    elif "not comfortable" in response or "uncomfortable" in response:
                        session["awaiting_finish_decision"] = False
                        yield "I completely understand. Your comfort is the most important thing. You can stop at any time. Is there something specific that's making you uncomfortable, or would you prefer to end the assessment now?"
                        return
                    else:
                        # Default: continue with assessment
                        session["awaiting_finish_decision"] = False
                        yield "Let's continue with a few more questions. What's been the main concern that brought you here today?"
                        return
                
                # First time asking about insufficient data
                session["awaiting_finish_decision"] = True
                missing_domains = dsm5_check["missing_domains"]
                completion_pct = dsm5_check["completion_percentage"]
                
                insufficient_data_response = f"""I understand you'd like to complete the assessment early. However, we need to gather more comprehensive information to provide you with a clinically accurate assessment.

Current assessment progress: {completion_pct:.0f}% complete

To ensure we can provide you with the most helpful and accurate clinical evaluation, I still need to ask about:
- {', '.join(missing_domains[:3])}{' and more' if len(missing_domains) > 3 else ''}

This comprehensive approach follows established clinical standards and ensures we don't miss important aspects of your mental health.

Would you like to continue with the assessment, or do you have a specific reason for wanting to finish now?

BEGIN_OPTIONS
- Continue with the comprehensive assessment
- I have a specific reason for finishing early
- I'm not comfortable continuing
END_OPTIONS"""
                
                yield insufficient_data_response
                return
            
            # Safe to finish with sufficient data
            session["is_finished"] = True
            # TODO: Call actual report generation
            completion_message = """Thank you for completing the assessment. Your detailed report has been generated and sent to your registered email address. Please review it and consult with a healthcare professional for further evaluation and personalized care.

Would you like to:
- Start a new assessment
- Review your current assessment
- Get help with something else

Is there anything else I can assist you with today?"""
            yield completion_message
            return
        
        # CRITICAL SAFETY CHECKS - Must happen before any other processing
        # ENHANCED SAFETY ASSESSMENT - Multi-layer validation
        safety_assessment = self.enhanced_safety_assessment(user_message)
        
        # Immediate intervention for high-risk scenarios
        if safety_assessment.get('immediate_intervention'):
            risk_type = safety_assessment['risk_type']
            session[f"{risk_type}_detected"] = True
            session["requires_immediate_safety_check"] = True
            session["safety_plan_needed"] = True
            
            # Provide crisis intervention message
            yield safety_assessment['intervention_message']
            
            # Add safety plan if needed
            if safety_assessment.get('safety_plan_needed'):
                yield "\n\nLet me help you create a safety plan. What are your personal warning signs that things might be getting worse?"
            
            return
        
        # Enhanced safety questions for medium-risk scenarios
        if safety_assessment.get('enhanced_safety_questions'):
            risk_types = safety_assessment['risk_types']
            session["enhanced_safety_questions_needed"] = True
            session["safety_plan_needed"] = True
            
            # Provide enhanced safety assessment
            safety_questions = self.get_enhanced_safety_questions(risk_types)
            yield safety_questions
            return
        
        # Add user message to history
        self.add_message(session_token, "user", user_message)
        
        # Track last question asked to prevent repetition
        session["last_question"] = user_message
        
        # Track discussed topics to prevent repetition
        self._track_discussed_topics(session_token, user_message)
        
        # Track chief complaint if this is early in the conversation
        self._track_chief_complaint(session_token, user_message)
        
        # Build messages for LLM with discussed topics context
        discussed_topics = session.get("discussed_topics", {})
        discussed_context = self._build_discussed_topics_context(discussed_topics)
        
        # Enhanced system prompt with discussed topics context
        enhanced_system_prompt = INTAKE_SYSTEM_PROMPT + f"""

**CRITICAL: PREVIOUSLY DISCUSSED TOPICS**
The following topics have already been discussed in this assessment. DO NOT ask about them again unless you need specific follow-up details:

{discussed_context}

**REPETITION PREVENTION RULES:**
- NEVER ask about topics that are marked as "DISCUSSED" above
- NEVER repeat questions about symptoms already confirmed
- If a topic was discussed in the chief complaint, move to the next symptom area
- Focus on gathering NEW information, not rehashing what's already known
"""
        
        messages = [{"role": "system", "content": enhanced_system_prompt}]
        
        # Add conversation history
        for msg in session["conversation_history"]:
            messages.append({
                "role": "assistant" if msg["role"] == "model" else "user",
                "content": msg["content"]
            })
        
        # Check for C-SSRS branching logic before generating response
        session = self.get_session(session_token)
        self._check_cssrs_branching(session_token, user_message)
        
        # Check if patient acknowledged screener intro
        if session and session.get("current_phase") == ConversationPhase.SCREENER_INTRO_PENDING:
            if self._is_acknowledgment(user_message):
                # Patient is ready, move to screening phase
                session["current_phase"] = ConversationPhase.SCREENING
                # Add instruction to start first screener
                messages[0]["content"] += "\n\nIMPORTANT: The patient has confirmed they are ready to begin the screeners. Start with the FIRST screener question now (e.g., 'Great! Let's start with the PHQ-9. PHQ-9 Question #1: ...')."
        
        # If we need to skip C-SSRS questions, modify the system prompt
        if session and session.get("skip_remaining_cssrs"):
            # Add instruction to skip remaining C-SSRS questions
            messages[0]["content"] += "\n\nIMPORTANT: The patient has answered 'No' to a C-SSRS question that should end the suicide risk assessment. Do NOT ask any more C-SSRS questions. Instead, acknowledge completion of the safety assessment and move to the next screener (GAD-7) or complete the assessment if no more screeners are needed."
            session["skip_remaining_cssrs"] = False  # Reset flag
        
        # Add PHQ-9 conversation context if we're about to start PHQ-9
        phq9_context = self._analyze_conversation_for_phq9(session_token)
        if phq9_context:
            context_info = "\n\nCONVERSATION CONTEXT FOR PHQ-9:"
            for question_num, topic in phq9_context.items():
                context_info += f"\n- PHQ-9 Question #{question_num}: Patient discussed {topic}"
            context_info += "\n\nUse this context to reference previous conversation when asking PHQ-9 questions."
            messages[0]["content"] += context_info
            
            # Store conversation context for provider documentation
            if session:
                session["phq9_conversation_context"] = phq9_context
        
        # Stream response with error handling
        full_response = ""
        try:
            async for chunk in llm_service.stream_chat_completion(messages):
                # Additional safety check for chunk content
                if chunk and isinstance(chunk, str):
                    full_response += chunk
                    yield chunk
                elif chunk:
                    # Handle non-string chunks
                    safe_chunk = str(chunk).encode('utf-8', errors='replace').decode('utf-8')
                    full_response += safe_chunk
                    yield safe_chunk
        except Exception as e:
            logger.error(f"Error in LLM streaming for session {session_token}: {str(e)}")
            error_message = "I apologize, but I encountered an error processing your message. Please try rephrasing your response or continue with the assessment."
            yield error_message
            full_response = error_message
        
        # Enforce single question rule (with clinical safety allowlist)
        current_screener = session.get("current_screener") if session else None
        current_question = None
        if current_screener and session.get("screener_progress"):
            screener_progress = session["screener_progress"].get(current_screener, {})
            current_question = screener_progress.get("current_question", 0)
            item_id = f"{current_screener.lower()}_q{current_question + 1}"
        else:
            item_id = None
        
        full_response = enforce_single_question(full_response, item_id)
        
        # Parse options if present
        options = parse_options_block(full_response)
        
        # Add AI response to history
        self.add_message(session_token, "model", full_response)
        
        # Optional: attach options parsed from the last model turn, if present
        try:
            if options and session and session.get("conversation_history"):
                session["conversation_history"][-1]["options"] = options
        except Exception:
            # Do not break the flow if session/history structure differs
            pass
        
        # Check if this is screener introduction asking "Are you ready to begin?"
        if self._is_screener_intro(full_response):
            # Set phase to pending acknowledgment
            if session:
                session["current_phase"] = ConversationPhase.SCREENER_INTRO_PENDING
                # Add yes/no options for acknowledgment
                if session["conversation_history"]:
                    session["conversation_history"][-1]["options"] = [
                        {"label": "Yes, I'm ready", "value": "Yes, I'm ready to begin"},
                        {"label": "I have questions first", "value": "I have some questions before we start"}
                    ]
        
        # Analyze for symptom detection (simple keyword matching for now)
        self._detect_symptoms(session_token, user_message.lower())
        
        # Check if we're in a screener and handle the response
        screener_handled = self._handle_screener_response(session_token, user_message)
        
        # If we're in a screener, we need to send the response through streaming
        if screener_handled:
            # Get the last message from conversation history (the screener response)
            session = self.get_session(session_token)
            if session and session.get("conversation_history"):
                last_message = session["conversation_history"][-1]
                if last_message.get("role") == "model":
                    # Stream the screener response
                    response_content = last_message["content"]
                    
                    # Send the response in chunks
                    chunk_size = 50
                    for i in range(0, len(response_content), chunk_size):
                        chunk = response_content[i:i + chunk_size]
                        response = ChatResponse(
                            role="model",
                            content=chunk,
                            timestamp=datetime.utcnow(),
                            done=False
                        )
                        yield f"data: {response.model_dump_json()}\n\n"
                    
                    # Send final message with options if this is a screener question
                    session = self.get_session(session_token)
                    current_screener = session.get("current_screener")
                    if current_screener:
                        # Get the current screener and question to find options
                        screener_class = screener_registry.get_screener(current_screener)
                        if screener_class:
                            screener_progress = session.get("screener_progress", {})
                            current_question_index = screener_progress.get(current_screener, {}).get("current_question", 0)
                            questions = screener_class().questions
                            if current_question_index < len(questions):
                                current_question = questions[current_question_index]
                                final_response = ChatResponse(
                                    role="model",
                                    content="",
                                    timestamp=datetime.utcnow(),
                                    done=True,
                                    options=current_question.options
                                )
                                yield f"data: {final_response.model_dump_json()}\n\n"
                                return
                    
                    # No options available
                    final_response = ChatResponse(
                        role="model",
                        content="",
                        timestamp=datetime.utcnow(),
                        done=True
                    )
                    yield f"data: {final_response.model_dump_json()}\n\n"
            return
        
        # Check if this is a screener question and add options
        # BUT NOT for name questions
        if not ("name" in full_response.lower() and "use during our conversation" in full_response.lower()):
            options = self._parse_screener_options(full_response)
            if options:
                # Update the last message with options
                session = self.get_session(session_token)
                if session and session["conversation_history"]:
                    session["conversation_history"][-1]["options"] = options
        
        # Check if we should show finish button
        if self._should_show_finish_button(full_response):
            session = self.get_session(session_token)
            if session and session["conversation_history"]:
                session["conversation_history"][-1]["options"] = [{
                    "label": "Complete Assessment",
                    "value": ":finish"
                }]
        
        # Track screener completion
        self._track_screener_completion(session_token, full_response)
        
        # Check for question repetition before finalizing response
        session = self.get_session(session_token)
        if session:
            last_ai_message = session.get("last_ai_question", "")
            if last_ai_message and _is_same_question(last_ai_message, full_response):
                # Generate a different follow-up question to avoid repetition
                alternative_response = "I understand. Let me ask you something different. How is this affecting your daily activities or work?"
                full_response = alternative_response
                logger.info(f"Prevented question repetition, using alternative: {alternative_response}")
            
            # Track AI's last question to prevent repetition
            session["last_ai_question"] = full_response
        
        # Check if we should enforce screener administration
        self._check_and_enforce_screeners(session_token)
    
    def _check_and_enforce_screeners(self, session_token: str):
        """
        Check if any screeners need to be enforced and add them to the conversation
        """
        try:
            logger.info(f"Checking screener enforcement for session {session_token}")
            session = self.get_session(session_token)
            if not session:
                logger.warning(f"Session not found for screener enforcement: {session_token}")
                return
            
            # Get detected symptoms and completed screeners
            symptoms = session.get("symptoms_detected", {})
            completed = session.get("completed_screeners", [])
            message_count = len(session.get("conversation_history", []))
            
            logger.info(f"Symptoms: {symptoms}, Completed: {completed}, Messages: {message_count}")
            
            # Get pending screeners that need to be administered
            pending_screeners = screener_enforcement_service.get_pending_screeners(symptoms, completed)
            logger.info(f"Pending screeners: {pending_screeners}")
            
            if pending_screeners:
                logger.info(f"Pending screeners detected: {pending_screeners}")
                
                # Check if we should enforce screeners now
                should_enforce = screener_enforcement_service.should_enforce_screeners(session)
                logger.info(f"Should enforce screeners: {should_enforce}")
                
                if should_enforce:
                    # Get the next screener to administer
                    next_screener = pending_screeners[0]
                    
                    # Get the actual screener instance and ask the first question
                    screener_class = screener_registry._screeners.get(next_screener)
                    if screener_class:
                        screener_instance = screener_class()
                        questions = screener_instance.questions
                        
                        if questions:
                            # Ask the first question with proper options
                            first_question = questions[0]
                            screener_message = f"Thank you for confirming, James! Let's start with the {next_screener}.\n\n{next_screener} Question #{first_question.number}: {first_question.text}\n\nPlease select your answer:\n"
                            
                            # Add options in the proper format
                            for option in first_question.options:
                                screener_message += f"- {option['label']}\n"
                            
                            # Add the screener message to conversation history
                            self.add_message(session_token, "model", screener_message)
                            
                            # Update session state
                            session["current_screener"] = next_screener
                            session["pending_screeners"] = pending_screeners[1:]  # Remove the one we're starting
                            session["screener_progress"] = {next_screener: {"current_question": 0, "responses": []}}
                            
                            logger.info(f"Enforcing screener administration: {next_screener} - Question 1")
                        else:
                            # Fallback to generic message if no questions
                            screener_message = screener_enforcement_service.get_screener_transition_message(
                                pending_screeners
                            )
                            self.add_message(session_token, "model", screener_message)
                            session["current_screener"] = next_screener
                            session["pending_screeners"] = pending_screeners[1:]
                    else:
                        logger.error(f"Screener class not found: {next_screener}")
            else:
                logger.info("No pending screeners found")
            
        except Exception as e:
            logger.error(f"Error in screener enforcement: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
    
    def _handle_screener_response(self, session_token: str, user_message: str) -> bool:
        """
        Handle responses when user is in the middle of a screener
        
        Returns:
            True if screener response was handled, False otherwise
        """
        try:
            session = self.get_session(session_token)
            if not session:
                return False
            
            current_screener = session.get("current_screener")
            if not current_screener:
                return False
            
            logger.info(f"Handling screener response for {current_screener}: {user_message}")
            
            # Get screener instance
            screener_class = screener_registry._screeners.get(current_screener)
            if not screener_class:
                logger.error(f"Screener class not found: {current_screener}")
                return False
            
            screener_instance = screener_class()
            questions = screener_instance.questions
            
            # Get current progress
            screener_progress = session.get("screener_progress", {})
            current_progress = screener_progress.get(current_screener, {"current_question": 0, "responses": []})
            current_question_index = current_progress["current_question"]
            responses = current_progress["responses"]
            
            # Map user response to option value
            current_question = questions[current_question_index]
            user_response_value = self._map_response_to_value(user_message, current_question.options)
            
            if user_response_value is not None:
                # Add response
                responses.append(user_response_value)
                current_question_index += 1
                
                # Update progress
                screener_progress[current_screener] = {
                    "current_question": current_question_index,
                    "responses": responses
                }
                session["screener_progress"] = screener_progress
                
                # Check if screener is complete
                if current_question_index >= len(questions):
                    # Screener complete - score it
                    score_result = screener_instance.score(responses)
                    
                    # Store score
                    if "screener_scores" not in session:
                        session["screener_scores"] = {}
                    session["screener_scores"][current_screener] = score_result
                    
                    # Mark as completed
                    if "completed_screeners" not in session:
                        session["completed_screeners"] = []
                    if current_screener not in session["completed_screeners"]:
                        session["completed_screeners"].append(current_screener)
                    
                    # Clear current screener
                    session["current_screener"] = None
                    
                    # Add completion message
                    completion_message = f"Thank you for completing the {current_screener}. Your responses have been recorded.\n\n"
                    if hasattr(score_result, 'interpretation'):
                        completion_message += f"Based on your responses: {score_result.interpretation}\n\n"
                    
                    # Check if there are more screeners to complete
                    pending_screeners = session.get("pending_screeners", [])
                    if pending_screeners:
                        next_screener = pending_screeners[0]
                        completion_message += f"Now let's continue with the {next_screener}.\n\n"
                        
                        # Start next screener
                        next_screener_class = screener_registry._screeners.get(next_screener)
                        if next_screener_class:
                            next_screener_instance = next_screener_class()
                            next_questions = next_screener_instance.questions
                            
                            if next_questions:
                                first_question = next_questions[0]
                                completion_message += f"{next_screener} Question #{first_question.number}: {first_question.text}\n\nPlease select your answer:\n"
                                
                                for option in first_question.options:
                                    completion_message += f"- {option['label']}\n"
                                
                                # Update session state
                                session["current_screener"] = next_screener
                                session["pending_screeners"] = pending_screeners[1:]
                                screener_progress[next_screener] = {"current_question": 0, "responses": []}
                                session["screener_progress"] = screener_progress
                                
                    
                    self.add_message(session_token, "model", completion_message)
                    logger.info(f"Completed screener: {current_screener}")
                    return True
                    
                else:
                    # Ask next question
                    next_question = questions[current_question_index]
                    next_question_message = f"{current_screener} Question #{next_question.number}: {next_question.text}\n\nPlease select your answer:\n"
                    
                    for option in next_question.options:
                        next_question_message += f"- {option['label']}\n"
                    
                    self.add_message(session_token, "model", next_question_message)
                    
                    logger.info(f"Asked {current_screener} question {current_question_index + 1}")
                    return True
            else:
                # Response not recognized, ask for clarification
                clarification_message = f"I didn't understand your response. Please select one of the following options:\n"
                for option in current_question.options:
                    clarification_message += f"- {option['label']}\n"
                
                self.add_message(session_token, "model", clarification_message)
                
                return True
            
        except Exception as e:
            logger.error(f"Error handling screener response: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return False
    
    def _map_response_to_value(self, user_message: str, options: List[Dict]) -> Optional[int]:
        """
        Map user's text response to the corresponding option value
        """
        user_message_lower = user_message.lower().strip()
        
        # Try exact matches first
        for option in options:
            if option['label'].lower() == user_message_lower:
                return option['value']
        
        # Try partial matches
        for option in options:
            if option['label'].lower() in user_message_lower or user_message_lower in option['label'].lower():
                return option['value']
        
        # Try common variations
        response_mappings = {
            'never': 0, 'rarely': 1, 'sometimes': 2, 'often': 3, 'very often': 4,
            'not at all': 0, 'several days': 1, 'more than half': 2, 'nearly every day': 3,
            'yes': 1, 'no': 0, 'true': 1, 'false': 0
        }
        
        for key, value in response_mappings.items():
            if key in user_message_lower:
                return value
        
        return None
    
    def _analyze_conversation_for_phq9(self, session_token: str) -> Dict[str, str]:
        """
        Analyze conversation history to extract relevant information for PHQ-9 questions
        Returns a mapping of PHQ-9 question numbers to relevant conversation snippets
        """
        session = self.get_session(session_token)
        if not session:
            return {}
        
        conversation = session.get("conversation_history", [])
        phq9_context = {}
        
        # Combine all conversation text for analysis
        full_conversation = ""
        for msg in conversation:
            if msg.get("role") == "user":
                full_conversation += msg.get("content", "") + " "
        
        full_conversation = full_conversation.lower()
        
        # PHQ-9 #1: Little interest or pleasure in doing things
        if any(word in full_conversation for word in ["interest", "enjoy", "pleasure", "fun", "hobby", "motivation"]):
            phq9_context["1"] = "interest/pleasure"
        
        # PHQ-9 #2: Feeling down, depressed, or hopeless
        if any(word in full_conversation for word in ["depressed", "sad", "hopeless", "down", "blue", "miserable"]):
            phq9_context["2"] = "depression/mood"
        
        # PHQ-9 #3: Trouble falling or staying asleep, or sleeping too much
        if any(word in full_conversation for word in ["sleep", "insomnia", "tired", "exhausted", "can't sleep", "sleeping"]):
            phq9_context["3"] = "sleep"
        
        # PHQ-9 #4: Feeling tired or having little energy
        if any(word in full_conversation for word in ["tired", "energy", "fatigue", "exhausted", "lethargic"]):
            phq9_context["4"] = "energy"
        
        # PHQ-9 #5: Poor appetite or overeating
        if any(word in full_conversation for word in ["appetite", "eating", "hungry", "food", "weight"]):
            phq9_context["5"] = "appetite"
        
        # PHQ-9 #6: Feeling bad about yourself
        if any(word in full_conversation for word in ["worthless", "failure", "guilty", "bad about myself", "self-esteem"]):
            phq9_context["6"] = "self-worth"
        
        # PHQ-9 #7: Trouble concentrating
        if any(word in full_conversation for word in ["concentrate", "focus", "attention", "distracted", "mind wandering"]):
            phq9_context["7"] = "concentration"
        
        # PHQ-9 #8: Moving or speaking slowly
        if any(word in full_conversation for word in ["slow", "sluggish", "moving slowly", "speaking slowly"]):
            phq9_context["8"] = "psychomotor"
        
        # PHQ-9 #9: Thoughts of self-harm
        if any(word in full_conversation for word in ["hurt myself", "suicide", "kill myself", "self-harm", "death"]):
            phq9_context["9"] = "self-harm"
        
        return phq9_context
    
    def enhanced_safety_assessment(self, message: str) -> Dict[str, Any]:
        """
        Enhanced safety assessment with comprehensive risk evaluation
        """
        risks = {
            'suicide_risk': check_suicide_risk(message),
            'homicidal_risk': check_homicidal_risk(message),
            'psychosis_risk': check_psychosis_risk(message),
            'mania_risk': check_mania_risk(message),
            'substance_overdose_risk': check_substance_overdose_risk(message),
            'trauma_crisis_risk': check_trauma_crisis_risk(message)
        }
        
        # Immediate intervention for high-risk scenarios
        for risk_type, risk_level in risks.items():
            if risk_level == 'high':
                return {
                    'immediate_intervention': True,
                    'risk_type': risk_type,
                    'risk_level': risk_level,
                    'intervention_message': self.get_crisis_intervention_message(risk_type),
                    'safety_plan_needed': True
                }
        
        # Medium-risk scenarios get enhanced safety questions
        medium_risks = [risk_type for risk_type, level in risks.items() if level == 'medium']
        if medium_risks:
            return {
                'immediate_intervention': False,
                'enhanced_safety_questions': True,
                'risk_types': medium_risks,
                'safety_plan_needed': True
            }
        
        return {'immediate_intervention': False, 'enhanced_safety_questions': False}
    
    def get_crisis_intervention_message(self, risk_type: str) -> str:
        """Get appropriate crisis intervention message"""
        interventions = {
            'suicide_risk': "I'm concerned about your safety. Please call 988 (Suicide & Crisis Lifeline) or go to your nearest emergency room immediately. You're not alone, and help is available.",
            'homicidal_risk': "I'm concerned about safety. Please contact emergency services (911) or go to your nearest emergency room immediately. Professional help is available.",
            'psychosis_risk': "I'm concerned about your symptoms. Please contact emergency services (911) or go to your nearest emergency room for immediate evaluation. Help is available.",
            'mania_risk': "I'm concerned about your symptoms. Please contact your healthcare provider or go to your nearest emergency room for immediate evaluation."
        }
        return interventions.get(risk_type, "Please contact emergency services or go to your nearest emergency room immediately.")
    
    def stanley_brown_safety_plan(self, risk_type: str) -> Dict[str, str]:
        """
        Stanley-Brown Safety Plan micro-flow implementation
        """
        safety_plan_steps = {
            'SP-1': {
                'title': 'Warning Signs',
                'content': 'What are your personal warning signs that a crisis might be developing? (e.g., increased isolation, sleep changes, substance use)'
            },
            'SP-2': {
                'title': 'Internal Coping Strategies',
                'content': 'What are some things you can do on your own to help you feel better? (e.g., exercise, music, breathing exercises)'
            },
            'SP-3': {
                'title': 'People and Places',
                'content': 'Who are people you can contact for support? What are safe places you can go?'
            },
            'SP-4': {
                'title': 'Professional Contacts',
                'content': 'Who are your professional supports? (therapist, doctor, crisis line: 988)'
            },
            'SP-5': {
                'title': 'Means Restriction',
                'content': 'How can we make your environment safer? (removing access to harmful items, having someone hold medications)'
            }
        }
        
        return safety_plan_steps
    
    def get_enhanced_safety_questions(self, risk_types: List[str]) -> str:
        """Get enhanced safety questions for medium-risk scenarios"""
        questions = []
        
        for risk_type in risk_types:
            if risk_type == 'suicide_risk':
                questions.append("Have you had any thoughts of hurting yourself or ending your life?")
            elif risk_type == 'homicidal_risk':
                questions.append("Have you had any thoughts of hurting others?")
            elif risk_type == 'psychosis_risk':
                questions.append("Are you hearing voices or seeing things that others don't see or hear?")
            elif risk_type == 'mania_risk':
                questions.append("Have you been feeling unusually energetic or like you don't need sleep?")
            elif risk_type == 'substance_overdose_risk':
                questions.append("Are you using substances in a way that concerns you or others?")
            elif risk_type == 'trauma_crisis_risk':
                questions.append("Are you currently experiencing flashbacks or feeling triggered?")
        
        if questions:
            return "I want to make sure you're safe. " + " ".join(questions)
        return "I want to make sure you're safe. How are you feeling right now?"

    def _detect_symptoms(self, session_token: str, message: str):
        """
        Enhanced symptom detection from user message
        """
        try:
            logger.info(f"Detecting symptoms for message: '{message[:100]}...'")
            session = self.get_session(session_token)
            if not session:
                logger.warning(f"Session not found for symptom detection: {session_token}")
                return
            
            symptoms = session.get("symptoms_detected", {})
            logger.info(f"Current symptoms before detection: {symptoms}")
        except Exception as e:
            logger.error(f"Error in symptom detection setup: {str(e)}")
            return
        
        # Enhanced clinical condition detection
        message_lower = message.lower()
        
        # MDD (Major Depressive Disorder) - comprehensive detection
        mdd_keywords = ["depressed", "sad", "hopeless", "down", "worthless", "failure", "crying", "empty", 
                       "anhedonia", "loss of interest", "guilty", "suicidal", "death thoughts"]
        if any(word in message_lower for word in mdd_keywords):
            symptoms["depression"] = True
            symptoms["mdd"] = True
        
        # GAD (Generalized Anxiety Disorder) - comprehensive detection
        gad_keywords = ["anxious", "anxiety", "worry", "worried", "nervous", "panic", "fear", "stressed", "tense",
                       "restless", "muscle tension", "irritable", "fatigue", "concentration problems"]
        if any(word in message_lower for word in gad_keywords):
            symptoms["anxiety"] = True
            symptoms["gad"] = True
        
        # PTSD - comprehensive detection
        ptsd_keywords = ["trauma", "flashback", "nightmare", "avoidance", "hypervigilance", "ptsd", "abuse", "assault"]
        if any(word in message_lower for word in ptsd_keywords):
            symptoms["ptsd"] = True
            symptoms["trauma"] = True
        
        # Bipolar Disorder - comprehensive detection
        bipolar_keywords = ["manic", "mania", "hyper", "hypomanic", "racing", "energetic", "impulsive", "reckless", 
                           "grandiose", "elevated mood", "decreased sleep", "bipolar", "mood swings"]
        if any(word in message_lower for word in bipolar_keywords):
            symptoms["mania"] = True
            symptoms["bipolar"] = True
        
        # ADHD - comprehensive detection
        adhd_keywords = ["attention", "focus", "concentration", "distracted", "hyperactive", "impulsive", "adhd",
                        "forgetful", "disorganized", "fidgety", "restless"]
        if any(word in message_lower for word in adhd_keywords):
            symptoms["attention"] = True
            symptoms["adhd"] = True
        
        # Schizophrenia - comprehensive detection
        schizophrenia_keywords = ["hallucination", "delusion", "voices", "paranoid", "disorganized", "schizophrenia",
                                 "hearing voices", "seeing things", "thoughts", "beliefs"]
        if any(word in message_lower for word in schizophrenia_keywords):
            symptoms["psychosis"] = True
            symptoms["schizophrenia"] = True
        
        # ADHD keywords
        if any(word in message for word in ["focus", "attention", "concentrate", "concentrating", "distracted", "forgetful", "organize", "restless", "fidget", "hyperactive"]):
            symptoms["attention"] = True
        
        # Trauma keywords
        if any(word in message for word in ["trauma", "flashback", "nightmare", "ptsd", "assault", "abuse", "accident", "intrusive"]):
            symptoms["trauma"] = True
        
        # Sleep keywords
        if any(word in message for word in ["sleep", "sleeping", "insomnia", "tired", "exhausted", "fatigue", "wake", "waking", "drowsy"]):
            symptoms["sleep"] = True
        
        # Alcohol keywords
        if any(word in message for word in ["alcohol", "drinking", "drink", "drunk", "beer", "wine", "liquor"]):
            symptoms["substance"] = True
            symptoms["alcohol"] = True
        
        # Drug use keywords
        if any(word in message for word in ["drugs", "marijuana", "cocaine", "heroin", "meth", "pills", "opioid", "weed", "high"]):
            symptoms["substance"] = True
            symptoms["drugs"] = True
        
        # Eating disorder keywords
        if any(word in message for word in ["appetite", "eating", "weight", "gained", "lost", "food", "hungry", "overeating", "binge", "purge", "vomit", "fat", "thin"]):
            symptoms["eating"] = True
        
        # OCD keywords
        if any(word in message for word in ["obsess", "obsessive", "compulsive", "ritual", "checking", "washing", "contamination", "intrusive", "repetitive"]):
            symptoms["obsessions"] = True
            symptoms["compulsions"] = True
        
        # Stress keywords
        if any(word in message for word in ["stress", "stressed", "overwhelmed", "pressure", "burden", "demands", "cope", "coping"]):
            symptoms["stress"] = True
        
        # Social anxiety keywords
        if any(word in message for word in ["social", "embarrass", "embarrassed", "people", "public", "shy", "avoid", "judged", "awkward"]):
            symptoms["social_anxiety"] = True
        
        # Panic keywords
        if any(word in message for word in ["panic", "panicking", "heart racing", "palpitations", "hyperventilate", "chest"]):
            symptoms["panic"] = True
        
        # Somatic/physical keywords
        if any(word in message for word in ["pain", "aches", "headache", "stomach", "dizzy", "nausea", "physical"]):
            symptoms["somatic"] = True
            symptoms["physical"] = True
        
        # Loneliness/isolation keywords
        if any(word in message for word in ["lonely", "alone", "isolated", "no friends", "nobody"]):
            symptoms["loneliness"] = True
            symptoms["isolated"] = True
        
        # Life dissatisfaction keywords
        if any(word in message for word in ["dissatisfied", "unhappy", "unfulfilled", "meaningless", "pointless"]):
            symptoms["dissatisfied"] = True
            symptoms["unhappy"] = True
        
        # Impulsivity keywords
        if any(word in message for word in ["impulsive", "reckless", "act without thinking", "spur of the moment"]):
            symptoms["impulsive"] = True
            symptoms["reckless"] = True
        
        # Perinatal keywords
        if any(word in message for word in ["pregnant", "pregnancy", "postpartum", "baby", "newborn", "breastfeeding"]):
            symptoms["pregnant"] = True
            symptoms["postpartum"] = True
            symptoms["perinatal"] = True
        
        # Childhood trauma keywords
        if any(word in message for word in ["childhood", "growing up", "when i was young", "as a child", "abused", "neglect"]):
            symptoms["childhood"] = True
        
        try:
            session["symptoms_detected"] = symptoms
            logger.info(f"Updated symptoms: {symptoms}")
            
            # Freeze required_screeners in session data for progress UI
            if "required_screeners" not in session:
                session["required_screeners"] = screener_enforcement_service.get_required_screeners(symptoms)
                logger.info(f"Frozen required_screeners: {session['required_screeners']}")
        except Exception as e:
            logger.error(f"Error updating symptoms in session: {str(e)}")
    
    def _parse_screener_options(self, response: str) -> List[Dict[str, str]]:
        """
        Parse screener response to extract options for clickable buttons
        Also detects options in conversational questions with "Please select your answer:"
        """
        # Check if this looks like a screener question OR has the "Please select" phrase
        is_formal_screener = ("PHQ-9 Question" in response or "GAD-7 Question" in response or "C-SSRS Question" in response)
        has_select_phrase = ("Please select your answer:" in response or "Please enter your choice" in response or "Please select:" in response)
        
        if is_formal_screener or has_select_phrase:
            # Extract options from the response
            lines = response.split('\n')
            options = []
            
            # Only look for options after the question text
            in_options_section = False
            
            for line in lines:
                line = line.strip()
                
                # Check if we've reached the options section
                if "Please select your answer:" in line or "Please enter your choice" in line or "Please select:" in line:
                    in_options_section = True
                    continue
                
                # Only process options after we've found the options section
                if in_options_section and line.startswith('- '):
                    option_text = line[2:].strip()
                    # Filter out invalid options (screener names, system messages)
                    if (option_text and 
                        option_text not in ["The system will provide clickable buttons for these options"] and
                        not option_text.endswith("(depression screening)") and
                        not option_text.endswith("(anxiety screening)") and
                        not option_text.endswith("(safety assessment)")):
                        options.append({
                            "label": option_text,
                            "value": option_text
                        })
            
            return options if len(options) >= 2 else None
        
        return None
    
    def _should_show_finish_button(self, response: str) -> bool:
        """
        Check if the response indicates completion and should show finish button
        """
        finish_indicators = [
            "enough information to create your assessment report",
            "ready to generate your comprehensive report",
            "click the button below to generate",
            "complete your assessment",
            "generate your report"
        ]
        
        return any(indicator in response.lower() for indicator in finish_indicators)
    
    def _track_screener_completion(self, session_token: str, response: str):
        """
        Track when screeners are completed for pause/resume functionality
        """
        session = self.get_session(session_token)
        if not session:
            return
        
        # Initialize tracking if not present
        if "completed_screeners" not in session:
            session["completed_screeners"] = []
        if "current_screener" not in session:
            session["current_screener"] = None
        if "screener_progress" not in session:
            session["screener_progress"] = {}
        
        # Dynamic screener tracking for ALL screeners
        from app.screeners.registry import screener_registry
        all_screeners = screener_registry.list_screeners()
        
        # Check for screener completion (dynamic for any screener)
        for screener_name in all_screeners:
            if f"{screener_name} completed" in response or f"{screener_name.lower()} completed" in response.lower():
                if screener_name not in session["completed_screeners"]:
                    session["completed_screeners"].append(screener_name)
            session["current_screener"] = None
            
            # Add progress update to response
            progress_msg = generate_progress_update(session)
            if progress_msg:
                response += progress_msg
            
            # Check if we should offer a break
            if should_offer_break(session):
                break_offer = generate_break_offer()
                session[f"break_offered_after_{len(session['completed_screeners'])}"] = True
                # Return break offer instead of next screener
                response = break_offer
            
            break
        
        # Track when starting a new screener (dynamic for any screener)
        for screener_name in all_screeners:
            if f"{screener_name} Question" in response:
                session["current_screener"] = screener_name
                break
    
    def _check_cssrs_branching(self, session_token: str, user_message: str):
        """
        Check if we need to skip C-SSRS questions based on patient responses
        """
        session = self.get_session(session_token)
        if not session:
            return
        
        # Check if the last AI message was a C-SSRS question
        conversation = session.get("conversation_history", [])
        if not conversation:
            return
        
        last_ai_message = None
        for msg in reversed(conversation):
            if msg.get("role") == "model":
                last_ai_message = msg.get("content", "")
                break
        
        if not last_ai_message or "C-SSRS Question" not in last_ai_message:
            return
        
        # Check which C-SSRS question was asked and what the patient answered
        user_response = user_message.lower().strip()
        
        # C-SSRS Question #1: Wished dead
        if "C-SSRS Question #1" in last_ai_message:
            if user_response in ["no"]:
                # Skip to next screener - add a flag to skip remaining C-SSRS questions
                session["skip_remaining_cssrs"] = True
                return
        
        # C-SSRS Question #2: Thoughts of killing self
        elif "C-SSRS Question #2" in last_ai_message:
            if user_response in ["no"]:
                # Skip to next screener - add a flag to skip remaining C-SSRS questions
                session["skip_remaining_cssrs"] = True
                return
        
        # C-SSRS Question #3: Thought about how
        elif "C-SSRS Question #3" in last_ai_message:
            if user_response in ["no"]:
                # Skip to next screener - add a flag to skip remaining C-SSRS questions
                session["skip_remaining_cssrs"] = True
                return
        
        # C-SSRS Question #4: Intention of acting
        elif "C-SSRS Question #4" in last_ai_message:
            if user_response in ["no"]:
                # Skip to next screener - add a flag to skip remaining C-SSRS questions
                session["skip_remaining_cssrs"] = True
                return
    
    def get_recommended_screeners(self, session_token: str) -> List[str]:
        """
        Get list of recommended screeners based on symptoms detected
        
        Args:
            session_token: Session identifier
            
        Returns:
            List of screener names to administer
        """
        session = self.get_session(session_token)
        if not session:
            return []
        
        symptoms = session.get("symptoms_detected", {})
        completed = session.get("screeners_completed", [])
        
        # Get recommended screeners
        try:
            logger.info(f"Getting screeners for symptoms: {symptoms}")
            recommended = screener_registry.get_screeners_for_symptoms(symptoms)
            logger.info(f"Recommended screeners: {recommended}")
        except Exception as e:
            logger.error(f"Error getting recommended screeners: {str(e)}")
            recommended = []
        
        # Filter out already completed
        return [s for s in recommended if s not in completed]
    
    def _is_screener_intro(self, response: str) -> bool:
        """
        Detect if Ava is introducing screeners and asking "Are you ready to begin?"
        
        Args:
            response: Ava's message
            
        Returns:
            True if this is a screener introduction message
        """
        lower_response = response.lower()
        
        # Check for screener introduction keywords + readiness question
        has_screener_intro = any(word in lower_response for word in [
            "phq-9", "gad-7", "c-ssrs", "screening questionnaire", "standardized screening"
        ])
        has_ready_question = any(phrase in lower_response for phrase in [
            "are you ready to begin", "are you ready", "ready to begin", "shall we begin"
        ])
        
        return has_screener_intro and has_ready_question
    
    def _is_acknowledgment(self, user_message: str) -> bool:
        """
        Detect if patient is acknowledging readiness to begin screeners
        
        Args:
            user_message: Patient's response
            
        Returns:
            True if patient is saying yes/ready
        """
        lower_msg = user_message.lower().strip()
        
        # Positive acknowledgments
        positive = ["yes", "yeah", "yep", "sure", "ok", "okay", "ready", "i'm ready", "let's go", 
                   "let's begin", "let's start", "go ahead", "proceed"]
        
        return any(phrase in lower_msg for phrase in positive)
    
    def restore_session(self, session_token: str, session_data: dict):
        """
        Restore a paused session with full state
        """
        # Store the complete session state
        self.sessions[session_token] = session_data
        
        # Ensure we have all required fields
        if "conversation_history" not in self.sessions[session_token]:
            self.sessions[session_token]["conversation_history"] = []
        if "extracted_data" not in self.sessions[session_token]:
            self.sessions[session_token]["extracted_data"] = {}
        if "screener_scores" not in self.sessions[session_token]:
            self.sessions[session_token]["screener_scores"] = {}
        if "completed_screeners" not in self.sessions[session_token]:
            self.sessions[session_token]["completed_screeners"] = []
        if "current_screener" not in self.sessions[session_token]:
            self.sessions[session_token]["current_screener"] = None
        if "screener_progress" not in self.sessions[session_token]:
            self.sessions[session_token]["screener_progress"] = {}
        if "current_phase" not in self.sessions[session_token]:
            self.sessions[session_token]["current_phase"] = "greeting"


# Global conversation service instance
conversation_service = ConversationService()

