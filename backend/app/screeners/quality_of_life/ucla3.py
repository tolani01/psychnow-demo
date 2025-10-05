"""
UCLA-3: UCLA Loneliness Scale (3-item brief version)
Brief measure of loneliness

Scoring: 3-9, higher = more lonely
"""
from typing import List
from app.screeners.base import BaseScreener, ScreenerQuestion, ScreenerResult


class UCLA3(BaseScreener):
    """UCLA-3 Loneliness Scale"""
    
    @property
    def name(self) -> str:
        return "UCLA-3"
    
    @property
    def description(self) -> str:
        return "UCLA Loneliness Scale (3-item) - assesses loneliness"
    
    @property
    def questions(self) -> List[ScreenerQuestion]:
        options = [
            {"value": 1, "label": "Hardly ever"},
            {"value": 2, "label": "Some of the time"},
            {"value": 3, "label": "Often"}
        ]
        
        return [
            ScreenerQuestion(
                number=1,
                text="How often do you feel that you lack companionship?",
                options=options
            ),
            ScreenerQuestion(
                number=2,
                text="How often do you feel left out?",
                options=options
            ),
            ScreenerQuestion(
                number=3,
                text="How often do you feel isolated from others?",
                options=options
            )
        ]
    
    def score(self, responses: List[int]) -> ScreenerResult:
        self.validate_responses(responses)
        total = sum(responses)
        
        if total >= 7:
            severity = "high"
            interpretation = "High loneliness"
            clinical_sig = "High loneliness (≥7). Significant social isolation. Loneliness is a risk factor for depression, anxiety, and physical health problems. Interventions: social skills training, group therapy, community engagement, addressing social anxiety if present."
        elif total >= 5:
            severity = "moderate"
            interpretation = "Moderate loneliness"
            clinical_sig = "Moderate loneliness (5-6). Some social isolation present. May benefit from expanding social connections and support network."
        else:
            severity = "low"
            interpretation = "Low loneliness"
            clinical_sig = "Low loneliness (<5). Adequate social connection reported."
        
        return ScreenerResult(
            name=self.name,
            score=total,
            max_score=9,
            interpretation=interpretation,
            severity=severity,
            clinical_significance=clinical_sig,
            item_scores=responses
        )

