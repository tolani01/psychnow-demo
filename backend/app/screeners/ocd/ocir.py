"""
OCI-R: Obsessive-Compulsive Inventory - Revised
Brief screening tool for OCD symptoms

Scoring:
0-20: Normal
21+: Possible OCD (further evaluation recommended)

Subscales:
- Washing (items 1, 7, 13)
- Checking (items 2, 8, 14)
- Doubting (items 3, 9, 15)
- Ordering (items 4, 10, 16)
- Obsessing (items 5, 11, 17)
- Hoarding (items 6, 12, 18)
"""
from typing import List
from app.screeners.base import BaseScreener, ScreenerQuestion, ScreenerResult


class OCIR(BaseScreener):
    """OCI-R OCD Screener"""
    
    @property
    def name(self) -> str:
        return "OCI-R"
    
    @property
    def description(self) -> str:
        return "Obsessive-Compulsive Inventory - Revised (screens for OCD symptoms)"
    
    @property
    def questions(self) -> List[ScreenerQuestion]:
        """OCI-R questions - How much has this bothered or distressed you in the past month?"""
        options = [
            {"value": 0, "label": "Not at all"},
            {"value": 1, "label": "A little"},
            {"value": 2, "label": "Moderately"},
            {"value": 3, "label": "A lot"},
            {"value": 4, "label": "Extremely"}
        ]
        
        questions_text = [
            "I have saved up so many things that they get in the way.",  # Hoarding
            "I check things more often than necessary.",  # Checking
            "I get upset if objects are not arranged properly.",  # Ordering
            "I feel compelled to count while I am doing things.",  # Obsessing
            "I find it difficult to touch an object when I know it has been touched by strangers or certain people.",  # Washing
            "I find it difficult to control my own thoughts.",  # Obsessing
            "I collect things I don't need.",  # Hoarding
            "I repeatedly check doors, windows, drawers, etc.",  # Checking
            "I get upset if others change the way I have arranged things.",  # Ordering
            "I feel I have to repeat certain numbers.",  # Obsessing
            "I sometimes have to wash or clean myself simply because I feel contaminated.",  # Washing
            "I am upset by unpleasant thoughts that come into my mind against my will.",  # Obsessing
            "I avoid throwing things away because I am afraid I might need them later.",  # Hoarding
            "I repeatedly check gas and water taps and light switches after turning them off.",  # Checking
            "I need things to be arranged in a particular order.",  # Ordering
            "I feel that there are good and bad numbers.",  # Obsessing
            "I wash my hands more often and longer than necessary.",  # Washing
            "I frequently get nasty thoughts and have difficulty in getting rid of them."  # Obsessing
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
        Score OCI-R
        
        Args:
            responses: List of 18 integers (0-4)
            
        Returns:
            ScreenerResult with subscales
        """
        # Validate responses
        self.validate_responses(responses)
        
        # Calculate total score
        total = sum(responses)
        
        # Calculate subscales (each has 3 items)
        washing = responses[4] + responses[10] + responses[16]
        checking = responses[1] + responses[7] + responses[13]
        doubting = responses[2] + responses[8] + responses[14]
        ordering = responses[2] + responses[8] + responses[14]
        obsessing = responses[3] + responses[5] + responses[9] + responses[11] + responses[15] + responses[17]
        hoarding = responses[0] + responses[6] + responses[12]
        
        # Determine severity
        if total >= 40:
            severity = "severe"
            interpretation = "Severe OCD symptoms"
            clinical_sig = "Severe OCD symptoms (total ≥40). Comprehensive OCD assessment and treatment planning strongly recommended. Consider referral to OCD specialist. Evidence-based treatments include ERP (Exposure and Response Prevention) and/or SSRI medication."
        elif total >= 21:
            severity = "moderate"
            interpretation = "Moderate OCD symptoms (positive screen)"
            clinical_sig = "Positive OCD screen (total ≥21). Clinical interview recommended to confirm OCD diagnosis and assess symptom dimensions. Consider evidence-based OCD treatments: ERP therapy and/or pharmacotherapy (SSRI at therapeutic doses)."
        elif total >= 11:
            severity = "mild"
            interpretation = "Mild OCD symptoms"
            clinical_sig = "Mild OCD symptoms present. Further assessment recommended if symptoms cause distress or functional impairment. Monitor for symptom progression. Consider psychoeducation about OCD."
        else:
            severity = "minimal"
            interpretation = "Minimal or no OCD symptoms"
            clinical_sig = "No significant OCD symptoms identified on screening."
        
        return ScreenerResult(
            name=self.name,
            score=total,
            max_score=72,
            interpretation=interpretation,
            severity=severity,
            clinical_significance=clinical_sig,
            item_scores=responses,
            subscales={
                "washing": washing,
                "checking": checking,
                "ordering": ordering,
                "obsessing": obsessing,
                "hoarding": hoarding,
                "positive_screen": total >= 21
            }
        )

