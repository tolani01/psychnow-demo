"""
PHQ-9: Patient Health Questionnaire-9
Depression screening tool - most widely used

Scoring:
- 0-4: Minimal depression
- 5-9: Mild depression
- 10-14: Moderate depression
- 15-19: Moderately severe depression
- 20-27: Severe depression
"""
from typing import List
from app.screeners.base import BaseScreener, ScreenerQuestion, ScreenerResult


class PHQ9(BaseScreener):
    """PHQ-9 Depression Screener"""
    
    @property
    def name(self) -> str:
        return "PHQ-9"
    
    @property
    def description(self) -> str:
        return "Patient Health Questionnaire - 9 item depression screening tool"
    
    @property
    def questions(self) -> List[ScreenerQuestion]:
        """
        PHQ-9 questions - Over the past 2 weeks, how often have you been bothered by...
        
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
                text="Little interest or pleasure in doing things",
                options=options
            ),
            ScreenerQuestion(
                number=2,
                text="Feeling down, depressed, or hopeless",
                options=options
            ),
            ScreenerQuestion(
                number=3,
                text="Trouble falling or staying asleep, or sleeping too much",
                options=options
            ),
            ScreenerQuestion(
                number=4,
                text="Feeling tired or having little energy",
                options=options
            ),
            ScreenerQuestion(
                number=5,
                text="Poor appetite or overeating",
                options=options
            ),
            ScreenerQuestion(
                number=6,
                text="Feeling bad about yourself - or that you are a failure or have let yourself or your family down",
                options=options
            ),
            ScreenerQuestion(
                number=7,
                text="Trouble concentrating on things, such as reading the newspaper or watching television",
                options=options
            ),
            ScreenerQuestion(
                number=8,
                text="Moving or speaking so slowly that other people could have noticed. Or the opposite - being so fidgety or restless that you have been moving around a lot more than usual",
                options=options
            ),
            ScreenerQuestion(
                number=9,
                text="Thoughts that you would be better off dead, or of hurting yourself in some way",
                options=options
            ),
        ]
    
    def score(self, responses: List[int]) -> ScreenerResult:
        """
        Score PHQ-9
        
        Args:
            responses: List of 9 integers (0-3)
            
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
            interpretation = "Minimal or no depression"
            clinical_sig = "Symptoms may not require treatment. Monitor."
        elif total_score <= 9:
            severity = "mild"
            interpretation = "Mild depression"
            clinical_sig = "Watchful waiting, repeat PHQ-9 at follow-up. Consider therapy."
        elif total_score <= 14:
            severity = "moderate"
            interpretation = "Moderate depression"
            clinical_sig = "Treatment plan indicated. Consider therapy and/or medication."
        elif total_score <= 19:
            severity = "moderately_severe"
            interpretation = "Moderately severe depression"
            clinical_sig = "Active treatment with therapy and medication recommended."
        else:  # 20-27
            severity = "severe"
            interpretation = "Severe depression"
            clinical_sig = "Immediate treatment with medication and therapy strongly recommended."
        
        # Check question 9 (suicidal ideation)
        suicidal_thoughts = responses[8]
        if suicidal_thoughts > 0:
            clinical_sig += f" NOTE: Patient endorsed suicidal thoughts (Q9: {suicidal_thoughts}). C-SSRS assessment recommended."
        
        return ScreenerResult(
            name=self.name,
            score=total_score,
            max_score=27,
            interpretation=interpretation,
            severity=severity,
            clinical_significance=clinical_sig,
            item_scores=responses
        )

