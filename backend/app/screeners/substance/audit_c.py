"""
AUDIT-C: Alcohol Use Disorders Identification Test - Consumption
Brief alcohol screening tool (first 3 questions of full AUDIT)

Scoring:
Men:
- 0-3: Low risk
- 4+: Possible alcohol use disorder

Women:
- 0-2: Low risk
- 3+: Possible alcohol use disorder

General threshold: ≥4 suggests hazardous drinking
"""
from typing import List
from app.screeners.base import BaseScreener, ScreenerQuestion, ScreenerResult


class AUDITC(BaseScreener):
    """AUDIT-C Alcohol Screening Tool"""
    
    @property
    def name(self) -> str:
        return "AUDIT-C"
    
    @property
    def description(self) -> str:
        return "Alcohol Use Disorders Identification Test - Consumption (brief alcohol screening)"
    
    @property
    def questions(self) -> List[ScreenerQuestion]:
        """
        AUDIT-C questions about alcohol consumption
        """
        return [
            ScreenerQuestion(
                number=1,
                text="How often do you have a drink containing alcohol?",
                options=[
                    {"value": 0, "label": "Never"},
                    {"value": 1, "label": "Monthly or less"},
                    {"value": 2, "label": "2-4 times a month"},
                    {"value": 3, "label": "2-3 times a week"},
                    {"value": 4, "label": "4 or more times a week"}
                ]
            ),
            ScreenerQuestion(
                number=2,
                text="How many standard drinks containing alcohol do you have on a typical day when drinking?",
                options=[
                    {"value": 0, "label": "1 or 2"},
                    {"value": 1, "label": "3 or 4"},
                    {"value": 2, "label": "5 or 6"},
                    {"value": 3, "label": "7 to 9"},
                    {"value": 4, "label": "10 or more"}
                ]
            ),
            ScreenerQuestion(
                number=3,
                text="How often do you have 6 or more drinks on one occasion?",
                options=[
                    {"value": 0, "label": "Never"},
                    {"value": 1, "label": "Less than monthly"},
                    {"value": 2, "label": "Monthly"},
                    {"value": 3, "label": "Weekly"},
                    {"value": 4, "label": "Daily or almost daily"}
                ]
            ),
        ]
    
    def score(self, responses: List[int]) -> ScreenerResult:
        """
        Score AUDIT-C
        
        Args:
            responses: List of 3 integers (0-4)
            
        Returns:
            ScreenerResult with score and interpretation
        """
        # Validate responses
        self.validate_responses(responses)
        
        # Calculate total score
        total_score = sum(responses)
        
        # Note: Ideally we'd ask patient's gender for gender-specific cutoffs
        # For now, using general threshold of 4
        
        # Determine risk level
        if total_score == 0:
            severity = "abstinent"
            interpretation = "No alcohol use reported"
            clinical_sig = "Patient reports abstinence from alcohol."
        elif total_score <= 3:
            severity = "low_risk"
            interpretation = "Low-risk alcohol use"
            clinical_sig = "Alcohol use within low-risk guidelines. Brief advice on safe drinking limits may be appropriate."
        elif total_score <= 7:
            severity = "hazardous"
            interpretation = "Hazardous drinking"
            clinical_sig = "Hazardous drinking pattern detected. Full AUDIT-10 recommended. Brief intervention or counseling indicated. Consider referral to substance use treatment."
        else:  # 8-12
            severity = "harmful"
            interpretation = "Harmful drinking / possible alcohol use disorder"
            clinical_sig = "High-risk drinking pattern. Full AUDIT-10 strongly recommended. Specialist evaluation for alcohol use disorder indicated. Consider detoxification assessment if daily drinking."
        
        return ScreenerResult(
            name=self.name,
            score=total_score,
            max_score=12,
            interpretation=interpretation,
            severity=severity,
            clinical_significance=clinical_sig,
            item_scores=responses,
            subscales={
                "frequency": responses[0],
                "quantity": responses[1],
                "binge_frequency": responses[2],
                "meets_threshold": total_score >= 4
            }
        )

