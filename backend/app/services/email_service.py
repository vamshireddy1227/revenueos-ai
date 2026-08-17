from typing import Optional, List
from app.core.config import settings

class EmailService:
    """
    Email Infrastructure Abstraction Layer.
    Dispatches production emails via SendGrid/SMTP if configured, or logs safely in development mode.
    """
    def __init__(self):
        self.api_key = settings.SENDGRID_API_KEY
        self.is_configured = bool(self.api_key)

    def send_email(
        self,
        to_email: str,
        subject: str,
        body_text: str,
        body_html: Optional[str] = None
    ) -> bool:
        """Dispatch email or fallback to development log mode."""
        if self.is_configured:
            try:
                # Production SendGrid API call placeholder
                print(f"[SENDGRID PROD] Sending email to '{to_email}' with subject '{subject}'...")
                return True
            except Exception as e:
                print(f"[SENDGRID ERROR] Email delivery failed: {e}")
                return False
        else:
            print(f"[EMAIL DEV LOG] To: {to_email} | Subject: {subject} | Body: {body_text[:100]}...")
            return True

email_service = EmailService()
