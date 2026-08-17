from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.models import Workflow, WorkflowRun, User
from app.schemas.schemas import WorkflowCreate, WorkflowResponse
from app.auth.deps import get_current_user
from app.services.audit_service import audit_service

router = APIRouter(prefix="/workflows", tags=["Workflow Automation"])

@router.get("", response_model=List[WorkflowResponse])
def list_workflows(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    wfs = db.query(Workflow).filter(Workflow.organization_id == current_user.organization_id).all()
    return [WorkflowResponse.model_validate(w) for w in wfs]

@router.post("", response_model=WorkflowResponse, status_code=status.HTTP_201_CREATED)
def create_workflow(req: WorkflowCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    wf = Workflow(
        organization_id=current_user.organization_id,
        name=req.name,
        description=req.description,
        trigger_event=req.trigger_event,
        actions_json=req.actions_json,
        is_active=True
    )
    db.add(wf)
    db.commit()
    db.refresh(wf)

    audit_service.log(db, current_user.organization_id, "WORKFLOW_CREATED", "Workflow", current_user.id, current_user.email, wf.id, {"name": wf.name})
    return WorkflowResponse.model_validate(wf)
