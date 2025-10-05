"""
CAGE-AID: CAGE Adapted to Include Drugs
4-item brief screen for substance abuse (alcohol + drugs)

Scoring: 2+ positive = likely substance use disorder
"""
from typing import List
from app.screeners.base import BaseScreener, ScreenerQuestion, ScreenerResult


class CAGEAID(BaseScreener):
    """CAGE-AID Brief Substance Abuse Screener"""
    
    @property
    def name(self) -> str:
        return "CAGE-AID"
    
    @property
    def description(self) -> str:
        return "CAGE-AID - Brief substance abuse screen (alcohol and drugs)"
    
    @property
    def questions(self) -> List[ScreenerQuestion]:
        """CAGE-AID questions (alcohol AND/OR drugs)"""
        yes_no = [
            {"value": 0, "label": "No"},
            {"value": 1, "label": "Yes"}
        ]
        
        return [
            ScreenerQuestion(
                number=1,
                text="Have you ever felt you ought to Cut down on your drinking or drug use?",
                options=yes_no
            ),
            ScreenerQuestion(
                number=2,
                text="Have people Annoyed you by criticizing your drinking or drug use?",
                options=yes_no
            ),
            ScreenerQuestion(
                number=3,
                text="Have you felt bad or Guilty about your drinking or drug use?",
                options=yes_no
            ),
            ScreenerQuestion(
                number=4,
                text="Have you ever had a drink or used drugs first thing in the morning to steady your nerves or get rid of a hangover (Eye-opener)?",
                options=yes_no
            )
        ]
    
    def score(self, responses: List[int]) -> ScreenerResult:
        """Score CAGE-AID"""
        self.validate_responses(responses)
        
        total = sum(responses)
        
        if total >= 2:
            severity = "positive"
            interpretation = "Positive screen for substance use disorder"
            clinical_sig = "CAGE-AID positive (≥2). High likelihood of alcohol or drug use disorder. Further assessment strongly recommended with AUDIT-C, DAST-10, or comprehensive substance use evaluation. Address readiness for change, harm reduction, and treatment options (counseling, medication-assisted treatment, peer support)."
        elif total == 1:
            severity = "possible"
            interpretation = "Possible substance use concern"
            clinical_sig = "CAGE-AID borderline (1 point). Some substance use concern. Further screening warranted. Brief intervention may be helpful. Monitor use patterns."
        else:
            severity = "negative"
            interpretation = "Negative screen"
            clinical_sig = "CAGE-AID negative. No current substance use disorder indicated by screening."
        
        return ScreenerResult(
            name=self.name,
            score=total,
            max_score=4,
            interpretation=interpretation,
            severity=severity,
            clinical_significance=clinical_sig,
            item_scores=responses
        )

