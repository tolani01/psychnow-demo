"""
PCL-5: PTSD Checklist for DSM-5
Post-Traumatic Stress Disorder screening tool

Scoring:
- Cutoff score: ≥33 suggests PTSD diagnosis
- Symptom clusters:
  - Intrusion (Questions 1-5)
  - Avoidance (Questions 6-7)
  - Negative cognitions/mood (Questions 8-14)
  - Arousal/reactivity (Questions 15-20)

Severity (total score):
- 0-20: Minimal/No PTSD
- 21-32: Mild PTSD symptoms
- 33-45: Moderate PTSD (clinical threshold)
- 46-60: Moderately severe PTSD
- 61-80: Severe PTSD
"""
from typing import List
from app.screeners.base import BaseScreener, ScreenerQuestion, ScreenerResult


class PCL5(BaseScreener):
    """PCL-5 PTSD Screener"""
    
    @property
    def name(self) -> str:
        return "PCL-5"
    
    @property
    def description(self) -> str:
        return "PTSD Checklist for DSM-5 - screens for post-traumatic stress disorder symptoms"
    
    @property
    def questions(self) -> List[ScreenerQuestion]:
        """
        PCL-5 questions - In the past month, how much were you bothered by...
        
        Response options: 0=Not at all, 1=A little bit, 2=Moderately, 3=Quite a bit, 4=Extremely
        """
        options = [
            {"value": 0, "label": "Not at all"},
            {"value": 1, "label": "A little bit"},
            {"value": 2, "label": "Moderately"},
            {"value": 3, "label": "Quite a bit"},
            {"value": 4, "label": "Extremely"}
        ]
        
        return [
            # Cluster 1: Intrusion (1-5)
            ScreenerQuestion(
                number=1,
                text="Repeated, disturbing, and unwanted memories of the stressful experience?",
                options=options
            ),
            ScreenerQuestion(
                number=2,
                text="Repeated, disturbing dreams of the stressful experience?",
                options=options
            ),
            ScreenerQuestion(
                number=3,
                text="Suddenly feeling or acting as if the stressful experience were actually happening again (as if you were actually back there reliving it)?",
                options=options
            ),
            ScreenerQuestion(
                number=4,
                text="Feeling very upset when something reminded you of the stressful experience?",
                options=options
            ),
            ScreenerQuestion(
                number=5,
                text="Having strong physical reactions when something reminded you of the stressful experience (for example, heart pounding, trouble breathing, sweating)?",
                options=options
            ),
            # Cluster 2: Avoidance (6-7)
            ScreenerQuestion(
                number=6,
                text="Avoiding memories, thoughts, or feelings related to the stressful experience?",
                options=options
            ),
            ScreenerQuestion(
                number=7,
                text="Avoiding external reminders of the stressful experience (for example, people, places, conversations, activities, objects, or situations)?",
                options=options
            ),
            # Cluster 3: Negative Cognitions and Mood (8-14)
            ScreenerQuestion(
                number=8,
                text="Trouble remembering important parts of the stressful experience?",
                options=options
            ),
            ScreenerQuestion(
                number=9,
                text="Having strong negative beliefs about yourself, other people, or the world (for example, having thoughts such as: I am bad, there is something seriously wrong with me, no one can be trusted, the world is completely dangerous)?",
                options=options
            ),
            ScreenerQuestion(
                number=10,
                text="Blaming yourself or someone else for the stressful experience or what happened after it?",
                options=options
            ),
            ScreenerQuestion(
                number=11,
                text="Having strong negative feelings such as fear, horror, anger, guilt, or shame?",
                options=options
            ),
            ScreenerQuestion(
                number=12,
                text="Loss of interest in activities that you used to enjoy?",
                options=options
            ),
            ScreenerQuestion(
                number=13,
                text="Feeling distant or cut off from other people?",
                options=options
            ),
            ScreenerQuestion(
                number=14,
                text="Trouble experiencing positive feelings (for example, being unable to feel happiness or have loving feelings for people close to you)?",
                options=options
            ),
            # Cluster 4: Arousal and Reactivity (15-20)
            ScreenerQuestion(
                number=15,
                text="Irritable behavior, angry outbursts, or acting aggressively?",
                options=options
            ),
            ScreenerQuestion(
                number=16,
                text="Taking too many risks or doing things that could cause you harm?",
                options=options
            ),
            ScreenerQuestion(
                number=17,
                text="Being 'superalert' or watchful or on guard?",
                options=options
            ),
            ScreenerQuestion(
                number=18,
                text="Feeling jumpy or easily startled?",
                options=options
            ),
            ScreenerQuestion(
                number=19,
                text="Having difficulty concentrating?",
                options=options
            ),
            ScreenerQuestion(
                number=20,
                text="Trouble falling or staying asleep?",
                options=options
            ),
        ]
    
    def score(self, responses: List[int]) -> ScreenerResult:
        """
        Score PCL-5
        
        Args:
            responses: List of 20 integers (0-4)
            
        Returns:
            ScreenerResult with score, clusters, and interpretation
        """
        # Validate responses
        self.validate_responses(responses)
        
        # Calculate total score
        total_score = sum(responses)
        
        # Calculate cluster scores (DSM-5 criteria)
        intrusion = sum(responses[0:5])  # Questions 1-5
        avoidance = sum(responses[5:7])  # Questions 6-7
        cognition_mood = sum(responses[7:14])  # Questions 8-14
        arousal = sum(responses[14:20])  # Questions 15-20
        
        # Determine severity and interpretation
        if total_score < 21:
            severity = "minimal"
            interpretation = "Minimal or no PTSD symptoms"
            clinical_sig = "Score below clinical threshold. Monitor if trauma exposure is recent."
        elif total_score < 33:
            severity = "mild"
            interpretation = "Mild PTSD symptoms"
            clinical_sig = "Subthreshold PTSD symptoms. Consider trauma-focused therapy if causing distress."
        elif total_score < 46:
            severity = "moderate"
            interpretation = "Moderate PTSD (probable diagnosis)"
            clinical_sig = "Score meets threshold for probable PTSD diagnosis. Trauma-focused therapy (PE, CPT, EMDR) strongly recommended. Consider medication (SSRI)."
        elif total_score < 61:
            severity = "moderately_severe"
            interpretation = "Moderately severe PTSD"
            clinical_sig = "Significant PTSD symptoms. Intensive trauma-focused therapy recommended. Medication evaluation indicated. Monitor for safety."
        else:  # 61-80
            severity = "severe"
            interpretation = "Severe PTSD"
            clinical_sig = "Severe PTSD symptoms. Intensive treatment with trauma-focused therapy and medication recommended. Assess for comorbid conditions. Safety planning may be needed."
        
        return ScreenerResult(
            name=self.name,
            score=total_score,
            max_score=80,
            interpretation=interpretation,
            severity=severity,
            clinical_significance=clinical_sig,
            item_scores=responses,
            subscales={
                "intrusion": intrusion,
                "avoidance": avoidance,
                "cognition_mood": cognition_mood,
                "arousal": arousal,
                "meets_threshold": total_score >= 33,
                "cluster_breakdown": {
                    "Intrusion (re-experiencing)": f"{intrusion}/20",
                    "Avoidance": f"{avoidance}/8",
                    "Negative cognitions and mood": f"{cognition_mood}/28",
                    "Arousal and reactivity": f"{arousal}/24"
                }
            }
        )

