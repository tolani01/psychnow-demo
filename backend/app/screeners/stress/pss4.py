"""
PSS-4: Perceived Stress Scale (4-item brief version)

Scoring:
0-5: Low stress
6-7: Moderate stress
8+: High stress
"""
from typing import List
from app.screeners.base import BaseScreener, ScreenerQuestion, ScreenerResult


class PSS4(BaseScreener):
    """PSS-4 Brief Stress Screener"""
    
    @property
    def name(self) -> str:
        return "PSS-4"
    
    @property
    def description(self) -> str:
        return "Perceived Stress Scale (brief) - 4 items"
    
    @property
    def questions(self) -> List[ScreenerQuestion]:
        options = [
            {"value": 0, "label": "Never"},
            {"value": 1, "label": "Almost never"},
            {"value": 2, "label": "Sometimes"},
            {"value": 3, "label": "Fairly often"},
            {"value": 4, "label": "Very often"}
        ]
        
        return [
            ScreenerQuestion(
                number=1,
                text="In the last month, how often have you felt that you were unable to control the important things in your life?",
                options=options
            ),
            ScreenerQuestion(
                number=2,
                text="In the last month, how often have you felt confident about your ability to handle your personal problems?",  # Reverse
                options=options
            ),
            ScreenerQuestion(
                number=3,
                text="In the last month, how often have you felt that things were going your way?",  # Reverse
                options=options
            ),
            ScreenerQuestion(
                number=4,
                text="In the last month, how often have you felt difficulties were piling up so high that you could not overcome them?",
                options=options
            )
        ]
    
    def score(self, responses: List[int]) -> ScreenerResult:
        self.validate_responses(responses)
        
        # Reverse items 2 and 3
        adjusted = responses.copy()
        adjusted[1] = 4 - adjusted[1]
        adjusted[2] = 4 - adjusted[2]
        
        total = sum(adjusted)
        
        if total >= 8:
            severity = "high"
            interpretation = "High perceived stress"
            clinical_sig = "High stress (≥8). Significant stress impacting coping. Stress management interventions recommended."
        elif total >= 6:
            severity = "moderate"
            interpretation = "Moderate stress"
            clinical_sig = "Moderate stress (6-7). Some stress management strategies may be helpful."
        else:
            severity = "low"
            interpretation = "Low stress"
            clinical_sig = "Low stress (<6). Generally managing well."
        
        return ScreenerResult(
            name=self.name,
            score=total,
            max_score=16,
            interpretation=interpretation,
            severity=severity,
            clinical_significance=clinical_sig,
            item_scores=responses
        )

