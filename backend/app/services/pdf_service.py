"""
PDF Report Generation Service
Generates professional PDF reports from intake data
"""

from datetime import datetime
from typing import Dict, Any, List
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
import io
import base64


class PDFReportService:
    """Service for generating PDF reports from intake data"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Setup custom paragraph styles for the report"""
        # Title style
        self.styles.add(ParagraphStyle(
            name='ReportTitle',
            parent=self.styles['Heading1'],
            fontSize=18,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.darkblue
        ))
        
        # Section headers
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=14,
            spaceAfter=12,
            spaceBefore=20,
            textColor=colors.darkblue
        ))
        
        # Body text
        self.styles.add(ParagraphStyle(
            name='ReportBodyText',
            parent=self.styles['Normal'],
            fontSize=11,
            spaceAfter=6,
            alignment=TA_LEFT
        ))
        
        # Disclaimer style
        self.styles.add(ParagraphStyle(
            name='Disclaimer',
            parent=self.styles['Normal'],
            fontSize=9,
            spaceAfter=6,
            alignment=TA_CENTER,
            textColor=colors.grey
        ))
    
    def _format_date(self, date_str: str) -> str:
        """Format date string for display"""
        if not date_str:
            return "N/A"
        try:
            dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            return dt.strftime('%B %d, %Y at %I:%M %p')
        except:
            return date_str
    
    def generate_patient_report_pdf(self, report_data: Dict[str, Any], patient_name: str = "Patient") -> bytes:
        """Generate a PATIENT-FRIENDLY PDF report (simplified, supportive language)"""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=72, leftMargin=72, 
                              topMargin=72, bottomMargin=18)
        
        story = []
        
        # Title - Patient-Friendly
        story.append(Paragraph("Your Mental Health Assessment Summary", self.styles['ReportTitle']))
        story.append(Spacer(1, 20))
        
        # Header information - Simplified for patients
        header_data = [
            ['Your Name:', patient_name],
            ['Assessment Date:', self._format_date(report_data.get('date'))],
            ['Care Priority:', self._get_patient_friendly_urgency(report_data.get('urgency', 'routine'))]
        ]
        
        header_table = Table(header_data, colWidths=[1.5*inch, 4*inch])
        header_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightblue),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('BACKGROUND', (1, 0), (1, -1), colors.white),
        ]))
        
        story.append(header_table)
        story.append(Spacer(1, 20))
        
        # What You Shared
        if report_data.get('chief_complaint'):
            story.append(Paragraph("What Brought You Here Today", self.styles['SectionHeader']))
            story.append(Paragraph(report_data['chief_complaint'], self.styles['ReportBodyText']))
            story.append(Spacer(1, 12))
        
        # Your Symptoms (Patient-Friendly Summary)
        if report_data.get('history_present_illness'):
            story.append(Paragraph("What You've Been Experiencing", self.styles['SectionHeader']))
            story.append(Paragraph(report_data['history_present_illness'], self.styles['ReportBodyText']))
            story.append(Spacer(1, 12))
        
        # Screening Results - Patient-Friendly Format
        if report_data.get('screeners'):
            story.append(Paragraph("Your Screening Results", self.styles['SectionHeader']))
            story.append(Paragraph("You completed standardized questionnaires that help us understand your symptoms:", self.styles['ReportBodyText']))
            story.append(Spacer(1, 8))
            
            for screener in report_data['screeners']:
                screener_name = screener.get('name', 'Unknown')
                score = screener.get('score', 'N/A')
                max_score = screener.get('max_score', 'N/A')
                interpretation = screener.get('interpretation', '')
                
                # Patient-friendly screener names
                friendly_names = {
                    'PHQ-9': 'Depression Screening (PHQ-9)',
                    'GAD-7': 'Anxiety Screening (GAD-7)',
                    'C-SSRS': 'Safety Assessment (C-SSRS)'
                }
                
                display_name = friendly_names.get(screener_name, screener_name)
                story.append(Paragraph(f"<b>{display_name}:</b> {score}/{max_score}", self.styles['ReportBodyText']))
                if interpretation:
                    story.append(Paragraph(f"Result: {interpretation}", self.styles['ReportBodyText']))
                story.append(Spacer(1, 8))
        
        # Next Steps
        if report_data.get('recommendations'):
            story.append(Paragraph("Recommended Next Steps", self.styles['SectionHeader']))
            for rec in report_data['recommendations']:
                story.append(Paragraph(f"• {rec}", self.styles['ReportBodyText']))
            story.append(Spacer(1, 12))
        
        # Disclaimer
        disclaimer_text = "This is an AI-assisted intake summary for provider review. Final diagnosis and treatment plan to be determined by licensed clinician."
        story.append(Paragraph(disclaimer_text, self.styles['Disclaimer']))
        story.append(Spacer(1, 12))
        
        # Footer
        footer_text = f"Generated by PsychNow on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}"
        story.append(Paragraph(footer_text, self.styles['Disclaimer']))
        
        # Build PDF
        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()
    
    def generate_patient_report_base64(self, report_data: Dict[str, Any], patient_name: str = "Patient") -> str:
        """Generate a PATIENT-FRIENDLY PDF report and return as base64"""
        pdf_bytes = self.generate_patient_report_pdf(report_data, patient_name)
        return base64.b64encode(pdf_bytes).decode('utf-8')
    
    def generate_clinician_report_pdf(self, report_data: Dict[str, Any], patient_name: str = "Patient") -> bytes:
        """Generate a CONCISE CLINICIAN-FOCUSED PDF report (2 pages max)"""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=72, leftMargin=72, 
                              topMargin=72, bottomMargin=18)
        
        story = []
        
        # Title - SIMPLIFIED CLINICIAN VERSION
        story.append(Paragraph("PSYCHNOW CLINICAL ASSESSMENT", self.styles['ReportTitle']))
        story.append(Paragraph("<font size='10' color='red'><b>CONFIDENTIAL - FOR PROVIDER USE ONLY</b></font>", self.styles['Disclaimer']))
        story.append(Spacer(1, 20))
        
        # Header information - Simplified Clinical Version
        header_data = [
            ['Patient ID:', report_data.get('patient_id', 'N/A')],
            ['Patient Name:', patient_name],
            ['Assessment Date:', self._format_date(report_data.get('date'))],
            ['Risk Level:', report_data.get('risk_level', 'N/A').upper()],
            ['Urgency:', report_data.get('urgency', 'N/A').upper()]
        ]
        
        header_table = Table(header_data, colWidths=[1.5*inch, 4*inch])
        header_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#1e40af')),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.white),
            ('TEXTCOLOR', (1, 0), (1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('BACKGROUND', (1, 0), (1, -1), colors.HexColor('#f0f0f0')),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#d0d0d0'))
        ]))
        
        story.append(header_table)
        story.append(Spacer(1, 20))
        
        # Add helper function for sections
        def add_section(title: str, content: Any, is_list: bool = False):
            """Helper to add a section to the report"""
            story.append(Paragraph(title.upper(), self.styles['SectionHeader']))
            
            if content:
                if is_list and isinstance(content, list):
                    for item in content:
                        story.append(Paragraph(f"• {item}", self.styles['ReportBodyText']))
                elif isinstance(content, dict):
                    # Handle nested dict structure
                    story.append(Paragraph(str(content), self.styles['ReportBodyText']))
                else:
                    story.append(Paragraph(str(content), self.styles['ReportBodyText']))
            else:
                story.append(Paragraph("<i>Not assessed</i>", self.styles['ReportBodyText']))
            
            story.append(Spacer(1, 12))
        
        # 1. 🚨 CLINICAL ACTION DASHBOARD
        dashboard = report_data.get('clinical_action_dashboard', {})
        if dashboard:
            story.append(Paragraph("🚨 CLINICAL ACTION DASHBOARD", self.styles['SectionHeader']))
            
            # Immediate Actions
            if dashboard.get('immediate_actions'):
                story.append(Paragraph("<b>Immediate Actions:</b>", self.styles['ReportBodyText']))
                for action in dashboard['immediate_actions']:
                    story.append(Paragraph(f"• {action}", self.styles['ReportBodyText']))
            
            # Treatment Plan
            if dashboard.get('treatment_plan'):
                story.append(Paragraph(f"<b>Treatment Plan:</b> {dashboard['treatment_plan']}", self.styles['ReportBodyText']))
            
            # Safety Concerns
            if dashboard.get('safety_concerns'):
                story.append(Paragraph(f"<b>Safety Concerns:</b> {dashboard['safety_concerns']}", self.styles['ReportBodyText']))
            
            # Follow-up Timeline
            if dashboard.get('follow_up_timeline'):
                story.append(Paragraph(f"<b>Follow-up:</b> {dashboard['follow_up_timeline']}", self.styles['ReportBodyText']))
            
            story.append(Spacer(1, 12))
        
        # 2. 📋 CHIEF COMPLAINT & KEY SYMPTOMS
        add_section("📋 CHIEF COMPLAINT & KEY SYMPTOMS", report_data.get('chief_complaint'))
        if report_data.get('key_symptoms'):
            add_section("Key Symptoms", report_data['key_symptoms'])
        
        # 3. 🎯 DIAGNOSIS & SEVERITY
        diagnosis = report_data.get('diagnosis_severity', {})
        if diagnosis:
            story.append(Paragraph("🎯 DIAGNOSIS & SEVERITY", self.styles['SectionHeader']))
            if diagnosis.get('primary_diagnosis'):
                story.append(Paragraph(f"<b>Primary:</b> {diagnosis['primary_diagnosis']}", self.styles['ReportBodyText']))
            if diagnosis.get('comorbid_diagnoses'):
                story.append(Paragraph(f"<b>Comorbid:</b> {', '.join(diagnosis['comorbid_diagnoses'])}", self.styles['ReportBodyText']))
            if diagnosis.get('rule_out'):
                story.append(Paragraph(f"<b>Rule Out:</b> {', '.join(diagnosis['rule_out'])}", self.styles['ReportBodyText']))
            if diagnosis.get('functional_impairment'):
                story.append(Paragraph(f"<b>Functional Impact:</b> {diagnosis['functional_impairment']}", self.styles['ReportBodyText']))
            story.append(Spacer(1, 12))
        
        # 4. 💊 TREATMENT RECOMMENDATIONS
        treatment = report_data.get('treatment_recommendations', {})
        if treatment:
            story.append(Paragraph("💊 TREATMENT RECOMMENDATIONS", self.styles['SectionHeader']))
            if treatment.get('pharmacotherapy'):
                story.append(Paragraph(f"<b>Pharmacotherapy:</b> {treatment['pharmacotherapy']}", self.styles['ReportBodyText']))
            if treatment.get('psychotherapy'):
                story.append(Paragraph(f"<b>Psychotherapy:</b> {treatment['psychotherapy']}", self.styles['ReportBodyText']))
            if treatment.get('additional'):
                story.append(Paragraph(f"<b>Additional:</b> {treatment['additional']}", self.styles['ReportBodyText']))
            if treatment.get('follow_up'):
                story.append(Paragraph(f"<b>Follow-up:</b> {treatment['follow_up']}", self.styles['ReportBodyText']))
            story.append(Spacer(1, 12))
        
        # 5. 📊 SCREENER RESULTS (Table)
        screeners = report_data.get('screener_results', [])
        if screeners:
            story.append(Paragraph("📊 SCREENER RESULTS", self.styles['SectionHeader']))
            
            # Create table for screener results
            screener_data = [['Screener', 'Score', 'Interpretation', 'Clinical Significance']]
            for screener in screeners:
                screener_data.append([
                    screener.get('name', 'N/A'),
                    f"{screener.get('score', 'N/A')}/{screener.get('max_score', 'N/A')}",
                    screener.get('interpretation', 'N/A'),
                    screener.get('clinical_significance', 'N/A')
                ])
            
            screener_table = Table(screener_data, colWidths=[1.5*inch, 1*inch, 2*inch, 1.5*inch])
            screener_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e40af')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8f9fa')),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#dee2e6'))
            ]))
            
            story.append(screener_table)
            story.append(Spacer(1, 12))
        
        # 6. ⚠️ SAFETY ASSESSMENT (if concerns)
        safety = report_data.get('safety_assessment')
        if safety and safety != "No safety concerns identified":
            add_section("⚠️ SAFETY ASSESSMENT", safety)
        
        # 7. 📝 BRIEF HISTORY
        history = report_data.get('brief_history', {})
        if history:
            story.append(Paragraph("📝 BRIEF HISTORY", self.styles['SectionHeader']))
            
            if history.get('psychiatric_history'):
                story.append(Paragraph(f"<b>Psychiatric History:</b> {history['psychiatric_history']}", self.styles['ReportBodyText']))
            
            if history.get('medical_history'):
                story.append(Paragraph(f"<b>Medical History:</b> {history['medical_history']}", self.styles['ReportBodyText']))
            
            if history.get('substance_use'):
                story.append(Paragraph(f"<b>Substance Use:</b> {history['substance_use']}", self.styles['ReportBodyText']))
            
            if history.get('trauma_history'):
                story.append(Paragraph(f"<b>Trauma History:</b> {history['trauma_history']}", self.styles['ReportBodyText']))
            
            story.append(Spacer(1, 12))
        
        # Build PDF
        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()
    
    def generate_clinician_report_base64(self, report_data: Dict[str, Any], patient_name: str = "Patient") -> str:
        """Generate a CLINICIAN-FOCUSED PDF report and return as base64"""
        pdf_bytes = self.generate_clinician_report_pdf(report_data, patient_name)
        return base64.b64encode(pdf_bytes).decode('utf-8')
    
    def _get_patient_friendly_urgency(self, urgency: str) -> str:
        """Convert clinical urgency to patient-friendly language"""
        urgency_map = {
            'routine': 'Standard Care',
            'urgent': 'Priority Care',
            'emergent': 'Immediate Care'
        }
        return urgency_map.get(urgency, 'Standard Care')


# Global instance
pdf_service = PDFReportService()
