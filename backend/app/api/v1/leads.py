from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.models import Lead, User
from app.schemas.schemas import LeadCreate, LeadResponse
from app.auth.deps import get_current_user
from app.services.ml_engine import ml_engine
from app.services.ai_provider import ai_provider
from app.services.audit_service import audit_service
from app.services.workflow_engine import workflow_engine

router = APIRouter(prefix="/leads", tags=["Sales - Leads"])

@router.get("", response_model=List[LeadResponse])
def list_leads(
    status_filter: Optional[str] = Query(None, alias="status"),
    search: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(Lead).filter(Lead.organization_id == current_user.organization_id)
    if status_filter:
        query = query.filter(Lead.status == status_filter)
    if search:
        query = query.filter(
            (Lead.name.ilike(f"%{search}%")) | 
            (Lead.email.ilike(f"%{search}%")) |
            (Lead.company_name.ilike(f"%{search}%"))
        )
    leads = query.order_by(Lead.created_at.desc()).all()
    return [LeadResponse.model_validate(l) for l in leads]

@router.post("", response_model=LeadResponse, status_code=status.HTTP_201_CREATED)
def create_lead(
    req: LeadCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Calculate ML Lead Score automatically
    ml_result = ml_engine.calculate_lead_score(
        company_size=req.company_size or "51-200",
        industry=req.industry or "Technology",
        source=req.source or "Website",
        deal_value=req.deal_value or 10000.0,
        activity_count=1
    )

    rec_action = ai_provider.generate_sales_recommendation(
        score=ml_result["score"],
        deal_value=req.deal_value or 10000.0,
        industry=req.industry or "Technology",
        factors=ml_result["factors"]
    )

    lead = Lead(
        organization_id=current_user.organization_id,
        owner_id=current_user.id,
        name=req.name,
        email=req.email,
        phone=req.phone,
        company_name=req.company_name,
        industry=req.industry,
        company_size=req.company_size,
        source=req.source,
        status="New",
        deal_value=req.deal_value,
        score=ml_result["score"],
        conversion_prob=ml_result["conversion_prob"],
        risk_level=ml_result["risk_level"],
        score_factors=ml_result["factors"],
        recommended_action=rec_action,
        tags=req.tags or []
    )
    db.add(lead)
    db.commit()
    db.refresh(lead)

    audit_service.log(db, current_user.organization_id, "LEAD_CREATED", "Lead", current_user.id, current_user.email, lead.id, {"lead_name": lead.name, "score": lead.score})
    workflow_engine.trigger_event(db, current_user.organization_id, "lead_created", {"lead_id": lead.id, "user_id": current_user.id})

    return LeadResponse.model_validate(lead)

@router.get("/{lead_id}", response_model=LeadResponse)
def get_lead(lead_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    lead = db.query(Lead).filter(Lead.id == lead_id, Lead.organization_id == current_user.organization_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail={"error": {"code": "NOT_FOUND", "message": "Lead not found."}})
    return LeadResponse.model_validate(lead)

@router.post("/{lead_id}/rescore", response_model=LeadResponse)
def rescore_lead(lead_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    lead = db.query(Lead).filter(Lead.id == lead_id, Lead.organization_id == current_user.organization_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail={"error": {"code": "NOT_FOUND", "message": "Lead not found."}})
    
    ml_result = ml_engine.calculate_lead_score(
        company_size=lead.company_size or "51-200",
        industry=lead.industry or "Technology",
        source=lead.source or "Website",
        deal_value=lead.deal_value or 10000.0,
        activity_count=3
    )

    lead.score = ml_result["score"]
    lead.conversion_prob = ml_result["conversion_prob"]
    lead.risk_level = ml_result["risk_level"]
    lead.score_factors = ml_result["factors"]
    lead.recommended_action = ml_result["recommended_action"]
    db.commit()

    return LeadResponse.model_validate(lead)
