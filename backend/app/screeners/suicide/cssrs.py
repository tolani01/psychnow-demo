"""
C-SSRS: Columbia-Suicide Severity Rating Scale
CRITICAL suicide risk assessment tool

This is a simplified screening version for intake purposes.
Full clinical C-SSRS should be administered by a trained clinician.

Risk Levels:
- Low: Suicidal ideation without plan, intent, or behavior
- Moderate: Suicidal ideation with some planning
- High: Suicidal ideation with plan and intent, or recent behavior
"""
from typing import List, Dict, Any
from app.screeners.base import BaseScreener, ScreenerQuestion, ScreenerResult


class CSSRS(BaseScreener):
    """C-SSRS Suicide Risk Screener (Simplified Screening Version)"""
    
    @property
    def name(self) -> str:
        return "C-SSRS"
    
    @property
    def description(self) -> str:
        return "Columbia-Suicide Severity Rating Scale - Screening version for suicide risk assessment"
    
    @property
    def questions(self) -> List[ScreenerQuestion]:
        """
        C-SSRS Screening Questions
        Binary (Yes/No) responses
        """
        options = [
            {"value": 0, "label": "No"},
            {"value": 1, "label": "Yes"}
        ]
        
        return [
            ScreenerQuestion(
                number=1,
                text="Have you wished you were dead or wished you could go to sleep and not wake up?",
                options=options
            ),
            ScreenerQuestion(
                number=2,
                text="Have you actually had any thoughts of killing yourself?",
                options=options
            ),
            ScreenerQuestion(
                number=3,
                text="Have you been thinking about how you might do this?",
                options=options
            ),
            ScreenerQuestion(
                number=4,
                text="Have you had these thoughts and had some intention of acting on them?",
                options=options
            ),
            ScreenerQuestion(
                number=5,
                text="Have you started to work out or worked out the details of how to kill yourself? Do you intend to carry out this plan?",
                options=options
            ),
            ScreenerQuestion(
                number=6,
                text="In the past 3 months, have you done anything, started to do anything, or prepared to do anything to end your life?",
                options=options
            ),
        ]
    
    def score(self, responses: List[int]) -> ScreenerResult:
        """
        Score C-SSRS and determine risk level
        
        Args:
            responses: List of 6 binary integers (0 or 1)
            
        Returns:
            ScreenerResult with risk level and recommendations
        """
        # Validate responses
        self.validate_responses(responses)
        
        # Analyze responses
        wish_dead = responses[0]  # Q1
        suicidal_thoughts = responses[1]  # Q2
        methods = responses[2]  # Q3
        intent = responses[3]  # Q4
        plan = responses[4]  # Q5
        recent_behavior = responses[5]  # Q6
        
        # Determine risk level
        risk_level = "none"
        interpretation = "No current suicidal ideation"
        clinical_sig = "No immediate suicide risk detected. Continue monitoring."
        urgency = "routine"
        
        if wish_dead == 1 and suicidal_thoughts == 0:
            risk_level = "low"
            interpretation = "Passive death wish without active suicidal ideation"
            clinical_sig = "Low risk. Monitor closely. Provide crisis resources. Follow up soon."
            urgency = "routine"
        
        elif suicidal_thoughts == 1 and methods == 0 and intent == 0:
            risk_level = "low"
            interpretation = "Active suicidal ideation without plan or intent"
            clinical_sig = "Low-moderate risk. Safety planning recommended. Provide crisis resources. Follow up within 1 week."
            urgency = "urgent"
        
        elif suicidal_thoughts == 1 and methods == 1 and intent == 0:
            risk_level = "moderate"
            interpretation = "Suicidal ideation with method consideration but no intent"
            clinical_sig = "Moderate risk. Safety planning required. Consider same-day or next-day evaluation. Remove means if possible."
            urgency = "urgent"
        
        elif suicidal_thoughts == 1 and intent == 1:
            risk_level = "high"
            interpretation = "Suicidal ideation with intent"
            clinical_sig = "HIGH RISK. Immediate psychiatric evaluation required. Emergency services may be appropriate. Safety planning critical. Remove access to means."
            urgency = "emergent"
        
        elif plan == 1 or recent_behavior == 1:
            risk_level = "high"
            interpretation = "Suicidal plan and/or recent suicidal behavior"
            clinical_sig = "HIGH RISK. IMMEDIATE psychiatric evaluation required. Consider emergency department. Contact crisis services. Safety planning essential."
            urgency = "emergent"
        
        # Calculate numeric score for reference
        total_score = sum(responses)
        
        # Add specific recommendations based on responses
        recommendations = []
        if risk_level in ["moderate", "high"]:
            recommendations.append("988 Suicide & Crisis Lifeline")
            recommendations.append("Crisis Text Line: Text HOME to 741741")
            recommendations.append("Emergency services (911) if imminent risk")
        
        if intent == 1 or plan == 1 or recent_behavior == 1:
            recommendations.append("IMMEDIATE SAFETY INTERVENTION REQUIRED")
            recommendations.append("Do not leave patient alone")
            recommendations.append("Remove access to lethal means")
            recommendations.append("Emergency department evaluation strongly recommended")
        
        return ScreenerResult(
            name=self.name,
            score=total_score,
            max_score=6,
            interpretation=interpretation,
            severity=risk_level,
            clinical_significance=clinical_sig,
            item_scores=responses,
            subscales={
                "risk_level": risk_level,
                "urgency": urgency,
                "recommendations": recommendations,
                "ideation_present": suicidal_thoughts == 1,
                "plan_present": methods == 1 or plan == 1,
                "intent_present": intent == 1,
                "recent_behavior": recent_behavior == 1
            }
        )

