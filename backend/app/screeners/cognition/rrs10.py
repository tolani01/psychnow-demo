"""
RRS-10: Ruminative Response Scale (10-item brief version)
Measures ruminative thinking style

Rumination is repetitive, passive focus on negative emotions
Associated with depression and anxiety
"""
from typing import List
from app.screeners.base import BaseScreener, ScreenerQuestion, ScreenerResult


class RRS10(BaseScreener):
    """RRS-10 Rumination Scale"""
    
    @property
    def name(self) -> str:
        return "RRS-10"
    
    @property
    def description(self) -> str:
        return "Ruminative Response Scale (brief) - assesses rumination"
    
    @property
    def questions(self) -> List[ScreenerQuestion]:
        options = [
            {"value": 1, "label": "Almost never"},
            {"value": 2, "label": "Sometimes"},
            {"value": 3, "label": "Often"},
            {"value": 4, "label": "Almost always"}
        ]
        
        questions_text = [
            "Think about how alone you feel",
            "Think 'What am I doing to deserve this?'",
            "Think about your feelings of fatigue and achiness",
            "Think about how hard it is to concentrate",
            "Think 'Why do I always react this way?'",
            "Think about how passive and unmotivated you feel",
            "Analyze recent events to try to understand why you are depressed",
            "Think about how you don't seem to feel anything anymore",
            "Think 'Why can't I get going?'",
            "Think 'Why do I have problems other people don't have?'"
        ]
        
        return [
            ScreenerQuestion(
                number=i,
                text=f"When you feel down, sad, or depressed: {text}",
                options=options
            )
            for i, text in enumerate(questions_text, 1)
        ]
    
    def score(self, responses: List[int]) -> ScreenerResult:
        self.validate_responses(responses)
        total = sum(responses)
        
        if total >= 30:
            severity = "high"
            interpretation = "High rumination"
            clinical_sig = "High rumination (≥30). Excessive repetitive negative thinking. Rumination maintains and worsens depression. CBT techniques recommended: behavioral activation, thought defusion, mindfulness, rumination-focused CBT. Address underlying depression/anxiety."
        elif total >= 20:
            severity = "moderate"
            interpretation = "Moderate rumination"
            clinical_sig = "Moderate rumination (20-29). Notable ruminative thinking pattern. May benefit from mindfulness, thought interruption techniques, and behavioral activation."
        else:
            severity = "low"
            interpretation = "Low rumination"
            clinical_sig = "Low rumination (<20). Not a significant issue."
        
        return ScreenerResult(
            name=self.name,
            score=total,
            max_score=40,
            interpretation=interpretation,
            severity=severity,
            clinical_significance=clinical_sig,
            item_scores=responses
        )

