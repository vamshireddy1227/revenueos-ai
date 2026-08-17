import random
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.models import Ticket, TicketEvent, User, Customer
from app.schemas.schemas import TicketCreate, TicketResponse
from app.auth.deps import get_current_user
from app.services.ai_provider import ai_provider
from app.services.audit_service import audit_service
from app.services.workflow_engine import workflow_engine

router = APIRouter(prefix="/tickets", tags=["AI Support - Tickets"])

@router.get("", response_model=List[TicketResponse])
def list_tickets(
    status_filter: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(Ticket).filter(Ticket.organization_id == current_user.organization_id)
    if status_filter:
        query = query.filter(Ticket.status == status_filter)
    tickets = query.order_by(Ticket.created_at.desc()).all()
    return [TicketResponse.model_validate(t) for t in tickets]

@router.post("", response_model=TicketResponse, status_code=status.HTTP_201_CREATED)
def create_ticket(
    req: TicketCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    customer = db.query(Customer).filter(Customer.id == req.customer_id, Customer.organization_id == current_user.organization_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail={"error": {"code": "NOT_FOUND", "message": "Customer not found."}})
    
    # AI Automatic Classification (Intent, Sentiment, Urgency, Priority)
    classified = ai_provider.classify_ticket(req.subject, req.description)
    
    code = f"TICK-{random.randint(10000, 99999)}"
    ticket = Ticket(
        ticket_code=code,
        organization_id=current_user.organization_id,
        customer_id=customer.id,
        assigned_agent_id=current_user.id,
        subject=req.subject,
        description=req.description,
        category=req.category or "General",
        intent=classified["intent"],
        sentiment=classified["sentiment"],
        urgency=classified["urgency"],
        priority=classified["priority"],
        status="Open"
    )
    db.add(ticket)
    db.flush()

    event = TicketEvent(
        ticket_id=ticket.id,
        user_id=current_user.id,
        event_type="ticket_created",
        message=f"Ticket created and classified by AI: Intent={classified['intent']}, Sentiment={classified['sentiment']}, Priority={classified['priority']}."
    )
    db.add(event)
    db.commit()
    db.refresh(ticket)

    audit_service.log(db, current_user.organization_id, "TICKET_CREATED", "Ticket", current_user.id, current_user.email, ticket.id, {"code": code, "intent": classified['intent']})
    workflow_engine.trigger_event(db, current_user.organization_id, "ticket_created", {"ticket_id": ticket.id, "user_id": current_user.id})

    return TicketResponse.model_validate(ticket)

@router.get("/{ticket_id}", response_model=TicketResponse)
def get_ticket(ticket_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id, Ticket.organization_id == current_user.organization_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail={"error": {"code": "NOT_FOUND", "message": "Ticket not found."}})
    return TicketResponse.model_validate(ticket)

@router.put("/{ticket_id}/status", response_model=TicketResponse)
def update_ticket_status(ticket_id: str, new_status: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id, Ticket.organization_id == current_user.organization_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail={"error": {"code": "NOT_FOUND", "message": "Ticket not found."}})
    
    old_status = ticket.status
    ticket.status = new_status
    
    event = TicketEvent(
        ticket_id=ticket.id,
        user_id=current_user.id,
        event_type="status_change",
        message=f"Ticket status changed from '{old_status}' to '{new_status}' by {current_user.full_name}."
    )
    db.add(event)
    db.commit()
    return TicketResponse.model_validate(ticket)
