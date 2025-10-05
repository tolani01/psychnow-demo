"""
PC-PTSD-5: Primary Care PTSD Screen for DSM-5
5-item brief PTSD screener

Scoring: 3+ positive = likely PTSD (refer for further evaluation)
"""
from typing import List
from app.screeners.base import BaseScreener, ScreenerQuestion, ScreenerResult


class PCPTSD5(BaseScreener):
    """PC-PTSD-5 Brief PTSD Screener"""
    
    @property
    def name(self) -> str:
        return "PC-PTSD-5"
    
    @property
    def description(self) -> str:
        return "Primary Care PTSD Screen - brief PTSD screener"
    
    @property
    def questions(self) -> List[ScreenerQuestion]:
        """PC-PTSD-5 questions"""
        yes_no = [
            {"value": 0, "label": "No"},
            {"value": 1, "label": "Yes"}
        ]
        
        return [
            ScreenerQuestion(
                number=1,
                text="In the past month, have you had nightmares about a stressful experience or thought about it when you did not want to?",
                options=yes_no
            ),
            ScreenerQuestion(
                number=2,
                text="In the past month, have you tried hard not to think about a stressful experience or went out of your way to avoid situations that reminded you of it?",
                options=yes_no
            ),
            ScreenerQuestion(
                number=3,
                text="In the past month, have you been constantly on guard, watchful, or easily startled?",
                options=yes_no
            ),
            ScreenerQuestion(
                number=4,
                text="In the past month, have you felt numb or detached from people, activities, or your surroundings?",
                options=yes_no
            ),
            ScreenerQuestion(
                number=5,
                text="In the past month, have you felt guilty or unable to stop blaming yourself or others for the stressful experience or what happened after it?",
                options=yes_no
            )
        ]
    
    def score(self, responses: List[int]) -> ScreenerResult:
        """Score PC-PTSD-5"""
        self.validate_responses(responses)
        
        total = sum(responses)
        
        if total >= 3:
            severity = "positive"
            interpretation = "Positive PTSD screen"
            clinical_sig = "PC-PTSD-5 positive (≥3). High likelihood of PTSD. Comprehensive trauma assessment strongly recommended with PCL-5 or clinical interview. Evidence-based trauma treatments include: Prolonged Exposure (PE), Cognitive Processing Therapy (CPT), EMDR, or trauma-focused CBT. Consider pharmacotherapy (SSRI/SNRI). Screen for suicide risk."
        elif total >= 1:
            severity = "subthreshold"
            interpretation = "Some PTSD symptoms"
            clinical_sig = "Subthreshold PTSD symptoms (1-2 positive). Some trauma-related distress present. Further evaluation may be warranted. Monitor for symptom progression. Psychoeducation about trauma responses recommended."
        else:
            severity = "negative"
            interpretation = "Negative PTSD screen"
            clinical_sig = "No current PTSD symptoms indicated. If patient has trauma history, symptoms may emerge later - follow up as needed."
        
        return ScreenerResult(
            name=self.name,
            score=total,
            max_score=5,
            interpretation=interpretation,
            severity=severity,
            clinical_significance=clinical_sig,
            item_scores=responses
        )

