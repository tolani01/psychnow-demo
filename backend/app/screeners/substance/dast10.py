"""
DAST-10: Drug Abuse Screening Test (10-item version)
Screens for drug use problems (excluding alcohol and tobacco)

Scoring:
0: No problems reported
1-2: Low level (monitor)
3-5: Moderate level (further investigation)
6-8: Substantial level (intensive assessment)
9-10: Severe level (intensive assessment)
"""
from typing import List
from app.screeners.base import BaseScreener, ScreenerQuestion, ScreenerResult


class DAST10(BaseScreener):
    """DAST-10 Drug Abuse Screener"""
    
    @property
    def name(self) -> str:
        return "DAST-10"
    
    @property
    def description(self) -> str:
        return "Drug Abuse Screening Test - screens for drug use problems"
    
    @property
    def questions(self) -> List[ScreenerQuestion]:
        """
        DAST-10 questions
        The following questions concern information about your possible involvement with drugs 
        not including alcoholic beverages during the past 12 months.
        """
        yes_no = [
            {"value": 0, "label": "No"},
            {"value": 1, "label": "Yes"}
        ]
        
        questions_text = [
            "Have you used drugs other than those required for medical reasons?",
            "Do you abuse more than one drug at a time?",
            "Are you always able to stop using drugs when you want to? (If never use drugs, answer 'Yes')",
            "Have you had 'blackouts' or 'flashbacks' as a result of drug use?",
            "Do you ever feel bad or guilty about your drug use?",
            "Does your spouse (or parents) ever complain about your involvement with drugs?",
            "Have you neglected your family because of your use of drugs?",
            "Have you engaged in illegal activities in order to obtain drugs?",
            "Have you ever experienced withdrawal symptoms (felt sick) when you stopped taking drugs?",
            "Have you had medical problems as a result of your drug use (e.g. memory loss, hepatitis, convulsions, bleeding)?"
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
        Score DAST-10
        
        Args:
            responses: List of 10 integers (0 or 1)
            
        Returns:
            ScreenerResult with interpretation
        
        Note: Question 3 is reverse-scored (No = 1 point, Yes = 0 points)
        """
        # Validate responses
        self.validate_responses(responses)
        
        # Calculate total score (Question 3 is reverse-scored)
        total = sum(responses[:2])  # Q1, Q2
        total += (1 - responses[2])  # Q3 (reverse)
        total += sum(responses[3:])  # Q4-Q10
        
        # Determine severity
        if total == 0:
            severity = "none"
            interpretation = "No drug abuse problems reported"
            clinical_sig = "No current drug use problems identified. Continue monitoring if risk factors present."
        elif total <= 2:
            severity = "low"
            interpretation = "Low level of drug-related problems"
            clinical_sig = "Low-level drug use concerns. Consider brief intervention, motivational interviewing, and monitoring. Assess readiness for change."
        elif total <= 5:
            severity = "moderate"
            interpretation = "Moderate level of drug-related problems"
            clinical_sig = "Moderate substance use problems. Further investigation warranted. Consider referral to substance use disorder specialist. Assess for co-occurring mental health conditions."
        elif total <= 8:
            severity = "substantial"
            interpretation = "Substantial level of drug-related problems"
            clinical_sig = "Substantial substance use disorder indicated. Intensive assessment and treatment recommended. Refer to addiction specialist. Address medical complications, withdrawal risk, and social support needs."
        else:  # 9-10
            severity = "severe"
            interpretation = "Severe level of drug-related problems"
            clinical_sig = "Severe substance use disorder. Immediate comprehensive assessment required. High priority for intensive treatment (may need inpatient/residential level of care). Assess for medical complications, withdrawal risk, and safety concerns."
        
        return ScreenerResult(
            name=self.name,
            score=total,
            max_score=10,
            interpretation=interpretation,
            severity=severity,
            clinical_significance=clinical_sig,
            item_scores=responses
        )

