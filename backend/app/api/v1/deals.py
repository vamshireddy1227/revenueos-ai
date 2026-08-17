from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.models import Deal, User
from app.schemas.schemas import DealCreate, DealResponse
from app.auth.deps import get_current_user
from app.services.audit_service import audit_service

router = APIRouter(prefix="/deals", tags=["Sales - Deals"])

STAGES = ["New Lead", "Qualified", "Discovery", "Proposal", "Negotiation", "Won", "Lost"]

@router.get("", response_model=List[DealResponse])
def list_deals(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    deals = db.query(Deal).filter(Deal.organization_id == current_user.organization_id).order_by(Deal.created_at.desc()).all()
    return [DealResponse.model_validate(d) for d in deals]

@router.post("", response_model=DealResponse, status_code=status.HTTP_201_CREATED)
def create_deal(req: DealCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # Calculate initial risk level & AI recommendation
    if req.stage == "Proposal" or req.stage == "Negotiation":
        risk = "Low" if req.value < 50000 else "Medium"
        rec = f"Focus negotiation on enterprise SLA support & volume discount for {req.name}."
    else:
        risk = "Low"
        rec = f"Conduct discovery call to clarify budget and timeline for {req.name}."

    deal = Deal(
        organization_id=current_user.organization_id,
        owner_id=current_user.id,
        company_id=req.company_id,
        contact_id=req.contact_id,
        name=req.name,
        value=req.value,
        probability=req.probability or 0.5,
        expected_close_date=req.expected_close_date,
        stage=req.stage,
        notes=req.notes,
        risk_level=risk,
        ai_recommendation=rec
    )
    db.add(deal)
    db.commit()
    db.refresh(deal)

    audit_service.log(db, current_user.organization_id, "DEAL_CREATED", "Deal", current_user.id, current_user.email, deal.id, {"deal_name": deal.name, "value": deal.value})
    return DealResponse.model_validate(deal)

@router.put("/{deal_id}", response_model=DealResponse)
def update_deal(deal_id: str, req: DealCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    deal = db.query(Deal).filter(Deal.id == deal_id, Deal.organization_id == current_user.organization_id).first()
    if not deal:
        raise HTTPException(status_code=404, detail={"error": {"code": "NOT_FOUND", "message": "Deal not found."}})
    
    deal.name = req.name
    deal.value = req.value
    deal.stage = req.stage
    deal.probability = req.probability or deal.probability
    if req.notes:
        deal.notes = req.notes
    
    db.commit()
    return DealResponse.model_validate(deal)

@router.get("/forecast/summary", response_model=Dict[str, Any])
def get_deal_forecast(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    deals = db.query(Deal).filter(Deal.organization_id == current_user.organization_id).all()
    
    total_pipeline = sum(d.value for d in deals if d.stage not in ["Won", "Lost"])
    weighted_pipeline = sum(d.value * d.probability for d in deals if d.stage not in ["Won", "Lost"])
    won_revenue = sum(d.value for d in deals if d.stage == "Won")
    lost_revenue = sum(d.value for d in deals if d.stage == "Lost")
    
    won_count = sum(1 for d in deals if d.stage == "Won")
    total_count = len(deals)
    conversion_rate = (won_count / total_count * 100.0) if total_count > 0 else 0.0
    avg_deal_size = (sum(d.value for d in deals) / total_count) if total_count > 0 else 0.0

    return {
        "total_pipeline_value": total_pipeline,
        "weighted_pipeline_value": weighted_pipeline,
        "won_revenue": won_revenue,
        "lost_revenue": lost_revenue,
        "conversion_rate": round(conversion_rate, 1),
        "avg_deal_size": round(avg_deal_size, 2),
        "active_deals_count": total_count - won_count - sum(1 for d in deals if d.stage == "Lost")
    }
