"""
CTQ-SF: Childhood Trauma Questionnaire - Short Form
28-item retrospective self-report of childhood maltreatment

5 Subscales (5 items each + 3 validity items):
- Emotional Abuse
- Physical Abuse
- Sexual Abuse
- Emotional Neglect
- Physical Neglect
"""
from typing import List
from app.screeners.base import BaseScreener, ScreenerQuestion, ScreenerResult


class CTQSF(BaseScreener):
    """CTQ-SF Childhood Trauma Questionnaire"""
    
    @property
    def name(self) -> str:
        return "CTQ-SF"
    
    @property
    def description(self) -> str:
        return "Childhood Trauma Questionnaire - assesses childhood maltreatment history"
    
    @property
    def questions(self) -> List[ScreenerQuestion]:
        """CTQ-SF questions - When I was growing up..."""
        options = [
            {"value": 1, "label": "Never true"},
            {"value": 2, "label": "Rarely true"},
            {"value": 3, "label": "Sometimes true"},
            {"value": 4, "label": "Often true"},
            {"value": 5, "label": "Very often true"}
        ]
        
        questions_text = [
            # Emotional Abuse (EA)
            "I thought that my parents wished I had never been born",
            "People in my family said hurtful or insulting things to me",
            "People in my family called me things like 'stupid,' 'lazy,' or 'ugly'",
            "I felt that someone in my family hated me",
            "I believe that I was emotionally abused",
            # Physical Abuse (PA)
            "I got hit so hard by someone in my family that I had to see a doctor or go to the hospital",
            "People in my family hit me so hard that it left me with bruises or marks",
            "I was punished with a belt, board, cord, or some other hard object",
            "I was hit by someone in my family so hard that it hurt for days",
            "I believe that I was physically abused",
            # Sexual Abuse (SA)
            "Someone tried to touch me in a sexual way, or tried to make me touch them",
            "Someone threatened to hurt me or tell lies about me unless I did something sexual with them",
            "Someone tried to make me do sexual things or watch sexual things",
            "Someone molested me",
            "I believe that I was sexually abused",
            # Emotional Neglect (EN)
            "There was someone in my family who helped me feel important or special",  # Reverse
            "People in my family looked out for each other",  # Reverse
            "People in my family felt close to each other",  # Reverse
            "My family was a source of strength and support",  # Reverse
            "I felt loved",  # Reverse
            # Physical Neglect (PN)
            "There was not enough to eat in my house",
            "I knew there was someone there to take care of me and protect me",  # Reverse
            "My parents were too drunk or high to take care of the family",
            "I had to wear dirty clothes",
            "I felt that someone in my family would protect me if I needed it",  # Reverse
            # Validity items
            "I believe my family is perfect",  # Minimization
            "I have the best family in the world",  # Minimization
            "My family is as close as a family can be"  # Minimization
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
        """Score CTQ-SF"""
        self.validate_responses(responses)
        
        # Reverse score items 16-20, 22, 25 (indices 15-19, 21, 24)
        adjusted = responses.copy()
        reverse_items = [15, 16, 17, 18, 19, 21, 24]
        for idx in reverse_items:
            adjusted[idx] = 6 - adjusted[idx]
        
        # Calculate subscales
        emotional_abuse = sum(adjusted[0:5])
        physical_abuse = sum(adjusted[5:10])
        sexual_abuse = sum(adjusted[10:15])
        emotional_neglect = sum(adjusted[15:20])
        physical_neglect = sum(adjusted[20:25])
        
        # Validity (minimization)
        validity_score = sum(responses[25:28])
        
        total_trauma = emotional_abuse + physical_abuse + sexual_abuse + emotional_neglect + physical_neglect
        
        # Determine severity using clinical cutoffs
        severity_levels = []
        if emotional_abuse >= 13:
            severity_levels.append("severe emotional abuse")
        elif emotional_abuse >= 10:
            severity_levels.append("moderate emotional abuse")
        
        if physical_abuse >= 10:
            severity_levels.append("severe physical abuse")
        elif physical_abuse >= 8:
            severity_levels.append("moderate physical abuse")
        
        if sexual_abuse >= 8:
            severity_levels.append("severe sexual abuse")
        elif sexual_abuse >= 6:
            severity_levels.append("moderate sexual abuse")
        
        if emotional_neglect >= 15:
            severity_levels.append("severe emotional neglect")
        elif emotional_neglect >= 10:
            severity_levels.append("moderate emotional neglect")
        
        if physical_neglect >= 10:
            severity_levels.append("severe physical neglect")
        elif physical_neglect >= 8:
            severity_levels.append("moderate physical neglect")
        
        if severity_levels:
            severity = "trauma_history"
            interpretation = f"Childhood trauma history: {', '.join(severity_levels)}"
            clinical_sig = f"Significant childhood trauma history identified: {', '.join(severity_levels)}. Trauma-informed care essential. Assess current safety and support. Consider trauma-focused therapy (PE, CPT, EMDR, TF-CBT). Childhood trauma increases risk for PTSD, depression, anxiety, substance use, and relationship difficulties. Comprehensive trauma assessment recommended."
        else:
            severity = "low_minimal"
            interpretation = "Minimal or low childhood trauma"
            clinical_sig = "Minimal childhood trauma reported. Low CTQ scores."
        
        # Validity check
        if validity_score >= 10:
            clinical_sig += " NOTE: Elevated validity scores suggest possible minimization or idealization of family. Results may underestimate trauma exposure."
        
        return ScreenerResult(
            name=self.name,
            score=total_trauma,
            max_score=125,
            interpretation=interpretation,
            severity=severity,
            clinical_significance=clinical_sig,
            item_scores=responses,
            subscales={
                "emotional_abuse": emotional_abuse,
                "physical_abuse": physical_abuse,
                "sexual_abuse": sexual_abuse,
                "emotional_neglect": emotional_neglect,
                "physical_neglect": physical_neglect,
                "validity_minimization": validity_score
            }
        )

