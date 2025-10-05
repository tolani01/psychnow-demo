"""
PSS-10: Perceived Stress Scale (10-item version)
Measures the degree to which situations in one's life are appraised as stressful

Scoring:
0-13: Low stress
14-26: Moderate stress
27-40: High perceived stress

Note: Items 4, 5, 7, 8 are reverse-scored
"""
from typing import List
from app.screeners.base import BaseScreener, ScreenerQuestion, ScreenerResult


class PSS10(BaseScreener):
    """PSS-10 Perceived Stress Scale"""
    
    @property
    def name(self) -> str:
        return "PSS-10"
    
    @property
    def description(self) -> str:
        return "Perceived Stress Scale - measures perceived stress levels"
    
    @property
    def questions(self) -> List[ScreenerQuestion]:
        """PSS-10 questions - In the last month, how often have you..."""
        options = [
            {"value": 0, "label": "Never"},
            {"value": 1, "label": "Almost never"},
            {"value": 2, "label": "Sometimes"},
            {"value": 3, "label": "Fairly often"},
            {"value": 4, "label": "Very often"}
        ]
        
        questions_text = [
            "been upset because of something that happened unexpectedly?",
            "felt that you were unable to control the important things in your life?",
            "felt nervous and stressed?",
            "felt confident about your ability to handle your personal problems?",  # Reverse
            "felt that things were going your way?",  # Reverse
            "found that you could not cope with all the things that you had to do?",
            "been able to control irritations in your life?",  # Reverse
            "felt that you were on top of things?",  # Reverse
            "been angered because of things that happened that were outside of your control?",
            "felt difficulties were piling up so high that you could not overcome them?"
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
        Score PSS-10
        
        Args:
            responses: List of 10 integers (0-4)
            
        Returns:
            ScreenerResult with interpretation
        """
        # Validate responses
        self.validate_responses(responses)
        
        # Reverse score items 4, 5, 7, 8 (indices 3, 4, 6, 7)
        reverse_items = [3, 4, 6, 7]
        adjusted = responses.copy()
        for idx in reverse_items:
            adjusted[idx] = 4 - adjusted[idx]
        
        # Calculate total
        total = sum(adjusted)
        
        # Determine severity
        if total >= 27:
            severity = "high"
            interpretation = "High perceived stress"
            clinical_sig = "High stress levels (≥27). Patient reports feeling overwhelmed and unable to cope with demands. Assess for burnout, anxiety, depression. Stress management interventions strongly recommended: CBT, mindfulness, relaxation techniques, problem-solving therapy. Address contributing stressors (work, relationships, financial, health). Consider need for medication if co-occurring anxiety/depression."
        elif total >= 14:
            severity = "moderate"
            interpretation = "Moderate perceived stress"
            clinical_sig = "Moderate stress levels (14-26). Patient experiencing significant stress but with some coping capacity. Recommend stress management strategies: identify stressors, develop coping skills, improve self-care. Monitor for development of stress-related disorders."
        else:
            severity = "low"
            interpretation = "Low perceived stress"
            clinical_sig = "Low stress levels (<14). Patient reports generally managing life demands well. Continue current coping strategies."
        
        return ScreenerResult(
            name=self.name,
            score=total,
            max_score=40,
            interpretation=interpretation,
            severity=severity,
            clinical_significance=clinical_sig,
            item_scores=responses
        )

