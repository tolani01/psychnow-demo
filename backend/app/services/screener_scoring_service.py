"""
Screener Scoring Service
Handles scoring of completed screeners and storage of results
"""
from typing import List, Dict, Any
from sqlalchemy.orm import Session

from app.screeners.registry import screener_registry
from app.services.escalation_service import escalation_service


class ScreenerScoringService:
    """Service for scoring screeners and handling results"""
    
    async def score_and_store(
        self,
        session_token: str,
        screener_name: str,
        responses: List[int],
        session_data: Dict[str, Any],
        db: Session
    ) -> Dict[str, Any]:
        """
        Score a screener and store results in session
        
        Args:
            session_token: Session identifier
            screener_name: Name of screener (e.g., "PHQ-9")
            responses: List of patient responses
            session_data: Session data dictionary
            db: Database session for escalation
            
        Returns:
            Scoring result
        """
        try:
            # Get screener instance
            screener = screener_registry.get_screener(screener_name)
            
            # Score the responses
            result = screener.score(responses)
            
            # Store in session
            if "screener_scores" not in session_data:
                session_data["screener_scores"] = {}
            
            session_data["screener_scores"][screener_name] = {
                "name": result.name,
                "score": result.score,
                "max_score": result.max_score,
                "interpretation": result.interpretation,
                "severity": result.severity,
                "clinical_significance": result.clinical_significance,
                "item_scores": result.item_scores,
                "subscales": result.subscales
            }
            
            # Mark as completed
            if "screeners_completed" not in session_data:
                session_data["screeners_completed"] = []
            
            if screener_name not in session_data["screeners_completed"]:
                session_data["screeners_completed"].append(screener_name)
            
            # Check for high-risk conditions
            await self._check_for_risk_escalation(
                screener_name,
                result,
                session_data,
                db
            )
            
            return {
                "screener": screener_name,
                "score": result.score,
                "max_score": result.max_score,
                "interpretation": result.interpretation,
                "severity": result.severity
            }
        
        except Exception as e:
            return {
                "error": f"Error scoring {screener_name}: {str(e)}"
            }
    
    async def _check_for_risk_escalation(
        self,
        screener_name: str,
        result: Any,
        session_data: Dict[str, Any],
        db: Session
    ):
        """
        Check if screener result indicates high risk and trigger escalation
        
        Args:
            screener_name: Name of screener
            result: Screener result object
            session_data: Session data
            db: Database session
        """
        # C-SSRS high risk
        if screener_name == "C-SSRS":
            if result.severity == "high":
                await escalation_service.handle_high_risk_detection(
                    session_data=session_data,
                    risk_details={
                        "risk_level": "high",
                        "screener_name": "C-SSRS",
                        "score": result.score,
                        "details": f"C-SSRS indicates high suicide risk. {result.interpretation}"
                    },
                    db=db
                )
                
                # Add to risk flags
                if "risk_flags" not in session_data:
                    session_data["risk_flags"] = []
                
                session_data["risk_flags"].append({
                    "type": "high_suicide_risk",
                    "screener": "C-SSRS",
                    "details": result.clinical_significance,
                    "flagged_at": "now"
                })
        
        # PHQ-9 severe depression
        elif screener_name == "PHQ-9":
            if result.score >= 20:  # Severe depression
                # Add to risk flags
                if "risk_flags" not in session_data:
                    session_data["risk_flags"] = []
                
                session_data["risk_flags"].append({
                    "type": "severe_depression",
                    "screener": "PHQ-9",
                    "score": result.score,
                    "details": "Severe depression detected"
                })


# Global screener scoring service
screener_scoring_service = ScreenerScoringService()

