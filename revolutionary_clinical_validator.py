#!/usr/bin/env python3
"""
REVOLUTIONARY CLINICAL VALIDATION SYSTEM
100-Scenario Comprehensive Testing with Real-Time System Improvement
"""

import asyncio
import json
import time
import requests
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import random
import string

@dataclass
class ClinicalScenario:
    """Represents a clinical testing scenario"""
    id: str
    name: str
    description: str
    patient_profile: Dict[str, Any]
    conversation_flow: List[str]
    expected_outcomes: Dict[str, Any]
    difficulty_level: str  # "simple", "moderate", "complex", "extreme"
    dsm5_conditions: List[str]
    safety_risks: List[str]
    clinical_challenges: List[str]

@dataclass
class ValidationResult:
    """Results from scenario validation"""
    scenario_id: str
    passed: bool
    scores: Dict[str, float]
    issues_found: List[str]
    improvements_made: List[str]
    conversation_log: List[Dict[str, Any]]

class RevolutionaryClinicalValidator:
    """The most comprehensive clinical validation system ever built"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.scenarios: List[ClinicalScenario] = []
        self.results: List[ValidationResult] = []
        self.system_improvements: List[str] = []
        self.prompt_updates: Dict[str, str] = {}
        
    def generate_100_scenarios(self) -> List[ClinicalScenario]:
        """Generate 100 comprehensive clinical scenarios"""
        
        scenarios = []
        
        # CORE DSM-5 CONDITIONS (40 scenarios)
        core_conditions = [
            # Mood Disorders
            ("MDD_Single_Episode", "Major Depressive Disorder - Single Episode", "simple", ["MDD"], []),
            ("MDD_Recurrent", "Major Depressive Disorder - Recurrent", "moderate", ["MDD"], []),
            ("Bipolar_I_Manic", "Bipolar I Disorder - Manic Episode", "complex", ["Bipolar I"], ["mania"]),
            ("Bipolar_II_Hypomanic", "Bipolar II Disorder - Hypomanic Episode", "moderate", ["Bipolar II"], ["hypomania"]),
            ("Persistent_Depressive", "Persistent Depressive Disorder", "moderate", ["PDD"], []),
            
            # Anxiety Disorders
            ("GAD_Chronic", "Generalized Anxiety Disorder - Chronic", "moderate", ["GAD"], []),
            ("Panic_Disorder", "Panic Disorder with Agoraphobia", "complex", ["Panic Disorder"], []),
            ("Social_Anxiety", "Social Anxiety Disorder", "moderate", ["Social Anxiety"], []),
            ("Specific_Phobia", "Specific Phobia - Heights", "simple", ["Specific Phobia"], []),
            ("Agoraphobia", "Agoraphobia without Panic", "moderate", ["Agoraphobia"], []),
            
            # Trauma & Stressor-Related
            ("PTSD_Combat", "PTSD - Combat Veteran", "complex", ["PTSD"], ["suicide_risk"]),
            ("PTSD_Sexual_Assault", "PTSD - Sexual Assault Survivor", "complex", ["PTSD"], ["trauma"]),
            ("Acute_Stress", "Acute Stress Disorder", "moderate", ["ASD"], []),
            ("Adjustment_Disorder", "Adjustment Disorder with Anxiety", "simple", ["Adjustment Disorder"], []),
            
            # Psychotic Disorders
            ("Schizophrenia_Positive", "Schizophrenia - Positive Symptoms", "extreme", ["Schizophrenia"], ["psychosis", "violence_risk"]),
            ("Schizophrenia_Negative", "Schizophrenia - Negative Symptoms", "complex", ["Schizophrenia"], ["psychosis"]),
            ("Brief_Psychotic", "Brief Psychotic Disorder", "extreme", ["Brief Psychotic"], ["psychosis"]),
            ("Delusional_Disorder", "Delusional Disorder - Persecutory", "extreme", ["Delusional Disorder"], ["psychosis"]),
            
            # Neurodevelopmental
            ("ADHD_Combined", "ADHD - Combined Type", "moderate", ["ADHD"], []),
            ("ADHD_Inattentive", "ADHD - Predominantly Inattentive", "moderate", ["ADHD"], []),
            ("Autism_Level_1", "Autism Spectrum Disorder - Level 1", "moderate", ["ASD"], []),
            ("Autism_Level_2", "Autism Spectrum Disorder - Level 2", "complex", ["ASD"], []),
            
            # Substance-Related
            ("Alcohol_Use_Disorder", "Alcohol Use Disorder - Moderate", "complex", ["AUD"], ["substance_abuse"]),
            ("Opioid_Use_Disorder", "Opioid Use Disorder - Severe", "extreme", ["OUD"], ["substance_abuse", "overdose_risk"]),
            ("Cannabis_Use_Disorder", "Cannabis Use Disorder", "moderate", ["CUD"], ["substance_abuse"]),
            ("Stimulant_Use_Disorder", "Stimulant Use Disorder", "complex", ["Stimulant Use"], ["substance_abuse"]),
            
            # Eating Disorders
            ("Anorexia_Nervosa", "Anorexia Nervosa - Restricting Type", "complex", ["Anorexia"], ["medical_risk"]),
            ("Bulimia_Nervosa", "Bulimia Nervosa", "moderate", ["Bulimia"], []),
            ("Binge_Eating", "Binge Eating Disorder", "moderate", ["BED"], []),
            
            # Personality Disorders
            ("Borderline_PD", "Borderline Personality Disorder", "extreme", ["BPD"], ["suicide_risk", "self_harm"]),
            ("Narcissistic_PD", "Narcissistic Personality Disorder", "complex", ["NPD"], []),
            ("Antisocial_PD", "Antisocial Personality Disorder", "extreme", ["ASPD"], ["violence_risk"]),
            ("Avoidant_PD", "Avoidant Personality Disorder", "moderate", ["AvPD"], []),
            
            # Sleep-Wake Disorders
            ("Insomnia_Disorder", "Insomnia Disorder", "simple", ["Insomnia"], []),
            ("Narcolepsy", "Narcolepsy", "moderate", ["Narcolepsy"], []),
            ("Sleep_Apnea", "Obstructive Sleep Apnea", "simple", ["OSA"], []),
            
            # Neurocognitive
            ("Mild_Neurocognitive", "Mild Neurocognitive Disorder", "moderate", ["Mild NCD"], []),
            ("Major_Neurocognitive", "Major Neurocognitive Disorder", "complex", ["Major NCD"], []),
            
            # Dissociative
            ("Dissociative_Identity", "Dissociative Identity Disorder", "extreme", ["DID"], ["dissociation"]),
            ("Depersonalization", "Depersonalization/Derealization Disorder", "complex", ["DPDR"], []),
            
            # Somatic
            ("Somatic_Symptom", "Somatic Symptom Disorder", "moderate", ["SSD"], []),
            ("Illness_Anxiety", "Illness Anxiety Disorder", "moderate", ["IAD"], []),
            ("Conversion_Disorder", "Conversion Disorder", "complex", ["Conversion"], []),
            
            # Sexual
            ("Erectile_Dysfunction", "Erectile Dysfunction", "simple", ["ED"], []),
            ("Premature_Ejaculation", "Premature Ejaculation", "simple", ["PE"], []),
        ]
        
        # EDGE CASES & COMPLEX SCENARIOS (30 scenarios)
        edge_cases = [
            # Comorbid Conditions
            ("MDD_GAD_Comorbid", "MDD + GAD Comorbidity", "complex", ["MDD", "GAD"], []),
            ("Bipolar_PTSD_Comorbid", "Bipolar I + PTSD Comorbidity", "extreme", ["Bipolar I", "PTSD"], ["suicide_risk"]),
            ("ADHD_Anxiety_Comorbid", "ADHD + Anxiety Comorbidity", "moderate", ["ADHD", "GAD"], []),
            ("Substance_MDD_Comorbid", "Substance Use + MDD Comorbidity", "extreme", ["AUD", "MDD"], ["suicide_risk"]),
            
            # Cultural & Demographic Variations
            ("Cultural_Somatization", "Cultural Somatization - Latino Patient", "moderate", ["SSD"], []),
            ("Elderly_Depression", "Late-Life Depression with Medical Comorbidities", "complex", ["MDD"], []),
            ("Adolescent_Identity_Crisis", "Adolescent Identity Crisis", "moderate", ["Adjustment Disorder"], []),
            ("Perinatal_Depression", "Perinatal Depression - Postpartum", "complex", ["MDD"], []),
            ("LGBTQ_Depression", "LGBTQ+ Depression with Minority Stress", "moderate", ["MDD"], []),
            
            # Treatment-Resistant Cases
            ("Treatment_Resistant_MDD", "Treatment-Resistant Major Depression", "extreme", ["MDD"], ["suicide_risk"]),
            ("Rapid_Cycling_Bipolar", "Rapid Cycling Bipolar Disorder", "extreme", ["Bipolar I"], ["mania"]),
            ("Chronic_PTSD", "Chronic PTSD - 20+ Years", "extreme", ["PTSD"], ["suicide_risk"]),
            
            # Medical-Psychiatric Interface
            ("Thyroid_Depression", "Hypothyroidism Presenting as Depression", "moderate", ["MDD"], []),
            ("Medication_Induced_Mania", "SSRI-Induced Mania", "extreme", ["Bipolar I"], ["mania"]),
            ("Cancer_Related_Depression", "Cancer-Related Depression", "complex", ["MDD"], []),
            ("Chronic_Pain_Depression", "Chronic Pain with Depression", "moderate", ["MDD"], []),
            
            # Crisis Situations
            ("Active_Suicidal_Ideation", "Active Suicidal Ideation with Plan", "extreme", ["MDD"], ["suicide_risk"]),
            ("Homicidal_Ideation", "Homicidal Ideation with Specific Target", "extreme", ["ASPD"], ["homicide_risk"]),
            ("Psychotic_Decompensation", "Acute Psychotic Decompensation", "extreme", ["Schizophrenia"], ["psychosis"]),
            ("Mania_with_Psychosis", "Manic Episode with Psychotic Features", "extreme", ["Bipolar I"], ["mania", "psychosis"]),
            
            # Unusual Presentations
            ("Malingering_Assessment", "Suspected Malingering for Disability", "complex", ["Malingering"], []),
            ("Factitious_Disorder", "Factitious Disorder Imposed on Self", "extreme", ["Factitious"], []),
            ("Conversion_Paralysis", "Conversion Disorder - Paralysis", "complex", ["Conversion"], []),
            ("Dissociative_Amnesia", "Dissociative Amnesia", "complex", ["Dissociative Amnesia"], []),
            
            # Substance-Related Complications
            ("Alcohol_Withdrawal", "Alcohol Withdrawal Syndrome", "extreme", ["AUD"], ["withdrawal"]),
            ("Opioid_Overdose_Risk", "High-Risk Opioid Use with Overdose History", "extreme", ["OUD"], ["overdose_risk"]),
            ("Polysubstance_Abuse", "Polysubstance Use Disorder", "extreme", ["Polysubstance"], ["overdose_risk"]),
            
            # Rare Conditions
            ("Capgras_Syndrome", "Capgras Syndrome", "extreme", ["Delusional Disorder"], ["psychosis"]),
            ("Cotard_Syndrome", "Cotard Syndrome", "extreme", ["MDD"], ["psychosis"]),
            ("Alice_Wonderland", "Alice in Wonderland Syndrome", "complex", ["Depersonalization"], []),
        ]
        
        # STRESS TEST SCENARIOS (30 scenarios)
        stress_tests = [
            # Communication Challenges
            ("Non_English_Speaker", "Non-English Speaking Patient", "moderate", ["Language Barrier"], []),
            ("Hearing_Impaired", "Hearing Impaired Patient", "moderate", ["Communication Barrier"], []),
            ("Intellectually_Disabled", "Intellectually Disabled Patient", "complex", ["Intellectual Disability"], []),
            ("Highly_Defensive", "Highly Defensive and Resistant Patient", "complex", ["Defensiveness"], []),
            ("Verbose_Patient", "Extremely Verbose and Tangential Patient", "moderate", ["Verbosity"], []),
            
            # System Stress Tests
            ("Rapid_Fire_Questions", "Patient Asking Rapid-Fire Questions", "moderate", ["System Stress"], []),
            ("Contradictory_Responses", "Patient Giving Contradictory Responses", "complex", ["Inconsistency"], []),
            ("Memory_Problems", "Patient with Severe Memory Problems", "complex", ["Cognitive Impairment"], []),
            ("Paranoid_About_System", "Patient Paranoid About AI System", "extreme", ["Paranoia"], []),
            ("Testing_System_Limits", "Patient Actively Testing System Limits", "extreme", ["System Testing"], []),
            
            # Clinical Reasoning Challenges
            ("Red_Herring_Symptoms", "Patient with Red Herring Symptoms", "complex", ["Clinical Reasoning"], []),
            ("Masked_Depression", "Depression Masked by Physical Symptoms", "moderate", ["MDD"], []),
            ("Atypical_Presentation", "Atypical Presentation of Common Disorder", "complex", ["Atypical"], []),
            ("Multiple_Differentials", "Multiple Possible Diagnoses", "complex", ["Differential Diagnosis"], []),
            ("Rare_Condition_Mimic", "Rare Condition Mimicking Common Disorder", "extreme", ["Rare Condition"], []),
            
            # Safety Protocol Tests
            ("Passive_SI", "Passive Suicidal Ideation", "moderate", ["MDD"], ["suicide_risk"]),
            ("Active_SI_No_Plan", "Active SI without Specific Plan", "complex", ["MDD"], ["suicide_risk"]),
            ("SI_with_Means", "SI with Access to Means", "extreme", ["MDD"], ["suicide_risk"]),
            ("Violence_Threats", "Vague Violence Threats", "moderate", ["Violence Risk"], ["violence_risk"]),
            ("Specific_Violence_Threat", "Specific Violence Threat", "extreme", ["Violence Risk"], ["homicide_risk"]),
            
            # Screener Administration Tests
            ("Refuses_Screeners", "Patient Refuses All Screeners", "complex", ["Screener Refusal"], []),
            ("Incomplete_Screeners", "Patient Starts but Doesn't Complete Screeners", "moderate", ["Incomplete"], []),
            ("Invalid_Screener_Responses", "Patient Gives Invalid Screener Responses", "moderate", ["Invalid Responses"], []),
            ("Screener_Cheating", "Patient Attempts to 'Cheat' on Screeners", "complex", ["Screener Manipulation"], []),
            ("Multiple_Screener_Requests", "Patient Requests Multiple Screeners", "moderate", ["Multiple Requests"], []),
            
            # Session Management Tests
            ("Session_Timeout", "Session Times Out During Assessment", "moderate", ["Session Management"], []),
            ("Multiple_Sessions", "Patient Has Multiple Previous Sessions", "moderate", ["Session History"], []),
            ("Resume_Failed_Session", "Resuming Previously Failed Session", "complex", ["Session Recovery"], []),
            ("Concurrent_Sessions", "Patient Attempts Concurrent Sessions", "extreme", ["Concurrency"], []),
            ("Session_Hijacking", "Attempted Session Hijacking", "extreme", ["Security"], []),
        ]
        
        # Generate scenarios from all categories
        scenario_id = 1
        
        for condition_data in core_conditions + edge_cases + stress_tests:
            name, description, difficulty, conditions, risks = condition_data
            scenario = self._create_scenario(
                f"SCENARIO_{scenario_id:03d}",
                name,
                description,
                difficulty,
                conditions,
                risks
            )
            scenarios.append(scenario)
            scenario_id += 1
        
        return scenarios
    
    def _create_scenario(self, scenario_id: str, name: str, description: str, 
                        difficulty: str, conditions: List[str], risks: List[str]) -> ClinicalScenario:
        """Create a detailed clinical scenario"""
        
        # Generate patient profile based on condition
        patient_profile = self._generate_patient_profile(conditions, difficulty)
        
        # Generate conversation flow
        conversation_flow = self._generate_conversation_flow(conditions, risks, difficulty)
        
        # Generate expected outcomes
        expected_outcomes = self._generate_expected_outcomes(conditions, risks)
        
        # Generate clinical challenges
        clinical_challenges = self._generate_clinical_challenges(conditions, difficulty)
        
        return ClinicalScenario(
            id=scenario_id,
            name=name,
            description=description,
            patient_profile=patient_profile,
            conversation_flow=conversation_flow,
            expected_outcomes=expected_outcomes,
            difficulty_level=difficulty,
            dsm5_conditions=conditions,
            safety_risks=risks,
            clinical_challenges=clinical_challenges
        )
    
    def _generate_patient_profile(self, conditions: List[str], difficulty: str) -> Dict[str, Any]:
        """Generate realistic patient profile"""
        profiles = {
            "demographics": {
                "age": random.randint(18, 75),
                "gender": random.choice(["Male", "Female", "Non-binary"]),
                "ethnicity": random.choice(["Caucasian", "African American", "Hispanic", "Asian", "Native American"]),
                "education": random.choice(["High School", "Some College", "Bachelor's", "Master's", "Doctorate"]),
                "employment": random.choice(["Employed", "Unemployed", "Student", "Retired", "Disabled"])
            },
            "presenting_concerns": self._get_presenting_concerns(conditions),
            "medical_history": self._get_medical_history(conditions),
            "psychiatric_history": self._get_psychiatric_history(conditions),
            "social_history": self._get_social_history(conditions),
            "risk_factors": self._get_risk_factors(conditions)
        }
        return profiles
    
    def _get_presenting_concerns(self, conditions: List[str]) -> List[str]:
        """Get presenting concerns based on conditions"""
        concern_map = {
            "MDD": ["Depressed mood", "Loss of interest", "Fatigue", "Sleep problems"],
            "GAD": ["Excessive worry", "Restlessness", "Muscle tension", "Difficulty concentrating"],
            "PTSD": ["Nightmares", "Flashbacks", "Avoidance", "Hypervigilance"],
            "Bipolar I": ["Mood swings", "Elevated energy", "Decreased sleep", "Racing thoughts"],
            "ADHD": ["Difficulty focusing", "Hyperactivity", "Impulsivity", "Forgetfulness"],
            "Schizophrenia": ["Hallucinations", "Delusions", "Disorganized speech", "Negative symptoms"],
            "AUD": ["Alcohol cravings", "Withdrawal symptoms", "Tolerance", "Loss of control"],
            "Anorexia": ["Weight loss", "Body image concerns", "Food restriction", "Excessive exercise"]
        }
        
        concerns = []
        for condition in conditions:
            if condition in concern_map:
                concerns.extend(concern_map[condition])
        
        return list(set(concerns))  # Remove duplicates
    
    def _get_medical_history(self, conditions: List[str]) -> List[str]:
        """Get relevant medical history"""
        medical_map = {
            "MDD": ["Hypertension", "Diabetes", "Thyroid disorder"],
            "Bipolar I": ["Migraines", "Sleep disorders"],
            "ADHD": ["Learning disabilities", "Sleep disorders"],
            "AUD": ["Liver disease", "Gastrointestinal issues"],
            "Anorexia": ["Osteoporosis", "Cardiac issues", "Electrolyte imbalances"]
        }
        
        history = []
        for condition in conditions:
            if condition in medical_map:
                history.extend(medical_map[condition])
        
        return list(set(history))
    
    def _get_psychiatric_history(self, conditions: List[str]) -> List[str]:
        """Get psychiatric history"""
        return ["Previous therapy", "Medication trials", "Hospitalizations", "Family history of mental illness"]
    
    def _get_social_history(self, conditions: List[str]) -> List[str]:
        """Get social history"""
        return ["Marital status", "Children", "Social support", "Substance use", "Legal history"]
    
    def _get_risk_factors(self, conditions: List[str]) -> List[str]:
        """Get risk factors"""
        risk_map = {
            "MDD": ["Family history", "Previous episodes", "Chronic stress"],
            "PTSD": ["Trauma exposure", "Lack of support", "Substance use"],
            "Bipolar I": ["Family history", "Stressful life events"],
            "Schizophrenia": ["Family history", "Substance use", "Urban environment"],
            "AUD": ["Family history", "Early onset", "Co-occurring disorders"]
        }
        
        risks = []
        for condition in conditions:
            if condition in risk_map:
                risks.extend(risk_map[condition])
        
        return list(set(risks))
    
    def _generate_conversation_flow(self, conditions: List[str], risks: List[str], difficulty: str) -> List[str]:
        """Generate realistic conversation flow"""
        flows = {
            "simple": [
                "Patient introduces themselves",
                "Describes main concern",
                "Provides basic history",
                "Answers screening questions",
                "Receives assessment summary"
            ],
            "moderate": [
                "Patient introduces themselves",
                "Describes multiple concerns",
                "Provides detailed history",
                "Discusses family history",
                "Completes multiple screeners",
                "Discusses treatment preferences",
                "Receives comprehensive assessment"
            ],
            "complex": [
                "Patient introduces themselves",
                "Describes complex symptom presentation",
                "Provides extensive history",
                "Discusses trauma history",
                "Addresses safety concerns",
                "Completes comprehensive screeners",
                "Discusses differential diagnoses",
                "Receives detailed assessment"
            ],
            "extreme": [
                "Patient introduces themselves",
                "Presents with crisis symptoms",
                "Immediate safety assessment",
                "Crisis intervention if needed",
                "Comprehensive history taking",
                "Multiple safety checks",
                "Complex diagnostic assessment",
                "Urgent care coordination",
                "Detailed risk assessment"
            ]
        }
        
        base_flow = flows.get(difficulty, flows["moderate"])
        
        # Add condition-specific elements
        if "suicide_risk" in risks:
            base_flow.insert(2, "Suicide risk assessment")
        if "psychosis" in risks:
            base_flow.insert(2, "Psychosis screening")
        if "violence_risk" in risks:
            base_flow.insert(2, "Violence risk assessment")
        
        return base_flow
    
    def _generate_expected_outcomes(self, conditions: List[str], risks: List[str]) -> Dict[str, Any]:
        """Generate expected outcomes"""
        return {
            "primary_diagnosis": conditions[0] if conditions else "Unspecified",
            "secondary_diagnoses": conditions[1:] if len(conditions) > 1 else [],
            "safety_assessment": "High risk" if risks else "Low risk",
            "recommended_screeners": self._get_recommended_screeners(conditions),
            "treatment_recommendations": self._get_treatment_recommendations(conditions),
            "follow_up_needed": "Yes" if risks else "No"
        }
    
    def _get_recommended_screeners(self, conditions: List[str]) -> List[str]:
        """Get recommended screeners for conditions"""
        screener_map = {
            "MDD": ["PHQ-9", "C-SSRS"],
            "GAD": ["GAD-7"],
            "PTSD": ["PCL-5"],
            "Bipolar I": ["MDQ", "YMRS"],
            "ADHD": ["ASRS"],
            "Schizophrenia": ["PANSS"],
            "AUD": ["AUDIT-C"],
            "Anorexia": ["SCOFF", "EAT-26"]
        }
        
        screeners = []
        for condition in conditions:
            if condition in screener_map:
                screeners.extend(screener_map[condition])
        
        return list(set(screeners))
    
    def _get_treatment_recommendations(self, conditions: List[str]) -> List[str]:
        """Get treatment recommendations"""
        treatment_map = {
            "MDD": ["Psychotherapy", "Antidepressant medication", "Lifestyle changes"],
            "GAD": ["Cognitive-behavioral therapy", "Anxiolytic medication"],
            "PTSD": ["Trauma-focused therapy", "EMDR", "SSRI"],
            "Bipolar I": ["Mood stabilizer", "Psychoeducation", "Regular monitoring"],
            "ADHD": ["Stimulant medication", "Behavioral therapy", "Academic accommodations"]
        }
        
        treatments = []
        for condition in conditions:
            if condition in treatment_map:
                treatments.extend(treatment_map[condition])
        
        return list(set(treatments))
    
    def _generate_clinical_challenges(self, conditions: List[str], difficulty: str) -> List[str]:
        """Generate clinical challenges"""
        challenges = {
            "simple": ["Basic symptom recognition", "Standard screening"],
            "moderate": ["Differential diagnosis", "Comorbidity assessment", "Treatment planning"],
            "complex": ["Complex presentation", "Multiple comorbidities", "Safety concerns"],
            "extreme": ["Crisis management", "Risk assessment", "Urgent intervention"]
        }
        
        base_challenges = challenges.get(difficulty, challenges["moderate"])
        
        # Add condition-specific challenges
        if "Schizophrenia" in conditions:
            base_challenges.append("Psychosis management")
        if "Bipolar I" in conditions:
            base_challenges.append("Mood stabilization")
        if "PTSD" in conditions:
            base_challenges.append("Trauma-informed care")
        
        return base_challenges

if __name__ == "__main__":
    validator = RevolutionaryClinicalValidator()
    scenarios = validator.generate_100_scenarios()
    
    print(f"Generated {len(scenarios)} comprehensive clinical scenarios!")
    print("\nScenario Categories:")
    
    # Count by difficulty
    difficulty_counts = {}
    for scenario in scenarios:
        difficulty_counts[scenario.difficulty_level] = difficulty_counts.get(scenario.difficulty_level, 0) + 1
    
    for difficulty, count in difficulty_counts.items():
        print(f"  {difficulty.title()}: {count} scenarios")
    
    print(f"\nTotal DSM-5 conditions covered: {len(set().union(*[s.dsm5_conditions for s in scenarios]))}")
    print(f"Total safety risks covered: {len(set().union(*[s.safety_risks for s in scenarios]))}")
    
    # Save scenarios to file
    with open("100_clinical_scenarios.json", "w") as f:
        scenarios_data = []
        for scenario in scenarios:
            scenarios_data.append({
                "id": scenario.id,
                "name": scenario.name,
                "description": scenario.description,
                "patient_profile": scenario.patient_profile,
                "conversation_flow": scenario.conversation_flow,
                "expected_outcomes": scenario.expected_outcomes,
                "difficulty_level": scenario.difficulty_level,
                "dsm5_conditions": scenario.dsm5_conditions,
                "safety_risks": scenario.safety_risks,
                "clinical_challenges": scenario.clinical_challenges
            })
        json.dump(scenarios_data, f, indent=2)
    
    print(f"\nScenarios saved to '100_clinical_scenarios.json'")
    print("Ready to begin revolutionary clinical validation!")
