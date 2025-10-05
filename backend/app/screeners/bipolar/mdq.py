"""
MDQ: Mood Disorder Questionnaire
Screens for bipolar spectrum disorders

Scoring:
- Positive screen if:
  1. 7 or more "Yes" responses to questions 1-13, AND
  2. Several symptoms occurred at the same time (Question 14 = "Yes"), AND  
  3. Moderate or serious problems caused (Question 15 = "Moderate" or "Serious")
"""
from typing import List
from app.screeners.base import BaseScreener, ScreenerQuestion, ScreenerResult


class MDQ(BaseScreener):
    """MDQ Bipolar Screener"""
    
    @property
    def name(self) -> str:
        return "MDQ"
    
    @property
    def description(self) -> str:
        return "Mood Disorder Questionnaire - screens for bipolar spectrum disorders"
    
    @property
    def questions(self) -> List[ScreenerQuestion]:
        """
        MDQ questions - Has there ever been a period of time when you were not your usual self and...
        """
        yes_no = [
            {"value": 0, "label": "No"},
            {"value": 1, "label": "Yes"}
        ]
        
        questions_list = [
            "you felt so good or so hyper that other people thought you were not your normal self, or you were so hyper that you got into trouble?",
            "you were so irritable that you shouted at people or started fights or arguments?",
            "you felt much more self-confident than usual?",
            "you got much less sleep than usual and found you didn't really miss it?",
            "you were much more talkative or spoke much faster than usual?",
            "thoughts raced through your head or you couldn't slow your mind down?",
            "you were so easily distracted by things around you that you had trouble concentrating or staying on track?",
            "you had much more energy than usual?",
            "you were much more active or did many more things than usual?",
            "you were much more social or outgoing than usual, for example, you telephoned friends in the middle of the night?",
            "you were much more interested in sex than usual?",
            "you did things that were unusual for you or that other people might have thought were excessive, foolish, or risky?",
            "spending money got you or your family into trouble?"
        ]
        
        screener_questions = []
        for i, text in enumerate(questions_list, 1):
            screener_questions.append(
                ScreenerQuestion(
                    number=i,
                    text=text,
                    options=yes_no
                )
            )
        
        # Question 14: Co-occurrence
        screener_questions.append(
            ScreenerQuestion(
                number=14,
                text="If you checked YES to more than one of the above, have several of these ever happened during the same period of time?",
                options=yes_no
            )
        )
        
        # Question 15: Severity
        screener_questions.append(
            ScreenerQuestion(
                number=15,
                text="How much of a problem did any of these cause you?",
                options=[
                    {"value": 0, "label": "No problem"},
                    {"value": 1, "label": "Minor problem"},
                    {"value": 2, "label": "Moderate problem"},
                    {"value": 3, "label": "Serious problem"}
                ]
            )
        )
        
        return screener_questions
    
    def score(self, responses: List[int]) -> ScreenerResult:
        """
        Score MDQ
        
        Args:
            responses: List of 15 integers
            
        Returns:
            ScreenerResult with interpretation
        """
        # Validate responses
        self.validate_responses(responses)
        
        # Count "Yes" responses for questions 1-13
        yes_count = sum(responses[:13])
        
        # Check co-occurrence (question 14)
        co_occurred = responses[13] == 1
        
        # Check severity (question 15: 0=None, 1=Minor, 2=Moderate, 3=Serious)
        severity_level = responses[14]
        
        # Determine if positive screen
        positive_screen = (
            yes_count >= 7 and
            co_occurred and
            severity_level >= 2  # Moderate or Serious
        )
        
        if positive_screen:
            severity = "positive_screen"
            interpretation = "Positive screen for bipolar spectrum disorder"
            clinical_sig = "MDQ positive. Patient endorses ≥7 manic symptoms that co-occurred and caused moderate/serious problems. Comprehensive psychiatric evaluation for bipolar disorder strongly recommended. Rule out substance-induced symptoms."
        elif yes_count >= 7 and co_occurred:
            severity = "possible"
            interpretation = "Possible bipolar symptoms, further evaluation recommended"
            clinical_sig = "Patient endorses multiple manic symptoms that co-occurred but reports minimal functional impact. Clinical interview recommended to assess for bipolar spectrum, cyclothymia, or substance-related mood elevation."
        elif yes_count >= 4:
            severity = "subthreshold"
            interpretation = "Some manic symptoms endorsed"
            clinical_sig = "Some manic/hypomanic symptoms endorsed. Monitor for mood episodes. Consider bipolar spectrum in differential if symptoms recur with clear episodes."
        else:
            severity = "negative"
            interpretation = "Negative screen for bipolar disorder"
            clinical_sig = "Screening does not suggest bipolar spectrum disorder based on current responses."
        
        return ScreenerResult(
            name=self.name,
            score=yes_count,  # Count of "Yes" responses
            max_score=13,
            interpretation=interpretation,
            severity=severity,
            clinical_significance=clinical_sig,
            item_scores=responses,
            subscales={
                "symptom_count": yes_count,
                "co_occurrence": co_occurred,
                "functional_impact": severity_level,
                "meets_criteria": positive_screen
            }
        )

