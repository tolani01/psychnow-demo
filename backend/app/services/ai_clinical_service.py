"""
AI Clinical Service - Advanced clinical decision support and insights
Provides AI-powered diagnostic assistance, pattern recognition, and treatment recommendations
"""

import json
import re
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from sqlalchemy.orm import Session

from app.models.intake_report import IntakeReport
from app.models.user import User
from app.services.llm_service import llm_service


class AIClinicalService:
    """Service for AI-powered clinical insights and decision support"""
    
    def __init__(self):
        self.llm_service = llm_service
        
        # Clinical pattern recognition rules
        self.symptom_patterns = {
            "depression": {
                "keywords": ["depressed", "sad", "hopeless", "worthless", "guilty", "suicidal"],
                "screeners": ["PHQ-9", "BDI", "CES-D"],
                "severity_indicators": ["suicidal", "self-harm", "severe", "extreme"]
            },
            "anxiety": {
                "keywords": ["anxious", "worried", "panic", "fear", "nervous", "restless"],
                "screeners": ["GAD-7", "BAI", "STAI"],
                "severity_indicators": ["panic", "severe", "debilitating", "constant"]
            },
            "trauma": {
                "keywords": ["trauma", "ptsd", "flashback", "nightmare", "trigger", "abuse"],
                "screeners": ["PCL-5", "IES-R", "CAPS"],
                "severity_indicators": ["severe", "frequent", "debilitating", "flashback"]
            },
            "adhd": {
                "keywords": ["attention", "focus", "hyperactive", "impulsive", "distracted"],
                "screeners": ["ASRS", "ADHD-RS", "CPRS"],
                "severity_indicators": ["severe", "significant", "impairment", "constant"]
            },
            "bipolar": {
                "keywords": ["mania", "manic", "bipolar", "mood swings", "elevated", "irritable"],
                "screeners": ["YMRS", "MDQ", "BSDS"],
                "severity_indicators": ["mania", "severe", "psychotic", "hospitalization"]
            },
            "substance_use": {
                "keywords": ["alcohol", "drug", "substance", "addiction", "withdrawal", "overdose"],
                "screeners": ["AUDIT", "DAST", "CAGE"],
                "severity_indicators": ["severe", "dependence", "overdose", "withdrawal"]
            }
        }
        
        # Treatment recommendations database
        self.treatment_recommendations = {
            "depression": {
                "mild": ["Psychotherapy (CBT)", "Lifestyle modifications", "Regular follow-up"],
                "moderate": ["Psychotherapy (CBT/IPT)", "SSRI medication", "Regular monitoring"],
                "severe": ["SSRI/SNRI medication", "Intensive psychotherapy", "Close monitoring", "Safety planning"]
            },
            "anxiety": {
                "mild": ["Psychotherapy (CBT)", "Relaxation techniques", "Regular follow-up"],
                "moderate": ["CBT/Exposure therapy", "SSRI medication", "Regular monitoring"],
                "severe": ["SSRI/SNRI medication", "Intensive CBT", "Close monitoring", "Crisis planning"]
            },
            "trauma": {
                "mild": ["Psychoeducation", "Grounding techniques", "Regular follow-up"],
                "moderate": ["Trauma-focused CBT", "EMDR", "Regular monitoring"],
                "severe": ["Trauma-focused CBT", "EMDR", "SSRI medication", "Close monitoring", "Safety planning"]
            },
            "adhd": {
                "mild": ["Behavioral strategies", "Environmental modifications", "Regular follow-up"],
                "moderate": ["Stimulant medication", "Behavioral therapy", "Regular monitoring"],
                "severe": ["Stimulant medication", "Intensive behavioral therapy", "Close monitoring", "Academic/workplace accommodations"]
            },
            "bipolar": {
                "mild": ["Mood stabilizer", "Psychoeducation", "Regular follow-up"],
                "moderate": ["Mood stabilizer", "Psychotherapy", "Regular monitoring"],
                "severe": ["Mood stabilizer", "Antipsychotic medication", "Intensive psychotherapy", "Close monitoring", "Hospitalization consideration"]
            },
            "substance_use": {
                "mild": ["Psychoeducation", "Motivational interviewing", "Regular follow-up"],
                "moderate": ["Substance abuse counseling", "Medication-assisted treatment", "Regular monitoring"],
                "severe": ["Intensive outpatient program", "Medication-assisted treatment", "Close monitoring", "Detoxification consideration"]
            }
        }
    
    async def analyze_clinical_data(
        self,
        report_data: Dict[str, Any],
        screener_scores: Dict[str, Any],
        conversation_history: List[Dict[str, str]],
        db: Session = None
    ) -> Dict[str, Any]:
        """Comprehensive clinical analysis of patient data"""
        
        try:
            # Extract clinical information
            clinical_info = self._extract_clinical_information(report_data, screener_scores, conversation_history)
            
            # Perform pattern recognition
            pattern_analysis = self._analyze_symptom_patterns(clinical_info)
            
            # Generate AI insights
            ai_insights = await self._generate_ai_insights(clinical_info, pattern_analysis)
            
            # Risk assessment
            risk_assessment = self._assess_clinical_risk(clinical_info, pattern_analysis)
            
            # Treatment recommendations
            treatment_recs = self._generate_treatment_recommendations(pattern_analysis, risk_assessment)
            
            # Differential diagnosis
            differential_diagnosis = self._generate_differential_diagnosis(clinical_info, pattern_analysis)
            
            # Clinical impression
            clinical_impression = self._generate_clinical_impression(clinical_info, pattern_analysis, risk_assessment)
            
            return {
                "clinical_analysis": {
                    "pattern_analysis": pattern_analysis,
                    "risk_assessment": risk_assessment,
                    "differential_diagnosis": differential_diagnosis,
                    "clinical_impression": clinical_impression
                },
                "ai_insights": ai_insights,
                "treatment_recommendations": treatment_recs,
                "confidence_scores": self._calculate_confidence_scores(pattern_analysis),
                "red_flags": self._identify_red_flags(clinical_info, risk_assessment),
                "follow_up_priorities": self._determine_follow_up_priorities(pattern_analysis, risk_assessment),
                "analysis_timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            print(f"Error in clinical analysis: {e}")
            return {
                "error": str(e),
                "clinical_analysis": {},
                "ai_insights": "Analysis failed due to technical error",
                "treatment_recommendations": [],
                "analysis_timestamp": datetime.utcnow().isoformat()
            }
    
    def _extract_clinical_information(
        self,
        report_data: Dict[str, Any],
        screener_scores: Dict[str, Any],
        conversation_history: List[Dict[str, str]]
    ) -> Dict[str, Any]:
        """Extract and structure clinical information from various sources"""
        
        clinical_info = {
            "chief_complaint": report_data.get("chief_complaint", ""),
            "history_of_present_illness": report_data.get("history_of_present_illness", ""),
            "safety_assessment": report_data.get("safety_assessment", ""),
            "psychiatric_history": report_data.get("psychiatric_history", ""),
            "medical_history": report_data.get("medical_history", ""),
            "substance_history": report_data.get("substance_history", ""),
            "family_history": report_data.get("family_history", ""),
            "social_history": report_data.get("social_history", ""),
            "screener_scores": screener_scores,
            "patient_statements": report_data.get("patient_statements", []),
            "conversation_text": self._extract_conversation_text(conversation_history)
        }
        
        return clinical_info
    
    def _extract_conversation_text(self, conversation_history: List[Dict[str, str]]) -> str:
        """Extract patient statements from conversation history"""
        
        patient_statements = []
        for message in conversation_history:
            if message.get("role") == "user":
                patient_statements.append(message.get("content", ""))
        
        return " ".join(patient_statements)
    
    def _analyze_symptom_patterns(self, clinical_info: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze symptom patterns using rule-based and AI approaches"""
        
        pattern_analysis = {
            "detected_conditions": [],
            "symptom_severity": {},
            "pattern_confidence": {},
            "symptom_clusters": {},
            "risk_indicators": []
        }
        
        # Combine all text for analysis
        all_text = " ".join([
            clinical_info.get("chief_complaint", ""),
            clinical_info.get("history_of_present_illness", ""),
            clinical_info.get("conversation_text", ""),
            str(clinical_info.get("patient_statements", []))
        ]).lower()
        
        # Analyze each condition pattern
        for condition, pattern_data in self.symptom_patterns.items():
            confidence_score = 0
            detected_keywords = []
            severity_indicators = []
            
            # Check for keywords
            for keyword in pattern_data["keywords"]:
                if keyword.lower() in all_text:
                    detected_keywords.append(keyword)
                    confidence_score += 1
            
            # Check for severity indicators
            for indicator in pattern_data["severity_indicators"]:
                if indicator.lower() in all_text:
                    severity_indicators.append(indicator)
                    confidence_score += 2
            
            # Check screener scores
            screener_evidence = self._analyze_screener_scores(condition, clinical_info.get("screener_scores", {}))
            if screener_evidence["positive"]:
                confidence_score += screener_evidence["score"]
            
            # Determine severity
            severity = "mild"
            if severity_indicators:
                severity = "severe"
            elif confidence_score >= 3:
                severity = "moderate"
            
            # Add to analysis if confidence is sufficient
            if confidence_score >= 2:
                pattern_analysis["detected_conditions"].append({
                    "condition": condition,
                    "confidence_score": confidence_score,
                    "severity": severity,
                    "detected_keywords": detected_keywords,
                    "severity_indicators": severity_indicators,
                    "screener_evidence": screener_evidence
                })
                
                pattern_analysis["symptom_severity"][condition] = severity
                pattern_analysis["pattern_confidence"][condition] = confidence_score
        
        # Identify symptom clusters
        pattern_analysis["symptom_clusters"] = self._identify_symptom_clusters(pattern_analysis["detected_conditions"])
        
        return pattern_analysis
    
    def _analyze_screener_scores(self, condition: str, screener_scores: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze screener scores for specific conditions"""
        
        screener_mapping = {
            "depression": ["PHQ-9", "BDI", "CES-D"],
            "anxiety": ["GAD-7", "BAI", "STAI"],
            "trauma": ["PCL-5", "IES-R", "CAPS"],
            "adhd": ["ASRS", "ADHD-RS", "CPRS"],
            "bipolar": ["YMRS", "MDQ", "BSDS"],
            "substance_use": ["AUDIT", "DAST", "CAGE"]
        }
        
        relevant_screeners = screener_mapping.get(condition, [])
        evidence = {"positive": False, "score": 0, "screener_details": []}
        
        for screener_name in relevant_screeners:
            if screener_name in screener_scores:
                screener_data = screener_scores[screener_name]
                if isinstance(screener_data, dict):
                    score = screener_data.get("score", 0)
                    max_score = screener_data.get("max_score", 1)
                    severity = screener_data.get("severity", "minimal")
                    
                    evidence["screener_details"].append({
                        "screener": screener_name,
                        "score": score,
                        "max_score": max_score,
                        "severity": severity
                    })
                    
                    # Determine if positive based on severity
                    if severity in ["moderate", "severe"]:
                        evidence["positive"] = True
                        evidence["score"] += 2
                    elif severity == "mild":
                        evidence["score"] += 1
        
        return evidence
    
    def _identify_symptom_clusters(self, detected_conditions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Identify symptom clusters that may indicate specific disorders"""
        
        clusters = {
            "mood_disorders": [],
            "anxiety_disorders": [],
            "trauma_disorders": [],
            "attention_disorders": [],
            "substance_disorders": [],
            "psychotic_disorders": []
        }
        
        condition_mapping = {
            "depression": "mood_disorders",
            "bipolar": "mood_disorders",
            "anxiety": "anxiety_disorders",
            "trauma": "trauma_disorders",
            "adhd": "attention_disorders",
            "substance_use": "substance_disorders"
        }
        
        for condition_data in detected_conditions:
            condition = condition_data["condition"]
            cluster_type = condition_mapping.get(condition, "other")
            if cluster_type in clusters:
                clusters[cluster_type].append(condition_data)
        
        return clusters
    
    async def _generate_ai_insights(
        self,
        clinical_info: Dict[str, Any],
        pattern_analysis: Dict[str, Any]
    ) -> str:
        """Generate AI-powered clinical insights using LLM"""
        
        try:
            # Prepare clinical summary for AI analysis
            clinical_summary = self._prepare_clinical_summary(clinical_info, pattern_analysis)
            
            # Generate AI insights
            prompt = f"""
            As a board-certified psychiatrist with 15+ years of experience, analyze the following clinical data and provide comprehensive insights:

            CLINICAL DATA:
            {json.dumps(clinical_summary, indent=2)}

            Please provide:
            1. Clinical impression and key observations
            2. Symptom pattern analysis
            3. Risk factors and protective factors
            4. Differential diagnostic considerations
            5. Urgency level and immediate concerns
            6. Recommended next steps

            Focus on evidence-based clinical reasoning and provide actionable insights for the treating provider.
            """
            
            insights = await self.llm_service.generate_response(prompt)
            return insights
            
        except Exception as e:
            print(f"Error generating AI insights: {e}")
            return "AI insights generation failed due to technical error."
    
    def _prepare_clinical_summary(
        self,
        clinical_info: Dict[str, Any],
        pattern_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Prepare structured clinical summary for AI analysis"""
        
        return {
            "presenting_problem": {
                "chief_complaint": clinical_info.get("chief_complaint", ""),
                "history_of_present_illness": clinical_info.get("history_of_present_illness", ""),
                "safety_concerns": clinical_info.get("safety_assessment", "")
            },
            "clinical_assessment": {
                "detected_conditions": pattern_analysis.get("detected_conditions", []),
                "symptom_severity": pattern_analysis.get("symptom_severity", {}),
                "symptom_clusters": pattern_analysis.get("symptom_clusters", {}),
                "risk_indicators": pattern_analysis.get("risk_indicators", [])
            },
            "screener_results": clinical_info.get("screener_scores", {}),
            "patient_statements": clinical_info.get("patient_statements", []),
            "historical_information": {
                "psychiatric_history": clinical_info.get("psychiatric_history", ""),
                "medical_history": clinical_info.get("medical_history", ""),
                "substance_history": clinical_info.get("substance_history", ""),
                "family_history": clinical_info.get("family_history", ""),
                "social_history": clinical_info.get("social_history", "")
            }
        }
    
    def _assess_clinical_risk(
        self,
        clinical_info: Dict[str, Any],
        pattern_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Assess clinical risk level and specific risk factors"""
        
        risk_assessment = {
            "overall_risk": "low",
            "risk_factors": [],
            "protective_factors": [],
            "suicide_risk": "low",
            "self_harm_risk": "low",
            "violence_risk": "low",
            "substance_risk": "low"
        }
        
        # Check for high-risk indicators
        all_text = " ".join([
            clinical_info.get("chief_complaint", ""),
            clinical_info.get("safety_assessment", ""),
            clinical_info.get("conversation_text", "")
        ]).lower()
        
        # Suicide risk assessment
        suicide_keywords = ["suicide", "kill myself", "end it all", "not worth living", "better off dead"]
        if any(keyword in all_text for keyword in suicide_keywords):
            risk_assessment["suicide_risk"] = "high"
            risk_assessment["risk_factors"].append("Suicidal ideation expressed")
        
        # Self-harm risk assessment
        self_harm_keywords = ["cut myself", "hurt myself", "self-harm", "self-injury"]
        if any(keyword in all_text for keyword in self_harm_keywords):
            risk_assessment["self_harm_risk"] = "high"
            risk_assessment["risk_factors"].append("Self-harm ideation or behavior")
        
        # Substance use risk
        substance_keywords = ["overdose", "alcohol poisoning", "drug overdose", "withdrawal"]
        if any(keyword in all_text for keyword in substance_keywords):
            risk_assessment["substance_risk"] = "high"
            risk_assessment["risk_factors"].append("Substance use complications")
        
        # Determine overall risk
        high_risk_count = sum([
            1 for risk_type in ["suicide_risk", "self_harm_risk", "substance_risk"]
            if risk_assessment[risk_type] == "high"
        ])
        
        if high_risk_count >= 1:
            risk_assessment["overall_risk"] = "high"
        elif any(condition["severity"] == "severe" for condition in pattern_analysis.get("detected_conditions", [])):
            risk_assessment["overall_risk"] = "moderate"
        
        return risk_assessment
    
    def _generate_treatment_recommendations(
        self,
        pattern_analysis: Dict[str, Any],
        risk_assessment: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate evidence-based treatment recommendations"""
        
        recommendations = {
            "immediate_actions": [],
            "treatment_modalities": [],
            "medication_considerations": [],
            "psychotherapy_recommendations": [],
            "monitoring_plan": [],
            "follow_up_schedule": "routine"
        }
        
        # Immediate actions based on risk
        if risk_assessment["overall_risk"] == "high":
            recommendations["immediate_actions"].append("Immediate safety assessment required")
            recommendations["immediate_actions"].append("Consider crisis intervention")
            recommendations["follow_up_schedule"] = "urgent"
        elif risk_assessment["overall_risk"] == "moderate":
            recommendations["immediate_actions"].append("Close monitoring recommended")
            recommendations["follow_up_schedule"] = "frequent"
        
        # Treatment recommendations for detected conditions
        for condition_data in pattern_analysis.get("detected_conditions", []):
            condition = condition_data["condition"]
            severity = condition_data["severity"]
            
            if condition in self.treatment_recommendations:
                condition_recs = self.treatment_recommendations[condition].get(severity, [])
                recommendations["treatment_modalities"].extend(condition_recs)
        
        # Remove duplicates
        recommendations["treatment_modalities"] = list(set(recommendations["treatment_modalities"]))
        
        # Monitoring plan
        if risk_assessment["overall_risk"] == "high":
            recommendations["monitoring_plan"].append("Daily safety checks")
            recommendations["monitoring_plan"].append("24/7 crisis support available")
        elif risk_assessment["overall_risk"] == "moderate":
            recommendations["monitoring_plan"].append("Weekly check-ins")
            recommendations["monitoring_plan"].append("Crisis plan in place")
        else:
            recommendations["monitoring_plan"].append("Regular follow-up appointments")
        
        return recommendations
    
    def _generate_differential_diagnosis(
        self,
        clinical_info: Dict[str, Any],
        pattern_analysis: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate differential diagnosis based on clinical data"""
        
        differential = []
        
        for condition_data in pattern_analysis.get("detected_conditions", []):
            condition = condition_data["condition"]
            confidence = condition_data["confidence_score"]
            severity = condition_data["severity"]
            
            # Map conditions to diagnostic categories
            diagnostic_mapping = {
                "depression": "Major Depressive Disorder",
                "anxiety": "Generalized Anxiety Disorder",
                "trauma": "Post-Traumatic Stress Disorder",
                "adhd": "Attention-Deficit/Hyperactivity Disorder",
                "bipolar": "Bipolar Disorder",
                "substance_use": "Substance Use Disorder"
            }
            
            diagnosis = diagnostic_mapping.get(condition, condition.title())
            
            differential.append({
                "diagnosis": diagnosis,
                "confidence": confidence,
                "severity": severity,
                "supporting_evidence": condition_data["detected_keywords"],
                "rule_out": self._generate_rule_out_considerations(condition)
            })
        
        # Sort by confidence
        differential.sort(key=lambda x: x["confidence"], reverse=True)
        
        return differential
    
    def _generate_rule_out_considerations(self, condition: str) -> List[str]:
        """Generate rule-out considerations for differential diagnosis"""
        
        rule_out_mapping = {
            "depression": [
                "Bipolar Disorder",
                "Substance-Induced Mood Disorder",
                "Medical conditions affecting mood",
                "Adjustment Disorder"
            ],
            "anxiety": [
                "Generalized Anxiety Disorder",
                "Panic Disorder",
                "Social Anxiety Disorder",
                "Medical conditions causing anxiety"
            ],
            "trauma": [
                "Acute Stress Disorder",
                "Adjustment Disorder",
                "Other trauma-related disorders",
                "Medical conditions mimicking trauma symptoms"
            ],
            "adhd": [
                "Learning disabilities",
                "Anxiety disorders",
                "Bipolar Disorder",
                "Substance use affecting attention"
            ],
            "bipolar": [
                "Major Depressive Disorder",
                "Substance-Induced Mood Disorder",
                "Medical conditions affecting mood",
                "Personality disorders"
            ],
            "substance_use": [
                "Medical conditions",
                "Other psychiatric disorders",
                "Medication side effects",
                "Environmental factors"
            ]
        }
        
        return rule_out_mapping.get(condition, [])
    
    def _generate_clinical_impression(
        self,
        clinical_info: Dict[str, Any],
        pattern_analysis: Dict[str, Any],
        risk_assessment: Dict[str, Any]
    ) -> str:
        """Generate clinical impression summary"""
        
        impressions = []
        
        # Overall presentation
        if pattern_analysis.get("detected_conditions"):
            primary_conditions = [c["condition"] for c in pattern_analysis["detected_conditions"][:2]]
            impressions.append(f"Patient presents with symptoms consistent with {', '.join(primary_conditions)}")
        else:
            impressions.append("Patient presents with non-specific mental health concerns")
        
        # Severity assessment
        severe_conditions = [c["condition"] for c in pattern_analysis.get("detected_conditions", []) if c["severity"] == "severe"]
        if severe_conditions:
            impressions.append(f"Severe symptoms noted in {', '.join(severe_conditions)}")
        
        # Risk assessment
        if risk_assessment["overall_risk"] == "high":
            impressions.append("High risk presentation requiring immediate attention")
        elif risk_assessment["overall_risk"] == "moderate":
            impressions.append("Moderate risk requiring close monitoring")
        else:
            impressions.append("Low risk presentation")
        
        # Functional impact
        if any(c["severity"] in ["moderate", "severe"] for c in pattern_analysis.get("detected_conditions", [])):
            impressions.append("Significant functional impairment likely")
        
        return ". ".join(impressions) + "."
    
    def _calculate_confidence_scores(self, pattern_analysis: Dict[str, Any]) -> Dict[str, float]:
        """Calculate confidence scores for clinical assessments"""
        
        confidence_scores = {}
        
        for condition_data in pattern_analysis.get("detected_conditions", []):
            condition = condition_data["condition"]
            raw_score = condition_data["confidence_score"]
            
            # Normalize to 0-1 scale
            max_possible_score = 10  # Based on keyword count + severity indicators + screener evidence
            normalized_score = min(raw_score / max_possible_score, 1.0)
            
            confidence_scores[condition] = round(normalized_score, 2)
        
        return confidence_scores
    
    def _identify_red_flags(
        self,
        clinical_info: Dict[str, Any],
        risk_assessment: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Identify clinical red flags requiring immediate attention"""
        
        red_flags = []
        
        # Suicide risk
        if risk_assessment["suicide_risk"] == "high":
            red_flags.append({
                "type": "suicide_risk",
                "severity": "critical",
                "description": "Active suicidal ideation or intent",
                "action_required": "Immediate safety assessment and crisis intervention"
            })
        
        # Self-harm risk
        if risk_assessment["self_harm_risk"] == "high":
            red_flags.append({
                "type": "self_harm_risk",
                "severity": "high",
                "description": "Self-harm ideation or behavior",
                "action_required": "Safety planning and close monitoring"
            })
        
        # Substance complications
        if risk_assessment["substance_risk"] == "high":
            red_flags.append({
                "type": "substance_complications",
                "severity": "high",
                "description": "Substance use complications or overdose risk",
                "action_required": "Medical evaluation and substance abuse assessment"
            })
        
        # Psychotic symptoms
        all_text = " ".join([
            clinical_info.get("chief_complaint", ""),
            clinical_info.get("conversation_text", "")
        ]).lower()
        
        psychotic_keywords = ["hallucination", "delusion", "paranoid", "hearing voices", "seeing things"]
        if any(keyword in all_text for keyword in psychotic_keywords):
            red_flags.append({
                "type": "psychotic_symptoms",
                "severity": "high",
                "description": "Possible psychotic symptoms",
                "action_required": "Psychiatric evaluation and safety assessment"
            })
        
        return red_flags
    
    def _determine_follow_up_priorities(
        self,
        pattern_analysis: Dict[str, Any],
        risk_assessment: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Determine follow-up priorities based on clinical assessment"""
        
        priorities = []
        
        # Risk-based priorities
        if risk_assessment["overall_risk"] == "high":
            priorities.append({
                "priority": "immediate",
                "description": "Safety monitoring and crisis intervention",
                "timeline": "within 24 hours"
            })
        elif risk_assessment["overall_risk"] == "moderate":
            priorities.append({
                "priority": "urgent",
                "description": "Close monitoring and safety planning",
                "timeline": "within 48 hours"
            })
        
        # Condition-based priorities
        for condition_data in pattern_analysis.get("detected_conditions", []):
            condition = condition_data["condition"]
            severity = condition_data["severity"]
            
            if severity == "severe":
                priorities.append({
                    "priority": "urgent",
                    "description": f"Treatment initiation for {condition}",
                    "timeline": "within 1 week"
                })
            elif severity == "moderate":
                priorities.append({
                    "priority": "routine",
                    "description": f"Treatment planning for {condition}",
                    "timeline": "within 2 weeks"
                })
        
        return priorities


# Global AI clinical service instance
ai_clinical_service = AIClinicalService()
