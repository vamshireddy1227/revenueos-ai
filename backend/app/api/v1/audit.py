from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.models import AuditLog, User
from app.schemas.schemas import AuditLogResponse
from app.auth.deps import get_current_user, RequireRole

router = APIRouter(prefix="/audit-logs", tags=["Audit & Security Logs"])

@router.get("", response_model=List[AuditLogResponse])
def list_audit_logs(
    current_user: User = Depends(RequireRole(["Organization Owner", "Admin", "Executive"])),
    db: Session = Depends(get_db)
):
    logs = db.query(AuditLog).filter(AuditLog.organization_id == current_user.organization_id).order_by(AuditLog.created_at.desc()).limit(100).all()
    return [AuditLogResponse.model_validate(l) for l in logs]
