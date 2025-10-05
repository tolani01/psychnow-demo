"""
SPIN: Social Phobia Inventory (Brief)
17-item screening tool for social anxiety disorder

Scoring:
0-20: Minimal or no social anxiety
21-30: Mild social anxiety
31-40: Moderate social anxiety
41+: Severe social anxiety

Subscales:
- Fear (items 1, 3, 5, 10, 14, 15)
- Avoidance (items 4, 6, 8, 9, 11, 12, 16)
- Physiological (items 2, 7, 13, 17)
"""
from typing import List
from app.screeners.base import BaseScreener, ScreenerQuestion, ScreenerResult


class SPIN(BaseScreener):
    """SPIN Social Anxiety Screener"""
    
    @property
    def name(self) -> str:
        return "SPIN"
    
    @property
    def description(self) -> str:
        return "Social Phobia Inventory - screens for social anxiety disorder"
    
    @property
    def questions(self) -> List[ScreenerQuestion]:
        """SPIN questions - How much has this bothered you in the past week?"""
        options = [
            {"value": 0, "label": "Not at all"},
            {"value": 1, "label": "A little bit"},
            {"value": 2, "label": "Somewhat"},
            {"value": 3, "label": "Very much"},
            {"value": 4, "label": "Extremely"}
        ]
        
        questions_text = [
            "I am afraid of people in authority.",
            "I am bothered by blushing in front of people.",
            "Parties and social events scare me.",
            "I avoid talking to people I don't know.",
            "Being criticized scares me a lot.",
            "I avoid doing things or speaking to people for fear of embarrassment.",
            "Trembling or shaking in front of others is distressing to me.",
            "I avoid going to parties.",
            "I avoid activities in which I am the center of attention.",
            "Talking to strangers scares me.",
            "I avoid having to give speeches.",
            "I would do anything to avoid being criticized.",
            "Heart palpitations bother me when I am around people.",
            "I am afraid of doing things when people might be watching.",
            "Being embarrassed or looking stupid are among my worst fears.",
            "I avoid speaking to anyone in authority.",
            "Sweating in front of people causes me distress."
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
        Score SPIN
        
        Args:
            responses: List of 17 integers (0-4)
            
        Returns:
            ScreenerResult with subscales
        """
        # Validate responses
        self.validate_responses(responses)
        
        # Calculate total score
        total = sum(responses)
        
        # Calculate subscales (0-indexed)
        fear = sum([responses[i] for i in [0, 2, 4, 9, 13, 14]])
        avoidance = sum([responses[i] for i in [3, 5, 7, 8, 10, 11, 15]])
        physiological = sum([responses[i] for i in [1, 6, 12, 16]])
        
        # Determine severity
        if total >= 41:
            severity = "severe"
            interpretation = "Severe social anxiety"
            clinical_sig = "Severe social anxiety disorder (total ≥41). Comprehensive evaluation for Social Anxiety Disorder recommended. Evidence-based treatments include: CBT with exposure therapy, social skills training, and/or SSRI/SNRI medication. Consider referral to anxiety specialist."
        elif total >= 31:
            severity = "moderate"
            interpretation = "Moderate social anxiety"
            clinical_sig = "Moderate social anxiety (31-40). Clinical interview recommended to assess for Social Anxiety Disorder. Evidence-based treatments: cognitive-behavioral therapy focused on social anxiety, gradual exposure to feared situations. Consider medication if symptoms significantly impair functioning."
        elif total >= 21:
            severity = "mild"
            interpretation = "Mild social anxiety"
            clinical_sig = "Mild social anxiety symptoms (21-30). Further assessment recommended. CBT techniques, social skills training, and gradual exposure may be helpful. Monitor for symptom progression."
        else:
            severity = "minimal"
            interpretation = "Minimal or no social anxiety"
            clinical_sig = "No significant social anxiety symptoms identified."
        
        return ScreenerResult(
            name=self.name,
            score=total,
            max_score=68,
            interpretation=interpretation,
            severity=severity,
            clinical_significance=clinical_sig,
            item_scores=responses,
            subscales={
                "fear": fear,
                "avoidance": avoidance,
                "physiological": physiological
            }
        )

