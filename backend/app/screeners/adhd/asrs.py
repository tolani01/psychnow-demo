"""
ASRS v1.1: Adult ADHD Self-Report Scale
ADHD screening tool for adults

Part A (6 items): Screening questions - most predictive
Part B (12 items): Additional symptom inventory

Scoring Part A:
- 4 or more shaded boxes = High likelihood of ADHD
- Shaded: Questions 1-3 (≥2), Questions 4-6 (≥3)

Total score interpretation:
- Part A score ≥4: Highly suggestive of ADHD
- Total score ≥24 out of 72: Significant ADHD symptoms
"""
from typing import List
from app.screeners.base import BaseScreener, ScreenerQuestion, ScreenerResult


class ASRS(BaseScreener):
    """ASRS v1.1 ADHD Screener (18 items total)"""
    
    @property
    def name(self) -> str:
        return "ASRS v1.1"
    
    @property
    def description(self) -> str:
        return "Adult ADHD Self-Report Scale - screening tool for attention deficit hyperactivity disorder"
    
    @property
    def questions(self) -> List[ScreenerQuestion]:
        """
        ASRS v1.1 questions - How often do you have trouble with...
        
        Response options: 0=Never, 1=Rarely, 2=Sometimes, 3=Often, 4=Very Often
        """
        options = [
            {"value": 0, "label": "Never"},
            {"value": 1, "label": "Rarely"},
            {"value": 2, "label": "Sometimes"},
            {"value": 3, "label": "Often"},
            {"value": 4, "label": "Very Often"}
        ]
        
        return [
            # Part A (Screening Questions)
            ScreenerQuestion(
                number=1,
                text="How often do you have trouble wrapping up the final details of a project, once the challenging parts have been done?",
                options=options
            ),
            ScreenerQuestion(
                number=2,
                text="How often do you have difficulty getting things in order when you have to do a task that requires organization?",
                options=options
            ),
            ScreenerQuestion(
                number=3,
                text="How often do you have problems remembering appointments or obligations?",
                options=options
            ),
            ScreenerQuestion(
                number=4,
                text="When you have a task that requires a lot of thought, how often do you avoid or delay getting started?",
                options=options
            ),
            ScreenerQuestion(
                number=5,
                text="How often do you fidget or squirm with your hands or feet when you have to sit down for a long time?",
                options=options
            ),
            ScreenerQuestion(
                number=6,
                text="How often do you feel overly active and compelled to do things, like you were driven by a motor?",
                options=options
            ),
            # Part B (Additional Symptoms)
            ScreenerQuestion(
                number=7,
                text="How often do you make careless mistakes when you have to work on a boring or difficult project?",
                options=options
            ),
            ScreenerQuestion(
                number=8,
                text="How often do you have difficulty keeping your attention when you are doing boring or repetitive work?",
                options=options
            ),
            ScreenerQuestion(
                number=9,
                text="How often do you have difficulty concentrating on what people say to you, even when they are speaking to you directly?",
                options=options
            ),
            ScreenerQuestion(
                number=10,
                text="How often do you misplace or have difficulty finding things at home or at work?",
                options=options
            ),
            ScreenerQuestion(
                number=11,
                text="How often are you distracted by activity or noise around you?",
                options=options
            ),
            ScreenerQuestion(
                number=12,
                text="How often do you leave your seat in meetings or other situations in which you are expected to remain seated?",
                options=options
            ),
            ScreenerQuestion(
                number=13,
                text="How often do you feel restless or fidgety?",
                options=options
            ),
            ScreenerQuestion(
                number=14,
                text="How often do you have difficulty unwinding and relaxing when you have time to yourself?",
                options=options
            ),
            ScreenerQuestion(
                number=15,
                text="How often do you find yourself talking too much when you are in social situations?",
                options=options
            ),
            ScreenerQuestion(
                number=16,
                text="When you're in a conversation, how often do you find yourself finishing the sentences of the people you are talking to, before they can finish them themselves?",
                options=options
            ),
            ScreenerQuestion(
                number=17,
                text="How often do you have difficulty waiting your turn in situations when turn taking is required?",
                options=options
            ),
            ScreenerQuestion(
                number=18,
                text="How often do you interrupt others when they are busy?",
                options=options
            ),
        ]
    
    def score(self, responses: List[int]) -> ScreenerResult:
        """
        Score ASRS v1.1
        
        Args:
            responses: List of 18 integers (0-4)
            
        Returns:
            ScreenerResult with score and interpretation
        """
        # Validate responses
        self.validate_responses(responses)
        
        # Part A (Questions 1-6) - Screening
        part_a = responses[:6]
        
        # Shaded criteria for Part A
        # Q1-3: Shaded if ≥2 (Sometimes, Often, Very Often)
        # Q4-6: Shaded if ≥3 (Often, Very Often)
        shaded_count = 0
        shaded_count += sum(1 for r in part_a[:3] if r >= 2)  # Q1-3
        shaded_count += sum(1 for r in part_a[3:6] if r >= 3)  # Q4-6
        
        # Part B score (Questions 7-18)
        part_b = responses[6:]
        
        # Total score
        total_score = sum(responses)
        
        # Determine interpretation
        if shaded_count >= 4:
            severity = "positive_screen"
            interpretation = "Highly suggestive of ADHD"
            clinical_sig = "Part A screen positive (≥4 shaded). Comprehensive ADHD evaluation strongly recommended. Consider formal neuropsychological testing."
            likely_adhd = True
        elif shaded_count >= 2:
            severity = "possible"
            interpretation = "Possible ADHD, further evaluation recommended"
            clinical_sig = "Some ADHD symptoms present. Consider ADHD evaluation if symptoms cause functional impairment."
            likely_adhd = False
        else:
            severity = "unlikely"
            interpretation = "ADHD unlikely based on screening"
            clinical_sig = "Screening does not suggest ADHD. Consider other causes if attention difficulties persist."
            likely_adhd = False
        
        # Subscale analysis
        inattention_items = [0, 1, 2, 3, 6, 7, 8, 9, 10]  # Questions related to inattention
        hyperactivity_items = [4, 5, 11, 12, 13, 14, 15, 16, 17]  # Questions related to hyperactivity/impulsivity
        
        inattention_score = sum(responses[i] for i in inattention_items)
        hyperactivity_score = sum(responses[i] for i in hyperactivity_items)
        
        return ScreenerResult(
            name=self.name,
            score=total_score,
            max_score=72,
            interpretation=interpretation,
            severity=severity,
            clinical_significance=clinical_sig,
            item_scores=responses,
            subscales={
                "part_a_shaded": shaded_count,
                "part_a_total": sum(part_a),
                "part_b_total": sum(part_b),
                "inattention_score": inattention_score,
                "hyperactivity_score": hyperactivity_score,
                "likely_adhd": likely_adhd,
                "primary_subtype": "inattentive" if inattention_score > hyperactivity_score else "hyperactive" if hyperactivity_score > inattention_score else "combined"
            }
        )

