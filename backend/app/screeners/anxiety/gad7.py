"""
GAD-7: Generalized Anxiety Disorder-7
Anxiety screening tool

Scoring:
- 0-4: Minimal anxiety
- 5-9: Mild anxiety
- 10-14: Moderate anxiety
- 15-21: Severe anxiety
"""
from typing import List
from app.screeners.base import BaseScreener, ScreenerQuestion, ScreenerResult


class GAD7(BaseScreener):
    """GAD-7 Anxiety Screener"""
    
    @property
    def name(self) -> str:
        return "GAD-7"
    
    @property
    def description(self) -> str:
        return "Generalized Anxiety Disorder - 7 item anxiety screening tool"
    
    @property
    def questions(self) -> List[ScreenerQuestion]:
        """
        GAD-7 questions - Over the past 2 weeks, how often have you been bothered by...
        
        Response options: 0=Not at all, 1=Several days, 2=More than half the days, 3=Nearly every day
        """
        options = [
            {"value": 0, "label": "Not at all"},
            {"value": 1, "label": "Several days"},
            {"value": 2, "label": "More than half the days"},
            {"value": 3, "label": "Nearly every day"}
        ]
        
        return [
            ScreenerQuestion(
                number=1,
                text="Feeling nervous, anxious, or on edge",
                options=options
            ),
            ScreenerQuestion(
                number=2,
                text="Not being able to stop or control worrying",
                options=options
            ),
            ScreenerQuestion(
                number=3,
                text="Worrying too much about different things",
                options=options
            ),
            ScreenerQuestion(
                number=4,
                text="Trouble relaxing",
                options=options
            ),
            ScreenerQuestion(
                number=5,
                text="Being so restless that it's hard to sit still",
                options=options
            ),
            ScreenerQuestion(
                number=6,
                text="Becoming easily annoyed or irritable",
                options=options
            ),
            ScreenerQuestion(
                number=7,
                text="Feeling afraid as if something awful might happen",
                options=options
            ),
        ]
    
    def score(self, responses: List[int]) -> ScreenerResult:
        """
        Score GAD-7
        
        Args:
            responses: List of 7 integers (0-3)
            
        Returns:
            ScreenerResult with score and interpretation
        """
        # Validate responses
        self.validate_responses(responses)
        
        # Calculate total score
        total_score = sum(responses)
        
        # Determine severity
        if total_score <= 4:
            severity = "minimal"
            interpretation = "Minimal anxiety"
            clinical_sig = "Symptoms may not require treatment. Monitor."
        elif total_score <= 9:
            severity = "mild"
            interpretation = "Mild anxiety"
            clinical_sig = "Watchful waiting, consider therapy if symptoms persist."
        elif total_score <= 14:
            severity = "moderate"
            interpretation = "Moderate anxiety"
            clinical_sig = "Treatment plan indicated. Therapy recommended, consider medication."
        else:  # 15-21
            severity = "severe"
            interpretation = "Severe anxiety"
            clinical_sig = "Active treatment with therapy and medication strongly recommended."
        
        return ScreenerResult(
            name=self.name,
            score=total_score,
            max_score=21,
            interpretation=interpretation,
            severity=severity,
            clinical_significance=clinical_sig,
            item_scores=responses
        )

