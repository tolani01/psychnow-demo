"""
WSAS: Work and Social Adjustment Scale
5-item measure of functional impairment

Scoring:
0-10: Subclinical
10-20: Significant functional impairment
20-40: Severe impairment
"""
from typing import List
from app.screeners.base import BaseScreener, ScreenerQuestion, ScreenerResult


class WSAS(BaseScreener):
    """WSAS Work and Social Adjustment Scale"""
    
    @property
    def name(self) -> str:
        return "WSAS"
    
    @property
    def description(self) -> str:
        return "Work and Social Adjustment Scale - brief functional impairment measure"
    
    @property
    def questions(self) -> List[ScreenerQuestion]:
        """WSAS questions - How much does your [mental health condition] impair your ability to..."""
        options = [
            {"value": 0, "label": "Not at all"},
            {"value": 1, "label": "1"},
            {"value": 2, "label": "2"},
            {"value": 3, "label": "3"},
            {"value": 4, "label": "4"},
            {"value": 5, "label": "5"},
            {"value": 6, "label": "6"},
            {"value": 7, "label": "7"},
            {"value": 8, "label": "Very severely"}
        ]
        
        questions_text = [
            "carry out your work? (If unemployed, rate how your symptoms would affect your work)",
            "manage your home? (cleaning, tidying, shopping, cooking, bills, childcare, etc.)",
            "form and maintain close relationships with others? (family, friends, romantic relationships)",
            "engage in social leisure activities? (hobbies, seeing friends, going out)",
            "engage in private leisure activities? (activities done alone, like reading, watching TV, exercise)"
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
        """Score WSAS"""
        self.validate_responses(responses)
        
        total = sum(responses)
        
        if total >= 20:
            severity = "severe"
            interpretation = "Severe functional impairment"
            clinical_sig = "Severe functional impairment (≥20). Mental health symptoms are severely disrupting work, home, relationships, and leisure activities. Urgent psychiatric intervention needed. Functional restoration should be primary treatment goal."
        elif total >= 10:
            severity = "significant"
            interpretation = "Significant functional impairment"
            clinical_sig = "Significant functional impairment (10-19). Mental health symptoms are notably affecting daily functioning across multiple domains. Active treatment indicated. Consider skills training, supported employment, or occupational therapy in addition to psychiatric treatment."
        else:
            severity = "subclinical"
            interpretation = "Subclinical impairment"
            clinical_sig = "Minimal functional impairment (<10). Symptoms have limited impact on daily functioning."
        
        return ScreenerResult(
            name=self.name,
            score=total,
            max_score=40,
            interpretation=interpretation,
            severity=severity,
            clinical_significance=clinical_sig,
            item_scores=responses
        )

