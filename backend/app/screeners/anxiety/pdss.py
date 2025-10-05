"""
PDSS: Panic Disorder Severity Scale
7-item clinician or self-rated scale for panic disorder severity

Scoring:
0-5: Subclinical
6-9: Mild
10-13: Moderate
14+: Severe panic disorder
"""
from typing import List
from app.screeners.base import BaseScreener, ScreenerQuestion, ScreenerResult


class PDSS(BaseScreener):
    """PDSS Panic Disorder Severity Scale"""
    
    @property
    def name(self) -> str:
        return "PDSS"
    
    @property
    def description(self) -> str:
        return "Panic Disorder Severity Scale - assesses panic disorder severity"
    
    @property
    def questions(self) -> List[ScreenerQuestion]:
        """PDSS questions - Over the past month..."""
        options_frequency = [
            {"value": 0, "label": "None"},
            {"value": 1, "label": "Mild"},
            {"value": 2, "label": "Moderate"},
            {"value": 3, "label": "Severe"},
            {"value": 4, "label": "Extreme"}
        ]
        
        return [
            ScreenerQuestion(
                number=1,
                text="How many panic and limited symptom attacks did you have?",
                options=[
                    {"value": 0, "label": "None"},
                    {"value": 1, "label": "1-2"},
                    {"value": 2, "label": "3-5"},
                    {"value": 3, "label": "6-10"},
                    {"value": 4, "label": "11 or more"}
                ]
            ),
            ScreenerQuestion(
                number=2,
                text="If you had any panic attacks, how distressing were they?",
                options=options_frequency
            ),
            ScreenerQuestion(
                number=3,
                text="How much do you worry or feel anxious about when your next panic attack will occur or about fears related to the attacks?",
                options=options_frequency
            ),
            ScreenerQuestion(
                number=4,
                text="Were there places or situations you avoided, or felt afraid of, because of panic attacks?",
                options=options_frequency
            ),
            ScreenerQuestion(
                number=5,
                text="Were there any physical symptoms that frightened you during your panic attacks?",
                options=options_frequency
            ),
            ScreenerQuestion(
                number=6,
                text="During the past month, how much did the panic disorder interfere with your ability to work or carry out responsibilities at home?",
                options=options_frequency
            ),
            ScreenerQuestion(
                number=7,
                text="During the past month, how much did panic disorder interfere with your social life?",
                options=options_frequency
            )
        ]
    
    def score(self, responses: List[int]) -> ScreenerResult:
        """Score PDSS"""
        self.validate_responses(responses)
        
        total = sum(responses)
        
        if total >= 14:
            severity = "severe"
            interpretation = "Severe panic disorder"
            clinical_sig = "Severe panic disorder (≥14). Significant panic symptoms with substantial functional impairment and avoidance. Evidence-based treatments strongly recommended: CBT with interoceptive exposure, panic-focused therapy, and/or SSRI/SNRI medication. May need intensive treatment."
        elif total >= 10:
            severity = "moderate"
            interpretation = "Moderate panic disorder"
            clinical_sig = "Moderate panic disorder (10-13). Frequent panic attacks with moderate distress and some avoidance. CBT with exposure therapy recommended. Consider pharmacotherapy (SSRI/SNRI) if symptoms are functionally impairing."
        elif total >= 6:
            severity = "mild"
            interpretation = "Mild panic disorder"
            clinical_sig = "Mild panic disorder (6-9). Some panic attacks with mild distress. Psychotherapy (CBT) recommended as first-line treatment. Teach panic management skills and breathing techniques."
        else:
            severity = "subclinical"
            interpretation = "Subclinical or no panic disorder"
            clinical_sig = "Minimal panic symptoms (<6). May not meet criteria for panic disorder. Monitor if symptoms are new or worsening."
        
        return ScreenerResult(
            name=self.name,
            score=total,
            max_score=28,
            interpretation=interpretation,
            severity=severity,
            clinical_significance=clinical_sig,
            item_scores=responses
        )

