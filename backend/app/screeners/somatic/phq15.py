"""
PHQ-15: Patient Health Questionnaire - Somatic Symptoms
Screens for somatic symptom severity

Scoring:
0-4: Minimal
5-9: Low
10-14: Medium
15-30: High somatic symptom severity
"""
from typing import List
from app.screeners.base import BaseScreener, ScreenerQuestion, ScreenerResult


class PHQ15(BaseScreener):
    """PHQ-15 Somatic Symptom Screener"""
    
    @property
    def name(self) -> str:
        return "PHQ-15"
    
    @property
    def description(self) -> str:
        return "Patient Health Questionnaire - Somatic Symptoms (screens for physical symptom burden)"
    
    @property
    def questions(self) -> List[ScreenerQuestion]:
        """PHQ-15 questions - Over the past 2 weeks, how much have you been bothered by..."""
        options = [
            {"value": 0, "label": "Not bothered at all"},
            {"value": 1, "label": "Bothered a little"},
            {"value": 2, "label": "Bothered a lot"}
        ]
        
        questions_text = [
            "Stomach pain",
            "Back pain",
            "Pain in your arms, legs, or joints",
            "Menstrual cramps or other problems with your periods (women only)",
            "Headaches",
            "Chest pain",
            "Dizziness",
            "Fainting spells",
            "Feeling your heart pound or race",
            "Shortness of breath",
            "Pain or problems during sexual intercourse",
            "Constipation, loose bowels, or diarrhea",
            "Nausea, gas, or indigestion",
            "Feeling tired or having low energy",
            "Trouble sleeping"
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
        """
        Score PHQ-15
        
        Args:
            responses: List of 15 integers (0-2)
            
        Returns:
            ScreenerResult with interpretation
        """
        # Validate responses
        self.validate_responses(responses)
        
        # Calculate total score
        total = sum(responses)
        
        # Determine severity
        if total >= 15:
            severity = "high"
            interpretation = "High somatic symptom severity"
            clinical_sig = "High somatic symptom burden (≥15). Multiple physical symptoms significantly affecting daily life. Comprehensive medical evaluation recommended to rule out underlying medical conditions. High overlap with anxiety and depression - screen for psychiatric conditions. Consider Somatic Symptom Disorder if symptoms persist without medical explanation. CBT for somatic symptoms may be helpful."
        elif total >= 10:
            severity = "medium"
            interpretation = "Medium somatic symptom severity"
            clinical_sig = "Medium somatic symptom severity (10-14). Significant physical symptom burden. Medical evaluation recommended. Assess for co-occurring anxiety, depression, or pain disorders. May benefit from integrated medical-psychiatric care."
        elif total >= 5:
            severity = "low"
            interpretation = "Low somatic symptom severity"
            clinical_sig = "Low somatic symptom severity (5-9). Some physical symptoms present. Monitor for symptom progression. Consider medical evaluation if symptoms are new or worsening."
        else:
            severity = "minimal"
            interpretation = "Minimal somatic symptoms"
            clinical_sig = "Minimal somatic symptom burden (<5). No significant physical symptom concerns."
        
        return ScreenerResult(
            name=self.name,
            score=total,
            max_score=30,
            interpretation=interpretation,
            severity=severity,
            clinical_significance=clinical_sig,
            item_scores=responses
        )

