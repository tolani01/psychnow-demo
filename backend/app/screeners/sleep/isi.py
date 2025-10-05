"""
ISI: Insomnia Severity Index
Sleep disorder screening tool

Scoring:
- 0-7: No clinically significant insomnia
- 8-14: Subthreshold insomnia
- 15-21: Moderate insomnia (clinical)
- 22-28: Severe insomnia
"""
from typing import List
from app.screeners.base import BaseScreener, ScreenerQuestion, ScreenerResult


class ISI(BaseScreener):
    """ISI Insomnia Screener"""
    
    @property
    def name(self) -> str:
        return "ISI"
    
    @property
    def description(self) -> str:
        return "Insomnia Severity Index - screens for sleep disturbances"
    
    @property
    def questions(self) -> List[ScreenerQuestion]:
        """
        ISI questions about sleep over the past 2 weeks
        """
        # Questions 1-3 use 0-4 scale
        severity_options = [
            {"value": 0, "label": "None"},
            {"value": 1, "label": "Mild"},
            {"value": 2, "label": "Moderate"},
            {"value": 3, "label": "Severe"},
            {"value": 4, "label": "Very Severe"}
        ]
        
        # Questions 4-7 use 0-4 scale with different labels
        satisfaction_options = [
            {"value": 0, "label": "Very Satisfied"},
            {"value": 1, "label": "Satisfied"},
            {"value": 2, "label": "Neutral"},
            {"value": 3, "label": "Dissatisfied"},
            {"value": 4, "label": "Very Dissatisfied"}
        ]
        
        noticeable_options = [
            {"value": 0, "label": "Not at all Noticeable"},
            {"value": 1, "label": "A Little"},
            {"value": 2, "label": "Somewhat"},
            {"value": 3, "label": "Much"},
            {"value": 4, "label": "Very Much Noticeable"}
        ]
        
        worried_options = [
            {"value": 0, "label": "Not at all Worried"},
            {"value": 1, "label": "A Little"},
            {"value": 2, "label": "Somewhat"},
            {"value": 3, "label": "Much"},
            {"value": 4, "label": "Very Much Worried"}
        ]
        
        interfering_options = [
            {"value": 0, "label": "Not at all Interfering"},
            {"value": 1, "label": "A Little"},
            {"value": 2, "label": "Somewhat"},
            {"value": 3, "label": "Much"},
            {"value": 4, "label": "Very Much Interfering"}
        ]
        
        return [
            ScreenerQuestion(
                number=1,
                text="Difficulty falling asleep",
                options=severity_options
            ),
            ScreenerQuestion(
                number=2,
                text="Difficulty staying asleep",
                options=severity_options
            ),
            ScreenerQuestion(
                number=3,
                text="Problems waking up too early",
                options=severity_options
            ),
            ScreenerQuestion(
                number=4,
                text="How satisfied/dissatisfied are you with your current sleep pattern?",
                options=satisfaction_options
            ),
            ScreenerQuestion(
                number=5,
                text="How noticeable to others do you think your sleep problem is in terms of impairing the quality of your life?",
                options=noticeable_options
            ),
            ScreenerQuestion(
                number=6,
                text="How worried/distressed are you about your current sleep problem?",
                options=worried_options
            ),
            ScreenerQuestion(
                number=7,
                text="To what extent do you consider your sleep problem to interfere with your daily functioning?",
                options=interfering_options
            ),
        ]
    
    def score(self, responses: List[int]) -> ScreenerResult:
        """
        Score ISI
        
        Args:
            responses: List of 7 integers (0-4)
            
        Returns:
            ScreenerResult with score and interpretation
        """
        # Validate responses
        self.validate_responses(responses)
        
        # Calculate total score
        total_score = sum(responses)
        
        # Determine severity
        if total_score <= 7:
            severity = "no_insomnia"
            interpretation = "No clinically significant insomnia"
            clinical_sig = "Sleep patterns appear within normal range. No specific intervention needed."
        elif total_score <= 14:
            severity = "subthreshold"
            interpretation = "Subthreshold insomnia"
            clinical_sig = "Mild sleep disturbance present. Sleep hygiene education recommended. Monitor for progression."
        elif total_score <= 21:
            severity = "moderate"
            interpretation = "Moderate insomnia (clinical)"
            clinical_sig = "Clinical insomnia present. Consider Cognitive Behavioral Therapy for Insomnia (CBT-I) as first-line treatment. Sleep medication may be considered if CBT-I unavailable or insufficient."
        else:  # 22-28
            severity = "severe"
            interpretation = "Severe insomnia"
            clinical_sig = "Severe sleep disturbance. CBT-I strongly recommended. May require combination of therapy and medication. Assess for underlying conditions (sleep apnea, restless legs, mood disorders)."
        
        return ScreenerResult(
            name=self.name,
            score=total_score,
            max_score=28,
            interpretation=interpretation,
            severity=severity,
            clinical_significance=clinical_sig,
            item_scores=responses,
            subscales={
                "sleep_onset_difficulty": responses[0],
                "sleep_maintenance_difficulty": responses[1],
                "early_awakening": responses[2],
                "sleep_satisfaction": responses[3],
                "functional_impairment": sum(responses[4:7])
            }
        )

