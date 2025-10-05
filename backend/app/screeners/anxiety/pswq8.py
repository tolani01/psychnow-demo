"""
PSWQ-8: Penn State Worry Questionnaire (Brief)
8-item measure of pathological worry

Scoring: Higher = more worry
"""
from typing import List
from app.screeners.base import BaseScreener, ScreenerQuestion, ScreenerResult


class PSWQ8(BaseScreener):
    """PSWQ-8 Worry Screener"""
    
    @property
    def name(self) -> str:
        return "PSWQ-8"
    
    @property
    def description(self) -> str:
        return "Penn State Worry Questionnaire - Brief (assesses pathological worry)"
    
    @property
    def questions(self) -> List[ScreenerQuestion]:
        options = [
            {"value": 1, "label": "Not at all typical of me"},
            {"value": 2, "label": "2"},
            {"value": 3, "label": "3"},
            {"value": 4, "label": "4"},
            {"value": 5, "label": "Very typical of me"}
        ]
        
        questions_text = [
            "My worries overwhelm me",
            "I have been a worrier all my life",
            "I notice that I have been worrying about things",
            "Once I start worrying, I cannot stop",
            "I worry all the time",
            "I worry about projects until they are all done",
            "I am always worrying about something",
            "I find it easy to dismiss worrisome thoughts"  # Reverse scored
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
        self.validate_responses(responses)
        
        # Reverse score item 8
        adjusted = responses.copy()
        adjusted[7] = 6 - adjusted[7]
        
        total = sum(adjusted)
        
        if total >= 28:
            severity = "high"
            interpretation = "High pathological worry"
            clinical_sig = "High pathological worry (≥28). Chronic excessive worry characteristic of Generalized Anxiety Disorder. CBT with worry exposure and cognitive restructuring recommended. Consider GAD-7 if not already administered."
        elif total >= 21:
            severity = "moderate"
            interpretation = "Moderate worry"
            clinical_sig = "Moderate worry levels (21-27). Significant worry affecting daily functioning. Assess for GAD. Worry management techniques recommended."
        else:
            severity = "low"
            interpretation = "Low to normal worry"
            clinical_sig = "Low worry levels (<21). Within normal range."
        
        return ScreenerResult(
            name=self.name,
            score=total,
            max_score=40,
            interpretation=interpretation,
            severity=severity,
            clinical_significance=clinical_sig,
            item_scores=responses
        )

