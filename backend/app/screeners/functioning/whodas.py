"""
WHODAS 2.0: WHO Disability Assessment Schedule (12-item version)
Assesses functioning and disability across 6 domains

Domains:
- Cognition (2 items)
- Mobility (2 items)
- Self-care (2 items)
- Getting along (2 items)
- Life activities (2 items)
- Participation (2 items)

Scoring: Simple sum, higher = more disability
"""
from typing import List
from app.screeners.base import BaseScreener, ScreenerQuestion, ScreenerResult


class WHODAS(BaseScreener):
    """WHODAS 2.0 Functioning Assessment"""
    
    @property
    def name(self) -> str:
        return "WHODAS 2.0"
    
    @property
    def description(self) -> str:
        return "WHO Disability Assessment Schedule - assesses functioning across life domains"
    
    @property
    def questions(self) -> List[ScreenerQuestion]:
        """WHODAS questions - In the past 30 days, how much difficulty did you have in..."""
        options = [
            {"value": 0, "label": "None"},
            {"value": 1, "label": "Mild"},
            {"value": 2, "label": "Moderate"},
            {"value": 3, "label": "Severe"},
            {"value": 4, "label": "Extreme or cannot do"}
        ]
        
        questions_text = [
            # Cognition
            "Concentrating on doing something for ten minutes?",
            "Remembering to do important things?",
            # Mobility
            "Standing for long periods such as 30 minutes?",
            "Walking a long distance such as a kilometer (or equivalent)?",
            # Self-care
            "Washing your whole body?",
            "Getting dressed?",
            # Getting along
            "Dealing with people you do not know?",
            "Maintaining a friendship?",
            # Life activities
            "Your day-to-day work?",
            "Completing your household responsibilities?",
            # Participation
            "Joining in community activities (for example, festivities, religious or other activities)?",
            "How much of a problem did you have because of barriers or hindrances in the world around you?"
        ]
        
        return [
            ScreenerQuestion(
                number=i,
                text=text,
                options=options
            )
            for i, text in enumerate(questions_text, 1)
        ]
    
    def score(self, responses: List[int]) -> ScreenerResult:
        """Score WHODAS 2.0"""
        self.validate_responses(responses)
        
        # Calculate domain scores
        cognition = sum(responses[0:2])
        mobility = sum(responses[2:4])
        self_care = sum(responses[4:6])
        getting_along = sum(responses[6:8])
        life_activities = sum(responses[8:10])
        participation = sum(responses[10:12])
        
        total = sum(responses)
        
        # Determine severity
        if total >= 32:
            severity = "severe"
            interpretation = "Severe disability/impairment"
            clinical_sig = "Severe functional impairment (≥32). Significant disability across multiple life domains. Comprehensive treatment and support services urgently needed. May require disability accommodations. Functional restoration is critical treatment goal."
        elif total >= 24:
            severity = "moderate_severe"
            interpretation = "Moderate to severe disability"
            clinical_sig = "Moderate to severe functional impairment (24-31). Substantial difficulty in daily functioning. Intensive interventions needed. Consider occupational therapy, skills training, and addressing psychiatric/medical contributors to disability."
        elif total >= 16:
            severity = "moderate"
            interpretation = "Moderate disability"
            clinical_sig = "Moderate functional impairment (16-23). Noticeable difficulty in daily activities. Treatment should include functional goals. May benefit from skills training, environmental modifications, or support services."
        elif total >= 8:
            severity = "mild"
            interpretation = "Mild disability"
            clinical_sig = "Mild functional impairment (8-15). Some difficulty with daily activities. Monitor functional status. Address modifiable factors contributing to impairment."
        else:
            severity = "none_minimal"
            interpretation = "No to minimal disability"
            clinical_sig = "Minimal or no functional impairment (<8). Generally able to perform daily activities without difficulty."
        
        return ScreenerResult(
            name=self.name,
            score=total,
            max_score=48,
            interpretation=interpretation,
            severity=severity,
            clinical_significance=clinical_sig,
            item_scores=responses,
            subscales={
                "cognition": cognition,
                "mobility": mobility,
                "self_care": self_care,
                "getting_along": getting_along,
                "life_activities": life_activities,
                "participation": participation
            }
        )

