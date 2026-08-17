from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from app.models.models import AuditLog

class AuditService:
    @staticmethod
    def log(
        db: Session,
        organization_id: str,
        action: str,
        resource_type: str,
        user_id: Optional[str] = None,
        user_email: Optional[str] = None,
        resource_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        ip_address: str = "127.0.0.1"
    ):
        """Record compliance audit log entry."""
        audit_entry = AuditLog(
            organization_id=organization_id,
            user_id=user_id,
            user_email=user_email,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            details_json=details or {},
            ip_address=ip_address
        )
        db.add(audit_entry)
        db.commit()

audit_service = AuditService()
