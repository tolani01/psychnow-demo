"""
EPDS: Edinburgh Postnatal Depression Scale
10-item screen for perinatal depression (pregnancy and postpartum)

Scoring:
0-9: Low likelihood of depression
10-12: Possible depression
13+: Fairly high possibility of depression
Item 10 > 0: Suicidal ideation (immediate follow-up)
"""
from typing import List
from app.screeners.base import BaseScreener, ScreenerQuestion, ScreenerResult


class EPDS(BaseScreener):
    """EPDS Edinburgh Postnatal Depression Scale"""
    
    @property
    def name(self) -> str:
        return "EPDS"
    
    @property
    def description(self) -> str:
        return "Edinburgh Postnatal Depression Scale - screens for perinatal depression"
    
    @property
    def questions(self) -> List[ScreenerQuestion]:
        """EPDS questions - In the past 7 days..."""
        return [
            ScreenerQuestion(
                number=1,
                text="I have been able to laugh and see the funny side of things",
                options=[
                    {"value": 0, "label": "As much as I always could"},
                    {"value": 1, "label": "Not quite so much now"},
                    {"value": 2, "label": "Definitely not so much now"},
                    {"value": 3, "label": "Not at all"}
                ]
            ),
            ScreenerQuestion(
                number=2,
                text="I have looked forward with enjoyment to things",
                options=[
                    {"value": 0, "label": "As much as I ever did"},
                    {"value": 1, "label": "Rather less than I used to"},
                    {"value": 2, "label": "Definitely less than I used to"},
                    {"value": 3, "label": "Hardly at all"}
                ]
            ),
            ScreenerQuestion(
                number=3,
                text="I have blamed myself unnecessarily when things went wrong",
                options=[
                    {"value": 3, "label": "Yes, most of the time"},
                    {"value": 2, "label": "Yes, some of the time"},
                    {"value": 1, "label": "Not very often"},
                    {"value": 0, "label": "No, never"}
                ]
            ),
            ScreenerQuestion(
                number=4,
                text="I have been anxious or worried for no good reason",
                options=[
                    {"value": 0, "label": "No, not at all"},
                    {"value": 1, "label": "Hardly ever"},
                    {"value": 2, "label": "Yes, sometimes"},
                    {"value": 3, "label": "Yes, very often"}
                ]
            ),
            ScreenerQuestion(
                number=5,
                text="I have felt scared or panicky for no very good reason",
                options=[
                    {"value": 3, "label": "Yes, quite a lot"},
                    {"value": 2, "label": "Yes, sometimes"},
                    {"value": 1, "label": "No, not much"},
                    {"value": 0, "label": "No, not at all"}
                ]
            ),
            ScreenerQuestion(
                number=6,
                text="Things have been getting on top of me",
                options=[
                    {"value": 3, "label": "Yes, most of the time I haven't been able to cope at all"},
                    {"value": 2, "label": "Yes, sometimes I haven't been coping as well as usual"},
                    {"value": 1, "label": "No, most of the time I have coped quite well"},
                    {"value": 0, "label": "No, I have been coping as well as ever"}
                ]
            ),
            ScreenerQuestion(
                number=7,
                text="I have been so unhappy that I have had difficulty sleeping",
                options=[
                    {"value": 3, "label": "Yes, most of the time"},
                    {"value": 2, "label": "Yes, sometimes"},
                    {"value": 1, "label": "Not very often"},
                    {"value": 0, "label": "No, not at all"}
                ]
            ),
            ScreenerQuestion(
                number=8,
                text="I have felt sad or miserable",
                options=[
                    {"value": 3, "label": "Yes, most of the time"},
                    {"value": 2, "label": "Yes, quite often"},
                    {"value": 1, "label": "Not very often"},
                    {"value": 0, "label": "No, not at all"}
                ]
            ),
            ScreenerQuestion(
                number=9,
                text="I have been so unhappy that I have been crying",
                options=[
                    {"value": 3, "label": "Yes, most of the time"},
                    {"value": 2, "label": "Yes, quite often"},
                    {"value": 1, "label": "Only occasionally"},
                    {"value": 0, "label": "No, never"}
                ]
            ),
            ScreenerQuestion(
                number=10,
                text="The thought of harming myself has occurred to me",
                options=[
                    {"value": 3, "label": "Yes, quite often"},
                    {"value": 2, "label": "Sometimes"},
                    {"value": 1, "label": "Hardly ever"},
                    {"value": 0, "label": "Never"}
                ]
            )
        ]
    
    def score(self, responses: List[int]) -> ScreenerResult:
        """Score EPDS"""
        self.validate_responses(responses)
        
        total = sum(responses)
        suicidal_item = responses[9]  # Item 10
        
        if suicidal_item > 0:
            severity = "high_risk"
            interpretation = "🚨 Suicidal thoughts present - immediate follow-up required"
            clinical_sig = "🚨 CRITICAL: Patient endorsed thoughts of self-harm (Item 10 positive). IMMEDIATE suicide risk assessment required. Do not delay. Consider emergency evaluation if imminent risk. Perinatal depression with suicidal ideation requires urgent psychiatric consultation and safety planning."
        elif total >= 13:
            severity = "likely_depression"
            interpretation = "Likely perinatal depression"
            clinical_sig = "High likelihood of perinatal depression (≥13). Comprehensive psychiatric evaluation recommended. Evidence-based treatments: interpersonal psychotherapy (IPT), CBT, or antidepressant medication if indicated. For postpartum depression, consider mother-infant interventions. Screen for bipolar disorder (postpartum onset is common). Assess infant bonding and safety."
        elif total >= 10:
            severity = "possible_depression"
            interpretation = "Possible perinatal depression"
            clinical_sig = "Possible perinatal depression (10-12). Further assessment warranted. Clinical interview recommended. May benefit from psychotherapy. Monitor closely for symptom progression. Assess social support and infant care."
        else:
            severity = "low_risk"
            interpretation = "Low likelihood of perinatal depression"
            clinical_sig = "Low risk for perinatal depression (<10). Routine monitoring recommended during perinatal period."
        
        return ScreenerResult(
            name=self.name,
            score=total,
            max_score=30,
            interpretation=interpretation,
            severity=severity,
            clinical_significance=clinical_sig,
            item_scores=responses,
            subscales={
                "suicidal_ideation": suicidal_item > 0
            }
        )

