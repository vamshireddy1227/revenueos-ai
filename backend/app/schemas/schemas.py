from datetime import datetime
from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional, Any, Dict

# Auth & User Schemas
class LoginRequest(BaseModel):
    email: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: "UserResponse"

class SignupRequest(BaseModel):
    org_name: str
    full_name: str
    email: str
    password: str
    plan: str = "Growth"


class UserResponse(BaseModel):
    id: str
    organization_id: str
    email: str
    full_name: str
    role: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

class OrganizationResponse(BaseModel):
    id: str
    name: str
    slug: str
    plan: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True

# Lead Schemas
class LeadCreate(BaseModel):
    name: str
    email: str
    phone: Optional[str] = None

    company_name: str
    industry: Optional[str] = "Technology"
    company_size: Optional[str] = "51-200"
    source: Optional[str] = "Website"
    deal_value: Optional[float] = 10000.0
    tags: Optional[List[str]] = []

class LeadResponse(BaseModel):
    id: str
    organization_id: str
    owner_id: Optional[str] = None
    name: str
    email: str
    phone: Optional[str] = None
    company_name: str
    industry: Optional[str] = None
    company_size: Optional[str] = None
    source: str
    status: str
    deal_value: float
    score: int
    conversion_prob: float
    risk_level: str
    score_factors: List[Any]
    recommended_action: Optional[str] = None
    tags: List[Any]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Deal Schemas
class DealCreate(BaseModel):
    name: str
    value: float
    stage: str = "New Lead"
    company_id: Optional[str] = None
    contact_id: Optional[str] = None
    expected_close_date: Optional[str] = None
    probability: Optional[float] = 0.5
    notes: Optional[str] = None

class DealResponse(BaseModel):
    id: str
    organization_id: str
    company_id: Optional[str] = None
    contact_id: Optional[str] = None
    owner_id: Optional[str] = None
    name: str
    value: float
    probability: float
    expected_close_date: Optional[str] = None
    stage: str
    notes: Optional[str] = None
    risk_level: str
    ai_recommendation: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Customer Schemas
class CustomerResponse(BaseModel):
    id: str
    organization_id: str
    company_id: Optional[str] = None
    name: str
    email: str
    phone: Optional[str] = None
    industry: Optional[str] = None
    region: Optional[str] = None
    subscription_plan: str
    mrr: float
    arr: float
    health_score: int
    health_status: str
    churn_risk_score: float
    churn_risk_factors: List[Any]
    upsell_opportunity: Dict[str, Any]
    created_at: datetime

    class Config:
        from_attributes = True

# Support Ticket Schemas
class TicketCreate(BaseModel):
    customer_id: str
    subject: str
    description: str
    category: Optional[str] = "General"

class TicketResponse(BaseModel):
    id: str
    ticket_code: str
    organization_id: str
    customer_id: str
    assigned_agent_id: Optional[str] = None
    subject: str
    description: str
    category: str
    intent: str
    sentiment: str
    urgency: str
    priority: str
    status: str
    sla_due_at: Optional[datetime] = None
    resolution_notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Knowledge Base & RAG Schemas
class DocumentResponse(BaseModel):
    id: str
    organization_id: str
    title: str
    file_type: str
    file_size: int
    chunk_count: int
    is_indexed: bool
    created_at: datetime

    class Config:
        from_attributes = True

class RagQueryInput(BaseModel):
    question: str

class RagQueryOutput(BaseModel):
    question: str
    answer: str
    confidence: float
    sources: List[Dict[str, Any]]
    escalation_required: bool

# Copilot & Intelligence Schemas
class CopilotQueryInput(BaseModel):
    prompt: str

class CopilotQueryOutput(BaseModel):
    answer: str
    suggested_actions: List[str]
    context_used: Dict[str, Any]

class ExecutiveMetricsOutput(BaseModel):
    mrr: float
    arr: float
    total_pipeline_value: float
    weighted_pipeline_value: float
    total_leads: int
    total_customers: int
    open_tickets: int
    avg_health_score: float
    high_churn_risk_count: int
    conversion_rate: float

class ExecutiveInsightsOutput(BaseModel):
    summary: str
    highlights: List[str]
    risks: List[str]
    action_items: List[str]

# Workflow Schemas
class WorkflowCreate(BaseModel):
    name: str
    description: Optional[str] = None
    trigger_event: str
    actions_json: List[Dict[str, Any]]

class WorkflowResponse(BaseModel):
    id: str
    organization_id: str
    name: str
    description: Optional[str] = None
    trigger_event: str
    actions_json: List[Any]
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

# Audit & Billing Schemas
class AuditLogResponse(BaseModel):
    id: str
    organization_id: str
    user_id: Optional[str] = None
    user_email: Optional[str] = None
    action: str
    resource_type: str
    resource_id: Optional[str] = None
    details_json: Dict[str, Any]
    ip_address: str
    created_at: datetime

    class Config:
        from_attributes = True

class UsageSummaryOutput(BaseModel):
    plan_tier: str
    monthly_price: float
    ai_requests_used: int
    ai_requests_limit: int
    storage_bytes_used: int
    storage_bytes_limit: int
    workflow_runs_used: int
    workflow_runs_limit: int
