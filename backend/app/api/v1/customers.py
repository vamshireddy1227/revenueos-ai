from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.models import Customer, User, Ticket
from app.schemas.schemas import CustomerResponse
from app.auth.deps import get_current_user
from app.services.ml_engine import ml_engine

router = APIRouter(prefix="/customers", tags=["Customer Intelligence & 360"])

@router.get("", response_model=List[CustomerResponse])
def list_customers(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    customers = db.query(Customer).filter(Customer.organization_id == current_user.organization_id).order_by(Customer.created_at.desc()).all()
    return [CustomerResponse.model_validate(c) for c in customers]

@router.get("/{customer_id}", response_model=CustomerResponse)
def get_customer(customer_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    customer = db.query(Customer).filter(Customer.id == customer_id, Customer.organization_id == current_user.organization_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail={"error": {"code": "NOT_FOUND", "message": "Customer not found."}})
    return CustomerResponse.model_validate(customer)

@router.get("/{customer_id}/360", response_model=Dict[str, Any])
def get_customer_360(customer_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    customer = db.query(Customer).filter(Customer.id == customer_id, Customer.organization_id == current_user.organization_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail={"error": {"code": "NOT_FOUND", "message": "Customer not found."}})
    
    tickets = db.query(Ticket).filter(Ticket.customer_id == customer.id).all()
    
    # Recalculate health and upsell dynamically
    health = ml_engine.calculate_customer_health(
        mrr=customer.mrr,
        ticket_count=len(tickets),
        negative_sentiment_count=sum(1 for t in tickets if t.sentiment in ["Negative", "Angry"]),
        days_since_last_activity=5
    )
    upsell = ml_engine.calculate_upsell_opportunity(customer.mrr, health["health_score"], customer.subscription_plan)

    return {
        "profile": {
            "id": customer.id,
            "name": customer.name,
            "email": customer.email,
            "phone": customer.phone,
            "industry": customer.industry,
            "region": customer.region
        },
        "commercial": {
            "subscription_plan": customer.subscription_plan,
            "mrr": customer.mrr,
            "arr": customer.arr
        },
        "intelligence": {
            "health_score": health["health_score"],
            "health_status": health["health_status"],
            "churn_risk_score": health["churn_risk_score"],
            "churn_risk_level": health["churn_risk_level"],
            "risk_factors": health["risk_factors"],
            "upsell_opportunity": upsell
        },
        "support_summary": {
            "total_tickets": len(tickets),
            "open_tickets": sum(1 for t in tickets if t.status in ["Open", "In Progress", "Escalated"]),
            "recent_tickets": [
                {
                    "id": t.id,
                    "code": t.ticket_code,
                    "subject": t.subject,
                    "status": t.status,
                    "priority": t.priority,
                    "sentiment": t.sentiment
                } for t in tickets[:5]
            ]
        }
    }
