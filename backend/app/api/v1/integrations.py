from typing import List, Dict, Any
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.database import get_db
from app.models.models import User
from app.auth.deps import get_current_user

router = APIRouter(prefix="/integrations", tags=["Integration Center"])

@router.get("", response_model=List[Dict[str, Any]])
def list_integrations(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Returns Integration Center status matrix.
    Explicitly identifies whether each adapter is operating in MOCK, SANDBOX, or PRODUCTION mode.
    """
    stripe_mode = "PRODUCTION" if settings.STRIPE_SECRET_KEY else "SANDBOX_MOCK"
    sendgrid_mode = "PRODUCTION" if settings.SENDGRID_API_KEY else "SANDBOX_MOCK"

    return [
        {
            "provider": "hubspot",
            "name": "HubSpot CRM",
            "category": "CRM",
            "status": "connected",
            "mode": "SANDBOX_MOCK",
            "description": "Sync contacts, deals, and engagement timeline automatically."
        },
        {
            "provider": "salesforce",
            "name": "Salesforce Sales Cloud",
            "category": "CRM",
            "status": "connected",
            "mode": "SANDBOX_MOCK",
            "description": "Bi-directional opportunity & account sync."
        },
        {
            "provider": "sendgrid",
            "name": "SendGrid Email",
            "category": "Email",
            "status": "connected",
            "mode": sendgrid_mode,
            "description": "Automated transactional email dispatch & tracking."
        },
        {
            "provider": "slack",
            "name": "Slack Operations Bot",
            "category": "Messaging",
            "status": "connected",
            "mode": "SANDBOX_MOCK",
            "description": "Real-time deal alerts and high-risk customer notifications in Slack channels."
        },
        {
            "provider": "stripe",
            "name": "Stripe Billing Gateway",
            "category": "Payment Gateway",
            "status": "connected",
            "mode": stripe_mode,
            "description": "MRR, subscription tier, and invoice payment sync."
        }
    ]
