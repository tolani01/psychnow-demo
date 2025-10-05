"""
SWLS: Satisfaction With Life Scale
5-item measure of global life satisfaction

Scoring:
31-35: Extremely satisfied
26-30: Satisfied
21-25: Slightly satisfied
20: Neutral
15-19: Slightly dissatisfied
10-14: Dissatisfied
5-9: Extremely dissatisfied
"""
from typing import List
from app.screeners.base import BaseScreener, ScreenerQuestion, ScreenerResult


class SWLS(BaseScreener):
    """SWLS Satisfaction With Life Scale"""
    
    @property
    def name(self) -> str:
        return "SWLS"
    
    @property
    def description(self) -> str:
        return "Satisfaction With Life Scale - assesses global life satisfaction"
    
    @property
    def questions(self) -> List[ScreenerQuestion]:
        options = [
            {"value": 1, "label": "Strongly disagree"},
            {"value": 2, "label": "Disagree"},
            {"value": 3, "label": "Slightly disagree"},
            {"value": 4, "label": "Neither agree nor disagree"},
            {"value": 5, "label": "Slightly agree"},
            {"value": 6, "label": "Agree"},
            {"value": 7, "label": "Strongly agree"}
        ]
        
        questions_text = [
            "In most ways my life is close to my ideal",
            "The conditions of my life are excellent",
            "I am satisfied with my life",
            "So far I have gotten the important things I want in life",
            "If I could live my life over, I would change almost nothing"
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
        total = sum(responses)
        
        if total >= 31:
            severity = "extremely_satisfied"
            interpretation = "Extremely satisfied with life"
            clinical_sig = "Extremely high life satisfaction (31-35). Excellent subjective well-being."
        elif total >= 26:
            severity = "satisfied"
            interpretation = "Satisfied with life"
            clinical_sig = "High life satisfaction (26-30). Good subjective well-being."
        elif total >= 21:
            severity = "slightly_satisfied"
            interpretation = "Slightly satisfied with life"
            clinical_sig = "Above average life satisfaction (21-25). Generally positive outlook."
        elif total == 20:
            severity = "neutral"
            interpretation = "Neutral life satisfaction"
            clinical_sig = "Neutral life satisfaction (20). Neither satisfied nor dissatisfied."
        elif total >= 15:
            severity = "slightly_dissatisfied"
            interpretation = "Slightly dissatisfied with life"
            clinical_sig = "Below average life satisfaction (15-19). Some dissatisfaction present. May benefit from positive psychology interventions, goal-setting, values clarification."
        elif total >= 10:
            severity = "dissatisfied"
            interpretation = "Dissatisfied with life"
            clinical_sig = "Low life satisfaction (10-14). Significant dissatisfaction. Assess for depression, unmet needs, life circumstances. Therapy may help identify and address sources of dissatisfaction."
        else:
            severity = "extremely_dissatisfied"
            interpretation = "Extremely dissatisfied with life"
            clinical_sig = "Very low life satisfaction (5-9). Extreme dissatisfaction. High priority for intervention. Screen for depression and suicidal ideation. Comprehensive mental health treatment recommended."
        
        return ScreenerResult(
            name=self.name,
            score=total,
            max_score=35,
            interpretation=interpretation,
            severity=severity,
            clinical_significance=clinical_sig,
            item_scores=responses
        )

