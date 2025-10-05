"""
SCOFF: Brief Eating Disorder Screening Tool

Screens for anorexia nervosa and bulimia nervosa
Score ≥2 indicates possible eating disorder

Questions:
S - Do you make yourself Sick because you feel uncomfortably full?
C - Do you worry you have lost Control over how much you eat?
O - Have you recently lost more than One stone (14 lbs) in a three-month period?
F - Do you believe yourself to be Fat when others say you are too thin?
F - Would you say that Food dominates your life?
"""
from typing import List
from app.screeners.base import BaseScreener, ScreenerQuestion, ScreenerResult


class SCOFF(BaseScreener):
    """SCOFF Eating Disorder Screener"""
    
    @property
    def name(self) -> str:
        return "SCOFF"
    
    @property
    def description(self) -> str:
        return "Brief screening tool for eating disorders (anorexia and bulimia)"
    
    @property
    def questions(self) -> List[ScreenerQuestion]:
        """SCOFF questions"""
        yes_no = [
            {"value": 0, "label": "No"},
            {"value": 1, "label": "Yes"}
        ]
        
        questions_text = [
            "Do you make yourself Sick (vomit) because you feel uncomfortably full?",
            "Do you worry you have lost Control over how much you eat?",
            "Have you recently lost more than 14 pounds (One stone) in a 3-month period?",
            "Do you believe yourself to be Fat when others say you are too thin?",
            "Would you say that Food dominates your life?"
        ]
        
        return [
            ScreenerQuestion(
                number=i,
                text=text,
                options=yes_no
            )
            for i, text in enumerate(questions_text, 1)
        ]
    
    def score(self, responses: List[int]) -> ScreenerResult:
        """
        Score SCOFF
        
        Args:
            responses: List of 5 integers (0 or 1)
            
        Returns:
            ScreenerResult with interpretation
        """
        # Validate responses
        self.validate_responses(responses)
        
        # Calculate total score
        total = sum(responses)
        
        # Determine severity and interpretation
        if total >= 2:
            severity = "positive_screen"
            interpretation = "Positive screen for eating disorder"
            clinical_sig = "SCOFF positive (≥2 points). Significant concern for eating disorder (anorexia nervosa, bulimia nervosa, or EDNOS). Comprehensive eating disorder assessment recommended. Assess: weight history, eating patterns, compensatory behaviors (purging, laxatives, excessive exercise), body image distortion, and medical complications (electrolyte imbalance, cardiac issues). Consider referral to eating disorder specialist."
        elif total == 1:
            severity = "mild"
            interpretation = "Some eating concerns present"
            clinical_sig = "Subthreshold eating concerns. Further assessment warranted to clarify severity and type. Explore eating patterns, body image, weight fluctuations, and any compensatory behaviors. Monitor for progression of symptoms."
        else:
            severity = "negative"
            interpretation = "Negative screen for eating disorder"
            clinical_sig = "No significant eating disorder symptoms identified on screening. Continue to monitor if risk factors present (perfectionism, body dissatisfaction, history of dieting)."
        
        # Provide detailed breakdown
        concern_areas = []
        if responses[0] == 1:
            concern_areas.append("self-induced vomiting")
        if responses[1] == 1:
            concern_areas.append("loss of control over eating")
        if responses[2] == 1:
            concern_areas.append("significant recent weight loss")
        if responses[3] == 1:
            concern_areas.append("body image distortion")
        if responses[4] == 1:
            concern_areas.append("preoccupation with food")
        
        return ScreenerResult(
            name=self.name,
            score=total,
            max_score=5,
            interpretation=interpretation,
            severity=severity,
            clinical_significance=clinical_sig,
            item_scores=responses,
            subscales={
                "concern_areas": concern_areas,
                "positive_screen": total >= 2
            }
        )

