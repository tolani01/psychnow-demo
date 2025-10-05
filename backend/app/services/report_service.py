"""
Report Generation Service
Creates clinical intake reports from session data
"""
from typing import Dict, Any, List
import json
import uuid
from datetime import datetime

from app.services.llm_service import llm_service
from app.services.quote_service import quote_service
from app.prompts.system_prompts import REPORT_GENERATION_PROMPT, CLINICIAN_REPORT_GENERATION_PROMPT


def generate_clinical_action_dashboard(report_data: dict) -> str:
    """
    Generate the priority dashboard for top of clinician report.
    Shows immediate actions and critical flags.
    """
    # Determine urgency
    cssrs_risk = report_data.get("cssrs_risk_level", "none")
    phq9_score = report_data.get("phq9_score", 0)
    gad7_score = report_data.get("gad7_score", 0)
    
    # Set urgency level
    if cssrs_risk in ["high", "imminent"]:
        urgency = "EMERGENT"
        urgency_action = "Contact patient IMMEDIATELY - Active suicide risk"
    elif cssrs_risk == "moderate" or phq9_score >= 20:
        urgency = "URGENT"
        urgency_action = "Schedule within 24-48 hours - Severe symptoms"
    elif phq9_score >= 15 or gad7_score >= 15:
        urgency = "URGENT"
        urgency_action = "Schedule within 1 week - Moderate-severe symptoms"
    else:
        urgency = "ROUTINE"
        urgency_action = "Schedule within 1-2 weeks - Standard follow-up"
    
    # Collect critical flags
    flags = []
    if cssrs_risk != "none":
        flags.append(f"⚠️ Suicide Risk: {cssrs_risk.upper()} (C-SSRS)")
    if phq9_score >= 15:
        flags.append(f"⚠️ Severe Depression (PHQ-9: {phq9_score}/27)")
    if gad7_score >= 15:
        flags.append(f"⚠️ Severe Anxiety (GAD-7: {gad7_score}/21)")
    if report_data.get("prior_suicide_attempt"):
        flags.append(f"⚠️ Prior suicide attempt: {report_data.get('prior_attempt_details')}")
    
    flags_text = "\n║  ".join(flags) if flags else "None identified"
    
    # Generate recommended actions
    actions = generate_immediate_actions(report_data)
    actions_text = "\n║  ".join([f"{i+1}. {a}" for i, a in enumerate(actions)])
    
    # Build dashboard
    dashboard = f"""
╔══════════════════════════════════════════════════════════════╗
║  🚨 CLINICAL ACTION DASHBOARD                                 ║
╠══════════════════════════════════════════════════════════════╣
║  URGENCY: {urgency:<53}║
║  → {urgency_action:<57}║
║                                                               ║
║  CRITICAL RED FLAGS:                                          ║
║  {flags_text:<60}║
║                                                               ║
║  RECOMMENDED IMMEDIATE ACTIONS:                               ║
║  {actions_text:<60}║
║                                                               ║
║  TRIAGE LEVEL: {get_triage_level(report_data):<45}║
╚══════════════════════════════════════════════════════════════╝
"""
    
    return dashboard


def generate_immediate_actions(report_data: dict) -> list:
    """Generate list of immediate action recommendations."""
    actions = []
    
    cssrs_risk = report_data.get("cssrs_risk_level", "none")
    phq9_score = report_data.get("phq9_score", 0)
    
    # Safety actions
    if cssrs_risk in ["high", "imminent"]:
        actions.append("IMMEDIATE safety assessment and safety planning (PRIORITY)")
        actions.append("Consider same-day evaluation or ED referral")
        actions.append("Remove access to lethal means")
    elif cssrs_risk == "moderate":
        actions.append("Safety assessment and safety planning within 24 hours")
    
    # Treatment actions
    if phq9_score >= 15:
        actions.append("Initiate antidepressant therapy (consider SSRI)")
        actions.append("Refer for psychotherapy (CBT for depression)")
    
    # Lab work
    if phq9_score >= 10 or report_data.get("fatigue"):
        actions.append("Order labs: TSH, CBC, CMP, Vitamin D, B12")
    
    # Follow-up
    if cssrs_risk != "none":
        actions.append("Schedule close follow-up (within 1 week)")
    
    return actions[:5]  # Return top 5 actions


def get_triage_level(report_data: dict) -> str:
    """Determine triage level for scheduling priority."""
    cssrs_risk = report_data.get("cssrs_risk_level", "none")
    phq9_score = report_data.get("phq9_score", 0)
    
    if cssrs_risk in ["high", "imminent"]:
        return "Level 1 - Critical (Emergency)"
    elif cssrs_risk == "moderate" or phq9_score >= 20:
        return "Level 2 - High Acuity (Urgent)"
    elif phq9_score >= 10:
        return "Level 3 - Moderate Acuity"
    else:
        return "Level 4 - Standard"


class ReportService:
    """Service for generating intake reports"""
    
    async def generate_report(
        self,
        session_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate comprehensive intake report from session
        
        Args:
            session_data: Complete session data with conversation history and screeners
            
        Returns:
            Structured report dictionary with patient quotes
        """
        # Extract patient quotes FIRST
        patient_quotes = await quote_service.extract_key_quotes(
            session_data.get("conversation_history", [])
        )
        
        # Build conversation summary
        conversation_text = self._format_conversation(session_data.get("conversation_history", []))
        
        # Format screener results
        screener_results = session_data.get("screener_scores", {})
        screener_summary = self._format_screeners(screener_results)
        
        # Create prompt for report generation
        messages = [
            {"role": "system", "content": REPORT_GENERATION_PROMPT},
            {"role": "user", "content": f"""Generate a clinical intake report based on this information:

**CONVERSATION:**
{conversation_text}

**SCREENER RESULTS:**
{screener_summary}

**DETECTED SYMPTOMS:**
{json.dumps(session_data.get('symptoms_detected', {}), indent=2)}

**RISK FLAGS:**
{json.dumps(session_data.get('risk_flags', []), indent=2)}

Generate the structured JSON report now."""}
        ]
        
        # Get structured JSON response
        report = await llm_service.get_structured_completion(messages, response_format={})
        
        # Add metadata
        report["patient_id"] = session_data.get("patient_id") or str(uuid.uuid4())
        report["date"] = datetime.utcnow().isoformat()
        
        # Add patient quotes section
        report["patient_statements"] = patient_quotes
        
        # Add diagnostic considerations (provider-only)
        report["diagnostic_considerations"] = self._generate_diagnostic_considerations(session_data)
        
        # Add documentation note
        report["documentation_note"] = "Patient statements have been lightly edited for spelling/grammar only; clinical content and meaning preserved. This AI-assisted report requires provider review and signature."
        
        # Ensure screeners field is populated with ALL completed screeners
        # Override LLM's screeners array with actual completed screeners from session
        report["screeners"] = []
        for name, result in screener_results.items():
            report["screeners"].append({
                "name": name,
                "score": result.get("score"),
                "max_score": result.get("max_score"),
                "interpretation": result.get("interpretation"),
                "severity": result.get("severity"),
                "clinical_significance": result.get("clinical_significance"),
                "subscales": result.get("subscales")
            })
        
        # If no screeners from session, keep LLM's version (fallback)
        if not report["screeners"] and screener_results:
            report["screeners"] = report.get("screeners", [])
        
        return report
    
    def _format_conversation(self, history: List[Dict[str, Any]]) -> str:
        """Format conversation history for report generation"""
        formatted = []
        for msg in history:
            role = "Patient" if msg["role"] == "user" else "Ava"
            content = msg["content"]
            formatted.append(f"{role}: {content}")
        
        return "\n\n".join(formatted)
    
    def _format_screeners(self, screener_scores: Dict[str, Any]) -> str:
        """Format screener results for report generation"""
        if not screener_scores:
            return "No screeners administered yet."
        
        formatted = []
        for name, result in screener_scores.items():
            formatted.append(f"""
{name}:
- Score: {result.get('score', 'N/A')} / {result.get('max_score', 'N/A')}
- Severity: {result.get('severity', 'N/A')}
- Interpretation: {result.get('interpretation', 'N/A')}
- Clinical Significance: {result.get('clinical_significance', 'N/A')}
""")
        
        return "\n".join(formatted)
    
    def _generate_diagnostic_considerations(self, session_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate diagnostic considerations based on symptom patterns and screener results
        This is for provider review only - not shared with patients
        """
        considerations = {
            "primary_differential_diagnoses": [],
            "supporting_evidence": [],
            "ruling_out": [],
            "severity_indicators": [],
            "treatment_considerations": []
        }
        
        # Analyze symptom patterns
        symptoms = session_data.get("symptoms_detected", {})
        screener_results = session_data.get("screener_scores", {})
        
        # Depression considerations
        if "depression" in symptoms or "PHQ-9" in screener_results:
            phq9_score = screener_results.get("PHQ-9", {}).get("score", 0)
            if phq9_score >= 10:
                considerations["primary_differential_diagnoses"].append("Major Depressive Disorder")
                considerations["supporting_evidence"].append(f"PHQ-9 score: {phq9_score} (moderate-severe depression)")
            elif phq9_score >= 5:
                considerations["primary_differential_diagnoses"].append("Mild Depression or Adjustment Disorder")
                considerations["supporting_evidence"].append(f"PHQ-9 score: {phq9_score} (mild depression)")
        
        # Anxiety considerations
        if "anxiety" in symptoms or "GAD-7" in screener_results:
            gad7_score = screener_results.get("GAD-7", {}).get("score", 0)
            if gad7_score >= 10:
                considerations["primary_differential_diagnoses"].append("Generalized Anxiety Disorder")
                considerations["supporting_evidence"].append(f"GAD-7 score: {gad7_score} (moderate-severe anxiety)")
            elif gad7_score >= 5:
                considerations["primary_differential_diagnoses"].append("Mild Anxiety or Adjustment Disorder")
                considerations["supporting_evidence"].append(f"GAD-7 score: {gad7_score} (mild anxiety)")
        
        # ADHD considerations
        if "attention" in symptoms or "ASRS" in screener_results:
            considerations["primary_differential_diagnoses"].append("Attention-Deficit/Hyperactivity Disorder")
            considerations["supporting_evidence"].append("Attention/concentration difficulties reported")
        
        # Bipolar considerations (if mood symptoms present)
        if "mood" in symptoms:
            considerations["ruling_out"].append("Bipolar Disorder")
            considerations["supporting_evidence"].append("Mood symptoms present - rule out bipolar disorder")
        
        # Trauma considerations
        if "trauma" in symptoms or "PCL-5" in screener_results:
            considerations["primary_differential_diagnoses"].append("Post-Traumatic Stress Disorder")
            considerations["supporting_evidence"].append("Trauma history and PTSD symptoms reported")
        
        # Risk assessment
        if session_data.get("risk_flags"):
            considerations["severity_indicators"].append("High-risk presentation identified")
            considerations["treatment_considerations"].append("Immediate safety assessment and crisis intervention needed")
        
        # Treatment considerations based on severity
        if any(score >= 10 for score in [screener_results.get("PHQ-9", {}).get("score", 0), 
                                       screener_results.get("GAD-7", {}).get("score", 0)]):
            considerations["treatment_considerations"].append("Consider medication evaluation and psychotherapy")
        elif any(score >= 5 for score in [screener_results.get("PHQ-9", {}).get("score", 0), 
                                        screener_results.get("GAD-7", {}).get("score", 0)]):
            considerations["treatment_considerations"].append("Consider psychotherapy and lifestyle interventions")
        
        return considerations
    
    async def generate_clinician_report(
        self,
        session_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate comprehensive CLINICIAN-FOCUSED report with full diagnostic reasoning
        
        Args:
            session_data: Complete session data with conversation history and screeners
            
        Returns:
            Detailed structured report for providers (2-3X more detailed than patient report)
        """
        # Build conversation summary
        conversation_text = self._format_conversation(session_data.get("conversation_history", []))
        
        # Format screener results
        screener_results = session_data.get("screener_scores", {})
        screener_summary = self._format_screeners(screener_results)
        
        # Create prompt for clinician report generation
        messages = [
            {"role": "system", "content": CLINICIAN_REPORT_GENERATION_PROMPT},
            {"role": "user", "content": f"""Generate a comprehensive CLINICIAN REPORT with full diagnostic reasoning based on this information:

**CONVERSATION:**
{conversation_text}

**SCREENER RESULTS:**
{screener_summary}

**DETECTED SYMPTOMS:**
{json.dumps(session_data.get('symptoms_detected', {}), indent=2)}

**RISK FLAGS:**
{json.dumps(session_data.get('risk_flags', []), indent=2)}

Generate the detailed clinical JSON report now with ALL sections including diagnostic reasoning, mental status exam, treatment recommendations, complexity assessment, and barriers."""}
        ]
        
        # Get structured JSON response
        report = await llm_service.get_structured_completion(messages, response_format={})
        
        # Generate dashboard first
        dashboard = generate_clinical_action_dashboard(report)
        
        # Add metadata
        report["patient_id"] = session_data.get("patient_id") or str(uuid.uuid4())
        report["date"] = datetime.utcnow().isoformat()
        
        # Add dashboard to the beginning of the report
        report["action_dashboard"] = dashboard
        
        # Ensure screeners field is populated with ALL completed screeners from session
        report["screeners"] = []
        for name, result in screener_results.items():
            screener_dict = {
                "name": name,
                "score": result.get("score"),
                "max_score": result.get("max_score"),
                "interpretation": result.get("interpretation"),
                "severity": result.get("severity"),
                "clinical_significance": result.get("clinical_significance"),
                "subscales": result.get("subscales")
            }
            # Add item analysis if generated by LLM for this screener
            if "item_analysis" in result:
                screener_dict["item_analysis"] = result["item_analysis"]
            
            report["screeners"].append(screener_dict)
        
        return report
    
    async def generate_dual_reports(
        self,
        session_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate BOTH patient and clinician reports
        
        Args:
            session_data: Complete session data
            
        Returns:
            dict with 'patient_report' and 'clinician_report' keys
        """
        # Generate both reports in parallel would be ideal, but for now sequential is fine
        patient_report = await self.generate_report(session_data)
        clinician_report = await self.generate_clinician_report(session_data)
        
        return {
            "patient_report": patient_report,
            "clinician_report": clinician_report
        }


# Global report service instance
report_service = ReportService()

