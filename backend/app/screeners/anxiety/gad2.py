"""
GAD-2: Brief Anxiety Screener
First 2 questions of GAD-7 for rapid screening

Scoring: 3+ = positive screen (administer full GAD-7)
"""
from typing import List
from app.screeners.base import BaseScreener, ScreenerQuestion, ScreenerResult


class GAD2(BaseScreener):
    """GAD-2 Brief Anxiety Screener"""
    
    @property
    def name(self) -> str:
        return "GAD-2"
    
    @property
    def description(self) -> str:
        return "Brief anxiety screener (2 items)"
    
    @property
    def questions(self) -> List[ScreenerQuestion]:
        options = [
            {"value": 0, "label": "Not at all"},
            {"value": 1, "label": "Several days"},
            {"value": 2, "label": "More than half the days"},
            {"value": 3, "label": "Nearly every day"}
        ]
        
        return [
            ScreenerQuestion(
                number=1,
                text="Over the past 2 weeks, how often have you been bothered by feeling nervous, anxious, or on edge?",
                options=options
            ),
            ScreenerQuestion(
                number=2,
                text="Over the past 2 weeks, how often have you been bothered by not being able to stop or control worrying?",
                options=options
            )
        ]
    
    def score(self, responses: List[int]) -> ScreenerResult:
        self.validate_responses(responses)
        total = sum(responses)
        
        if total >= 3:
            severity = "positive"
            interpretation = "Positive anxiety screen"
            clinical_sig = "GAD-2 positive (≥3). Administer full GAD-7 for comprehensive anxiety assessment. High likelihood of anxiety disorder."
        else:
            severity = "negative"
            interpretation = "Negative anxiety screen"
            clinical_sig = "GAD-2 negative (<3). Low likelihood of anxiety disorder. If clinical concern persists, administer full GAD-7."
        
        return ScreenerResult(
            name=self.name,
            score=total,
            max_score=6,
            interpretation=interpretation,
            severity=severity,
            clinical_significance=clinical_sig,
            item_scores=responses
        )

