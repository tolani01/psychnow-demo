"""
PHQ-2: Brief Depression Screener
First 2 questions of PHQ-9 for rapid screening

Scoring: 3+ = positive screen (administer full PHQ-9)
"""
from typing import List
from app.screeners.base import BaseScreener, ScreenerQuestion, ScreenerResult


class PHQ2(BaseScreener):
    """PHQ-2 Brief Depression Screener"""
    
    @property
    def name(self) -> str:
        return "PHQ-2"
    
    @property
    def description(self) -> str:
        return "Brief depression screener (2 items)"
    
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
                text="Over the past 2 weeks, how often have you been bothered by little interest or pleasure in doing things?",
                options=options
            ),
            ScreenerQuestion(
                number=2,
                text="Over the past 2 weeks, how often have you been bothered by feeling down, depressed, or hopeless?",
                options=options
            )
        ]
    
    def score(self, responses: List[int]) -> ScreenerResult:
        self.validate_responses(responses)
        total = sum(responses)
        
        if total >= 3:
            severity = "positive"
            interpretation = "Positive depression screen"
            clinical_sig = "PHQ-2 positive (≥3). Administer full PHQ-9 for comprehensive depression assessment. High likelihood of depressive disorder."
        else:
            severity = "negative"
            interpretation = "Negative depression screen"
            clinical_sig = "PHQ-2 negative (<3). Low likelihood of depression. If clinical concern persists, administer full PHQ-9."
        
        return ScreenerResult(
            name=self.name,
            score=total,
            max_score=6,
            interpretation=interpretation,
            severity=severity,
            clinical_significance=clinical_sig,
            item_scores=responses
        )

