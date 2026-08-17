from typing import Dict, Any
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.database import get_db
from app.models.models import User, Lead, Deal, Customer, Ticket
from app.schemas.schemas import CopilotQueryInput, CopilotQueryOutput, ExecutiveInsightsOutput
from app.auth.deps import get_current_user, RequireRole
from app.services.ai_provider import ai_provider

router = APIRouter(prefix="/ai", tags=["AI Copilot & Executive Intelligence"])

EXECUTIVE_ROLES = ["Organization Owner", "Admin", "Executive"]

@router.get("/status", tags=["Observability"])
def get_ai_status(current_user: User = Depends(RequireRole(["Organization Owner", "Admin", "Executive"]))):
    """
    Administrative Endpoint: Reports operational AI provider health and active mode.
    Never exposes secret API keys.
    """
    has_key = bool(settings.AI_API_KEY)
    active_mode = "PRODUCTION" if has_key and settings.AI_PROVIDER != "mock" else "LOCAL_DEMO"
    
    return {
        "ai_provider": settings.AI_PROVIDER,
        "ai_model": settings.AI_MODEL,
        "active_mode": active_mode,
        "embedding_provider": "postgresql_pgvector" if not settings.DATABASE_URL.startswith("sqlite") else "numpy_local_vector",
        "has_api_key_configured": has_key,
        "environment": settings.ENVIRONMENT
    }

@router.post("/copilot", response_model=CopilotQueryOutput)
def query_global_copilot(
    req: CopilotQueryInput,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    prompt_lower = req.prompt.lower()
    org_id = current_user.organization_id

    # Security RBAC Check: Enforce role restrictions on financial & billing natural language queries
    is_asking_billing = any(kw in prompt_lower for kw in ["billing", "mrr", "arr", "subscription price", "payment gateway", "audit log"])
    if is_asking_billing and current_user.role not in EXECUTIVE_ROLES:
        return CopilotQueryOutput(
            answer=f"Access Restricted: Your assigned role ('{current_user.role}') is not authorized to access organization billing or executive financial analytics. Please contact an Organization Owner or Executive.",
            suggested_actions=["View Assigned Leads", "Open Support Queue"],
            context_used={"security_block": True, "required_roles": EXECUTIVE_ROLES}
        )

    # Retrieve live context for tenant (Strictly scoped to org_id)
    leads_count = db.query(Lead).filter(Lead.organization_id == org_id).count()
    deals = db.query(Deal).filter(Deal.organization_id == org_id).all()
    customers = db.query(Customer).filter(Customer.organization_id == org_id).all()
    tickets = db.query(Ticket).filter(Ticket.organization_id == org_id).all()

    pipeline_val = sum(d.value for d in deals if d.stage not in ["Won", "Lost"])
    high_risk_deals = [d for d in deals if d.risk_level in ["Medium", "High"] and d.stage not in ["Won", "Lost"]]
    high_churn_customers = [c for c in customers if c.health_status in ["At Risk", "Critical"]]

    if "lead" in prompt_lower or "contact" in prompt_lower:
        high_score_leads = db.query(Lead).filter(Lead.organization_id == org_id, Lead.score >= 70).all()
        lead_names = ", ".join([l.name for l in high_score_leads[:3]]) or "None currently"
        answer = (
            f"You currently have {leads_count} total leads in your organization. "
            f"There are {len(high_score_leads)} high-scoring leads ready for immediate follow-up: {lead_names}. "
            f"Recommended focus: Contact high-score leads within 2 hours to maintain momentum."
        )
        actions = ["View High-Score Leads", "Schedule Sales Calls", "Export Lead List"]

    elif "risk" in prompt_lower or "deal" in prompt_lower or "close" in prompt_lower:
        deal_names = ", ".join([d.name for d in high_risk_deals[:3]]) or "No high-risk deals"
        answer = (
            f"Your active sales pipeline total is ${pipeline_val:,.2f}. "
            f"There are {len(high_risk_deals)} deals identified at elevated risk: {deal_names}. "
            f"Executive recommendation: Review contract terms and offer executive sponsor calls to secure closing."
        )
        actions = ["Review At-Risk Deals", "Generate Proposal Summary", "Email Account Owners"]

    elif "customer" in prompt_lower or "churn" in prompt_lower:
        churn_names = ", ".join([c.name for c in high_churn_customers[:3]]) or "None"
        answer = (
            f"You have {len(customers)} active customer accounts. "
            f"There are {len(high_churn_customers)} accounts flagged with elevated churn risk: {churn_names}. "
            f"Recommended intervention: Assign CS lead for health assessment call."
        )
        actions = ["Open Customer 360", "Schedule CS Intervention", "Review Support Tickets"]

    elif "support" in prompt_lower or "ticket" in prompt_lower:
        open_count = sum(1 for t in tickets if t.status in ["Open", "In Progress", "Escalated"])
        answer = (
            f"Support Desk Status: You have {open_count} open tickets out of {len(tickets)} total. "
            f"Sentiment breakdown: {sum(1 for t in tickets if t.sentiment in ['Negative', 'Angry'])} negative sentiment cases. "
            f"Recommended action: Prioritize critical billing and tech tickets first."
        )
        actions = ["Go to Support Desk", "Filter Urgent Tickets", "Trigger AI Agent"]

    else:
        answer = (
            f"Hello {current_user.full_name}! RevenueOS AI is monitoring your organization's operations. "
            f"Overview: ${pipeline_val:,.2f} in pipeline, {len(customers)} active customers, {len(tickets)} total tickets logged. "
            f"How can I assist you with sales, support, or customer intelligence today?"
        )
        actions = ["Show High-Score Leads", "Show Deals at Risk", "Executive Insights Summary"]

    return CopilotQueryOutput(
        answer=answer,
        suggested_actions=actions,
        context_used={
            "total_leads": leads_count,
            "pipeline_value": pipeline_val,
            "at_risk_deals": len(high_risk_deals),
            "at_risk_customers": len(high_churn_customers)
        }
    )

@router.get("/executive-insights", response_model=ExecutiveInsightsOutput)
def get_executive_insights(
    current_user: User = Depends(RequireRole(EXECUTIVE_ROLES)),
    db: Session = Depends(get_db)
):
    org_id = current_user.organization_id
    deals = db.query(Deal).filter(Deal.organization_id == org_id).all()
    customers = db.query(Customer).filter(Customer.organization_id == org_id).all()
    tickets = db.query(Ticket).filter(Ticket.organization_id == org_id).all()
    leads = db.query(Lead).filter(Lead.organization_id == org_id).all()

    mrr = sum(c.mrr for c in customers)
    arr = sum(c.arr for c in customers)
    pipeline_val = sum(d.value for d in deals if d.stage not in ["Won", "Lost"])
    weighted_val = sum(d.value * d.probability for d in deals if d.stage not in ["Won", "Lost"])
    avg_health = (sum(c.health_score for c in customers) / len(customers)) if customers else 80.0
    high_churn = sum(1 for c in customers if c.health_status in ["At Risk", "Critical"])
    open_tickets = sum(1 for t in tickets if t.status in ["Open", "In Progress", "Escalated"])
    won_count = sum(1 for d in deals if d.stage == "Won")
    conv_rate = (won_count / len(deals) * 100.0) if deals else 25.0

    metrics = {
        "mrr": mrr,
        "arr": arr,
        "total_pipeline_value": pipeline_val,
        "weighted_pipeline_value": weighted_val,
        "total_leads": len(leads),
        "total_customers": len(customers),
        "open_tickets": open_tickets,
        "avg_health_score": avg_health,
        "high_churn_risk_count": high_churn,
        "conversion_rate": round(conv_rate, 1)
    }

    insights = ai_provider.generate_executive_insights(metrics)
    return ExecutiveInsightsOutput(
        summary=insights["summary"],
        highlights=insights["highlights"],
        risks=insights["risks"],
        action_items=insights["action_items"]
    )
