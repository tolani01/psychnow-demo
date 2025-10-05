"""
BIS-15: Barratt Impulsiveness Scale (15-item short form)
Measures impulsivity across 3 dimensions

Subscales:
- Attention (5 items)
- Motor (5 items)
- Non-Planning (5 items)
"""
from typing import List
from app.screeners.base import BaseScreener, ScreenerQuestion, ScreenerResult


class BIS15(BaseScreener):
    """BIS-15 Impulsivity Scale"""
    
    @property
    def name(self) -> str:
        return "BIS-15"
    
    @property
    def description(self) -> str:
        return "Barratt Impulsiveness Scale (short) - assesses impulsivity"
    
    @property
    def questions(self) -> List[ScreenerQuestion]:
        options = [
            {"value": 1, "label": "Rarely/Never"},
            {"value": 2, "label": "Occasionally"},
            {"value": 3, "label": "Often"},
            {"value": 4, "label": "Almost Always/Always"}
        ]
        
        questions_text = [
            # Attention
            "I don't pay attention",
            "I concentrate easily",  # Reverse
            "I am self-controlled",  # Reverse
            "I have 'racing' thoughts",
            "I squirm at lectures or talks",
            # Motor
            "I act on impulse",
            "I do things without thinking",
            "I act on the spur of the moment",
            "I buy things on impulse",
            "I say things without thinking",
            # Non-Planning
            "I plan tasks carefully",  # Reverse
            "I am a careful thinker",  # Reverse
            "I plan trips well ahead of time",  # Reverse
            "I am future oriented",  # Reverse
            "I change jobs"
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
        
        # Reverse score items 2, 3, 11, 12, 13, 14 (indices 1, 2, 10, 11, 12, 13)
        adjusted = responses.copy()
        reverse_items = [1, 2, 10, 11, 12, 13]
        for idx in reverse_items:
            adjusted[idx] = 5 - adjusted[idx]
        
        # Calculate subscales
        attention = sum(adjusted[0:5])
        motor = sum(adjusted[5:10])
        non_planning = sum(adjusted[10:15])
        
        total = sum(adjusted)
        
        if total >= 40:
            severity = "high"
            interpretation = "High impulsivity"
            clinical_sig = "High impulsivity (≥40). Significant impulsive behavior across domains. Associated with ADHD, bipolar disorder, substance use, borderline personality disorder. Assess for these conditions. DBT skills training (distress tolerance, emotion regulation) may be helpful."
        elif total >= 30:
            severity = "moderate"
            interpretation = "Moderate impulsivity"
            clinical_sig = "Moderate impulsivity (30-39). Notable impulsive tendencies. May benefit from impulse control strategies and self-monitoring."
        else:
            severity = "low"
            interpretation = "Low to normal impulsivity"
            clinical_sig = "Low impulsivity (<30). Within normal range."
        
        return ScreenerResult(
            name=self.name,
            score=total,
            max_score=60,
            interpretation=interpretation,
            severity=severity,
            clinical_significance=clinical_sig,
            item_scores=responses,
            subscales={
                "attention": attention,
                "motor": motor,
                "non_planning": non_planning
            }
        )

