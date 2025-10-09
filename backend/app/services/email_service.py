"""
Email Service
Handles all email notifications for demo system
"""
import smtplib
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from typing import Optional, List
import base64
from datetime import datetime

from app.core.config import settings
import json
import httpx

logger = logging.getLogger(__name__)


class EmailService:
    """Service for sending demo-related emails"""
    
    def __init__(self):
        self.smtp_host = settings.SMTP_HOST
        self.smtp_port = settings.SMTP_PORT
        self.smtp_user = settings.SMTP_USER
        self.smtp_password = settings.SMTP_PASSWORD
        self.admin_email = settings.ADMIN_EMAIL
        self.from_email = settings.FROM_EMAIL
        self.from_name = "PsychNow Demo"
    
    def send_email(
        self,
        to_email: str,
        subject: str,
        html_body: str,
        attachments: Optional[List[dict]] = None
    ) -> bool:
        """
        Send email with optional attachments
        
        Args:
            to_email: Recipient email
            subject: Email subject
            html_body: HTML email body
            attachments: List of dicts with 'filename' and 'content' (base64 or bytes)
        
        Returns:
            True if sent successfully, False otherwise
        """
        # Prefer Resend HTTP API if configured
        if settings.RESEND_API_KEY:
            try:
                # Use Resend's default domain for unverified senders
                from_email = self.from_email if "@resend.dev" in self.from_email else "onboarding@resend.dev"
                resend_payload = {
                    "from": f"{self.from_name} <{from_email}>",
                    "to": [to_email],
                    "subject": subject,
                    "html": html_body,
                }
                
                # Attachments (optional)
                if attachments:
                    resend_attachments = []
                    for att in attachments:
                        filename = att.get('filename', 'attachment.pdf')
                        content = att.get('content')
                        if isinstance(content, bytes):
                            b64_content = base64.b64encode(content).decode('utf-8')
                        else:
                            b64_content = content  # already base64
                        resend_attachments.append({
                            "content": b64_content,
                            "filename": filename,
                            "content_type": "application/pdf"
                        })
                    if resend_attachments:
                        resend_payload["attachments"] = resend_attachments
                
                headers = {
                    "Authorization": f"Bearer {settings.RESEND_API_KEY}",
                    "Content-Type": "application/json"
                }
                
                with httpx.Client(timeout=15) as client:
                    r = client.post("https://api.resend.com/emails", headers=headers, data=json.dumps(resend_payload))
                
                if 200 <= r.status_code < 300:
                    logger.info(f"✅ Resend email sent to {to_email}: {subject}")
                    return True
                else:
                    logger.error(f"❌ Resend failed: {r.status_code} {r.text}")
                    # Fall through to SMTP
            except Exception as e:
                logger.error(f"❌ Resend exception: {str(e)}")
                # Fall through to SMTP

        # SMTP fallback
        try:
            msg = MIMEMultipart()
            msg['From'] = f"{self.from_name} <{self.from_email}>"
            msg['To'] = to_email
            msg['Subject'] = subject
            msg.attach(MIMEText(html_body, 'html'))
            if attachments:
                for attachment in attachments:
                    self._attach_file(msg, attachment)
            if self.smtp_user and self.smtp_password:
                with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                    server.starttls()
                    server.login(self.smtp_user, self.smtp_password)
                    server.send_message(msg)
                logger.info(f"✅ Email sent successfully to {to_email}: {subject}")
                return True
            else:
                logger.warning("⚠️ SMTP credentials not configured - email not sent (logged only)")
                logger.info(f"📧 Would send to {to_email}: {subject}")
                return False
        except Exception as e:
            logger.error(f"❌ Failed to send email: {str(e)}")
            return False
    
    def _attach_file(self, msg: MIMEMultipart, attachment: dict):
        """Attach file to email message"""
        try:
            filename = attachment.get('filename', 'attachment.pdf')
            content = attachment.get('content')
            
            # Handle base64 content
            if isinstance(content, str):
                content = base64.b64decode(content)
            
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(content)
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', f'attachment; filename={filename}')
            msg.attach(part)
            
            logger.info(f"📎 Attached file: {filename}")
            
        except Exception as e:
            logger.error(f"❌ Failed to attach file {filename}: {str(e)}")
    
    def send_assessment_completion_email(
        self,
        session_id: str,
        patient_pdf_base64: str,
        clinician_pdf_base64: str,
        duration_minutes: Optional[int] = None
    ) -> bool:
        """Send email when assessment is completed"""
        
        subject = f"✅ New Demo Assessment Completed - Session {session_id[:8]}"
        
        html_body = f"""
        <html>
        <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif; line-height: 1.6; color: #1f2937; background-color: #f9fafb; padding: 20px;">
            <div style="max-width: 600px; margin: 0 auto; background: white; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); overflow: hidden;">
                <!-- Header -->
                <div style="background: linear-gradient(135deg, #2563eb 0%, #4f46e5 100%); color: white; padding: 30px 20px; text-align: center;">
                    <h1 style="margin: 0; font-size: 24px; font-weight: 600;">✅ Demo Assessment Completed</h1>
                    <p style="margin: 10px 0 0 0; opacity: 0.95; font-size: 14px;">PsychNow Clinical Validation</p>
                </div>
                
                <!-- Body -->
                <div style="padding: 30px 20px;">
                    <div style="background: #f3f4f6; padding: 20px; border-radius: 8px; margin-bottom: 25px;">
                        <p style="margin: 0 0 12px 0;"><strong style="color: #374151;">Session ID:</strong> <code style="background: #e5e7eb; padding: 2px 8px; border-radius: 4px; font-family: monospace;">{session_id}</code></p>
                        <p style="margin: 0 0 12px 0;"><strong style="color: #374151;">Completed:</strong> {self._format_timestamp()}</p>
                        {f'<p style="margin: 0;"><strong style="color: #374151;">Duration:</strong> {duration_minutes} minutes</p>' if duration_minutes else ''}
                    </div>
                    
                    <h2 style="color: #1f2937; font-size: 18px; margin: 25px 0 15px 0; border-bottom: 2px solid #e5e7eb; padding-bottom: 8px;">📎 Attached Reports</h2>
                    <ul style="list-style: none; padding: 0; margin: 0 0 25px 0;">
                        <li style="background: #dbeafe; padding: 12px 15px; border-radius: 6px; margin-bottom: 10px; border-left: 4px solid #2563eb;">
                            <strong style="color: #1e40af;">📋 patient-report-{session_id[:8]}.pdf</strong>
                            <p style="margin: 5px 0 0 0; font-size: 14px; color: #1e40af;">Patient-facing version (compassionate, accessible language)</p>
                        </li>
                        <li style="background: #ede9fe; padding: 12px 15px; border-radius: 6px; border-left: 4px solid #4f46e5;">
                            <strong style="color: #5b21b6;">🩺 clinician-report-{session_id[:8]}.pdf</strong>
                            <p style="margin: 5px 0 0 0; font-size: 14px; color: #5b21b6;">Clinical version (diagnostic reasoning, treatment recs)</p>
                        </li>
                    </ul>
                    
                    <div style="background: #fef3c7; border-left: 4px solid #f59e0b; padding: 15px; border-radius: 6px; margin-bottom: 25px;">
                        <p style="margin: 0; color: #92400e;"><strong>⏳ Feedback Status:</strong> Pending</p>
                        <p style="margin: 8px 0 0 0; font-size: 14px; color: #92400e;">
                            You'll receive another email when the clinician submits their feedback.
                        </p>
                    </div>
                    
                    <div style="background: #f0fdf4; border: 2px solid #86efac; padding: 15px; border-radius: 6px;">
                        <p style="margin: 0; color: #166534; font-size: 14px;">
                            <strong>💡 Next Step:</strong> Review both PDFs to see the difference between patient-facing and clinician-focused reports.
                        </p>
                    </div>
                </div>
                
                <!-- Footer -->
                <div style="background: #f9fafb; padding: 20px; text-align: center; border-top: 1px solid #e5e7eb;">
                    <p style="margin: 0; font-size: 12px; color: #6b7280;">
                        PsychNow Demo System<br>
                        Automated notification · Do not reply to this email
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
        
        attachments = [
            {
                'filename': f'patient-report-{session_id[:8]}.pdf',
                'content': patient_pdf_base64
            },
            {
                'filename': f'clinician-report-{session_id[:8]}.pdf',
                'content': clinician_pdf_base64
            }
        ]
        
        return self.send_email(self.admin_email, subject, html_body, attachments)
    
    def send_feedback_submission_email(self, feedback_data: dict) -> bool:
        """Send email when feedback is submitted"""
        
        session_id = feedback_data.get('session_id', 'Unknown')
        ratings = feedback_data.get('ratings', {})
        
        subject = f"💬 Demo Feedback Received - Session {session_id[:8]}"
        
        # Star rating display
        def stars(rating):
            return '⭐' * rating + '☆' * (5 - rating)
        
        html_body = f"""
        <html>
        <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif; line-height: 1.6; color: #1f2937; background-color: #f9fafb; padding: 20px;">
            <div style="max-width: 600px; margin: 0 auto; background: white; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); overflow: hidden;">
                <!-- Header -->
                <div style="background: linear-gradient(135deg, #10b981 0%, #059669 100%); color: white; padding: 30px 20px; text-align: center;">
                    <h1 style="margin: 0; font-size: 24px; font-weight: 600;">💬 Feedback Received!</h1>
                    <p style="margin: 10px 0 0 0; opacity: 0.95; font-size: 14px;">A clinician has submitted their assessment feedback</p>
                </div>
                
                <!-- Body -->
                <div style="padding: 30px 20px;">
                    <div style="background: #f3f4f6; padding: 20px; border-radius: 8px; margin-bottom: 25px;">
                        <p style="margin: 0 0 12px 0;"><strong style="color: #374151;">Session ID:</strong> <code style="background: #e5e7eb; padding: 2px 8px; border-radius: 4px; font-family: monospace;">{session_id}</code></p>
                        <p style="margin: 0 0 12px 0;"><strong style="color: #374151;">Submitted:</strong> {self._format_timestamp()}</p>
                        {f"<p style='margin: 0 0 12px 0;'><strong style='color: #374151;'>Tester:</strong> {feedback_data.get('tester', {}).get('name', 'Anonymous')}</p>" if feedback_data.get('tester', {}).get('name') else ''}
                        {f"<p style='margin: 0;'><strong style='color: #374151;'>Email:</strong> {feedback_data.get('tester', {}).get('email', 'Not provided')}</p>" if feedback_data.get('tester', {}).get('email') else ''}
                    </div>
                    
                    <h2 style="color: #1f2937; font-size: 18px; margin: 25px 0 15px 0; border-bottom: 2px solid #e5e7eb; padding-bottom: 8px;">⭐ Ratings</h2>
                    <div style="background: #f9fafb; border: 1px solid #e5e7eb; padding: 20px; border-radius: 8px; margin-bottom: 25px;">
                        <p style="margin: 0 0 15px 0; font-size: 16px;">
                            <strong style="color: #374151;">Conversation Flow:</strong><br>
                            <span style="font-size: 20px;">{stars(ratings.get('conversation', 0))}</span> <strong style="color: #2563eb;">({ratings.get('conversation', 0)}/5)</strong>
                        </p>
                        <p style="margin: 0 0 15px 0; font-size: 16px;">
                            <strong style="color: #374151;">Patient Report:</strong><br>
                            <span style="font-size: 20px;">{stars(ratings.get('patient_report', 0))}</span> <strong style="color: #2563eb;">({ratings.get('patient_report', 0)}/5)</strong>
                        </p>
                        <p style="margin: 0; font-size: 16px;">
                            <strong style="color: #374151;">Clinician Report:</strong><br>
                            <span style="font-size: 20px;">{stars(ratings.get('clinician_report', 0))}</span> <strong style="color: #2563eb;">({ratings.get('clinician_report', 0)}/5)</strong>
                        </p>
                    </div>
                    
                    <h2 style="color: #1f2937; font-size: 18px; margin: 25px 0 15px 0; border-bottom: 2px solid #e5e7eb; padding-bottom: 8px;">🏥 Would Use in Practice</h2>
                    <div style="background: #dbeafe; padding: 20px; border-radius: 8px; text-align: center; margin-bottom: 25px;">
                        <p style="margin: 0; font-size: 22px; font-weight: 600; color: #1e40af;">
                            {self._format_would_use(feedback_data.get('would_use', ''))}
                        </p>
                    </div>
                    
                    <h2 style="color: #1f2937; font-size: 18px; margin: 25px 0 15px 0; border-bottom: 2px solid #e5e7eb; padding-bottom: 8px;">💭 Qualitative Feedback</h2>
                    
                    {self._format_feedback_section('💪 Biggest Strength', feedback_data.get('feedback', {}).get('strength'), '#10b981', '#d1fae5')}
                    {self._format_feedback_section('⚠️ Biggest Concern', feedback_data.get('feedback', {}).get('concern'), '#ef4444', '#fee2e2')}
                    {self._format_feedback_section('📋 Missing from Patient Report', feedback_data.get('feedback', {}).get('missing_patient'), '#f59e0b', '#fef3c7')}
                    {self._format_feedback_section('🩺 Missing from Clinician Report', feedback_data.get('feedback', {}).get('missing_clinician'), '#f59e0b', '#fef3c7')}
                    {self._format_feedback_section('💡 Additional Comments', feedback_data.get('feedback', {}).get('additional_comments'), '#6366f1', '#e0e7ff')}
                </div>
                
                <!-- Footer -->
                <div style="background: #f9fafb; padding: 20px; text-align: center; border-top: 1px solid #e5e7eb;">
                    <p style="margin: 0; font-size: 12px; color: #6b7280;">
                        PsychNow Demo System<br>
                        Automated notification · Do not reply to this email
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return self.send_email(self.admin_email, subject, html_body)
    
    def _format_would_use(self, value: str) -> str:
        """Format would_use value for display"""
        mapping = {
            'yes_definitely': '✅ Yes, definitely',
            'yes_probably': '👍 Yes, probably',
            'maybe': '🤔 Maybe, with changes',
            'probably_not': '👎 Probably not',
            'no': '❌ No'
        }
        return mapping.get(value, value)
    
    def _format_feedback_section(self, title: str, content: Optional[str], border_color: str, bg_color: str) -> str:
        """Format a feedback section"""
        if not content or content.strip() == '':
            return ''
        
        # Escape HTML special characters
        content = content.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        
        return f"""
        <div style="margin: 0 0 20px 0;">
            <h3 style="color: {border_color}; margin: 0 0 10px 0; font-size: 16px;">{title}</h3>
            <div style="background: {bg_color}; border-left: 4px solid {border_color}; padding: 15px; border-radius: 6px;">
                <p style="margin: 0; white-space: pre-wrap; color: #374151;">{content}</p>
            </div>
        </div>
        """
    
    def _format_timestamp(self) -> str:
        """Format current timestamp"""
        return datetime.now().strftime("%B %d, %Y at %I:%M %p")


# Singleton instance
email_service = EmailService()

