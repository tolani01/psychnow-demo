"""
Screener Enforcement Service
Ensures all required screeners are completed based on symptoms
"""
from typing import List, Dict, Any
from app.screeners.registry import screener_registry


class ScreenerEnforcementService:
    """Service to enforce screener completion"""
    
    def get_required_screeners(self, symptoms: Dict[str, bool]) -> List[str]:
        """
        Get list of REQUIRED screeners based on detected symptoms
        
        Args:
            symptoms: Dictionary of symptom flags
            
        Returns:
            List of screener names that MUST be completed
        """
        return screener_registry.get_screeners_for_symptoms(symptoms)
    
    def get_pending_screeners(
        self,
        symptoms: Dict[str, bool],
        completed: List[str]
    ) -> List[str]:
        """
        Get list of screeners still pending
        
        Args:
            symptoms: Detected symptoms
            completed: List of already completed screeners
            
        Returns:
            List of screeners that still need to be administered
        """
        required = self.get_required_screeners(symptoms)
        return [s for s in required if s not in completed]
    
    def should_enforce_screeners(self, session_data: Dict[str, Any]) -> bool:
        """
        Check if conversation should pause for screener administration
        
        CRITICAL: Screeners should ONLY be administered AFTER comprehensive symptom review
        is complete. This ensures proper DSM-5 diagnostic assessment.
        
        Args:
            session_data: Session data
            
        Returns:
            True if screeners are pending and should be enforced
        """
        symptoms = session_data.get("symptoms_detected", {})
        completed = session_data.get("screeners_completed", [])
        
        pending = self.get_pending_screeners(symptoms, completed)
        
        # Enforce if:
        # 1. There are pending screeners
        # 2. We've completed comprehensive symptom review (message count > 15)
        # 3. We're not already in screening phase
        # 4. We have sufficient symptom data for proper diagnostic assessment
        
        message_count = len(session_data.get("conversation_history", []))
        current_phase = session_data.get("current_phase", "")
        symptoms_count = len([s for s in symptoms.values() if s])
        
        # Require comprehensive assessment before screeners
        # Check if all major assessment phases are completed
        completed_phases = session_data.get("completed_phases", [])
        required_phases = ["greeting", "chief_complaint", "mood_assessment", 
                          "cognitive_assessment", "physical_assessment", 
                          "behavioral_assessment", "mental_status_exam"]
        
        phases_complete = all(phase in completed_phases for phase in required_phases)
        
        return (
            len(pending) > 0 and
            message_count >= 25 and  # Need comprehensive conversation before screeners
            symptoms_count >= 5 and  # Need multiple symptom domains identified
            phases_complete and  # All assessment phases completed
            current_phase != "screening"
        )
    
    def get_screener_transition_message(self, pending_screeners: List[str]) -> str:
        """
        Get message to transition into screener administration
        
        Args:
            pending_screeners: List of screeners to administer
            
        Returns:
            Message explaining what screeners will be administered
        """
        screener_descriptions = {
            "PHQ-9": "depression screening (9 questions)",
            "GAD-7": "anxiety screening (7 questions)",
            "C-SSRS": "safety assessment (6 questions)",
            "ASRS": "ADHD screening (18 questions)",
            "PCL-5": "PTSD screening (20 questions)"
        }
        
        desc_list = [
            f"- {name}: {screener_descriptions.get(name, 'screening')}"
            for name in pending_screeners
        ]
        
        return f"""
Based on what you've shared, I'd like to administer some standardized screening questionnaires. These are brief validated tools that help providers assess your symptoms accurately.

We'll complete:
{chr(10).join(desc_list)}

These will take about {len(pending_screeners) * 2}-{len(pending_screeners) * 3} minutes total.

Let's start with the {pending_screeners[0]}.
""".strip()


# Global enforcement service instance
screener_enforcement_service = ScreenerEnforcementService()

