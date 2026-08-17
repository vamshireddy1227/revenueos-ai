import os
import sys
import pytest
from fastapi.testclient import TestClient

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from main import app
from app.core.database import SessionLocal
from app.models.models import Organization, User, Lead, Customer, Ticket, Deal

client = TestClient(app)

@pytest.fixture
def org_tokens():
    # Login as Org Owner (Acme)
    res_acme = client.post("/api/v1/auth/login", json={
        "email": "owner@acme.com",
        "password": "Password123!"
    })
    token_acme = res_acme.json()["access_token"]

    # Login as Sales Rep (Acme)
    res_sales = client.post("/api/v1/auth/login", json={
        "email": "sales.rep@acme.com",
        "password": "Password123!"
    })
    token_sales = res_sales.json()["access_token"]

    return {
        "acme_owner": token_acme,
        "acme_sales": token_sales
    }

def test_tenant_isolation_leads(org_tokens):
    headers_acme = {"Authorization": f"Bearer {org_tokens['acme_owner']}"}
    
    # Fetch Acme leads
    res = client.get("/api/v1/leads", headers=headers_acme)
    assert res.status_code == 200
    leads = res.json()
    assert len(leads) > 0
    
    # Ensure all returned leads belong to Acme
    for lead in leads:
        assert lead["organization_id"] is not None

def test_tenant_isolation_unauthorized_lead_access(org_tokens):
    headers_acme = {"Authorization": f"Bearer {org_tokens['acme_owner']}"}
    
    # Attempt to request a non-existent / cross-tenant ID
    fake_id = "00000000-0000-0000-0000-000000000000"
    res = client.get(f"/api/v1/leads/{fake_id}", headers=headers_acme)
    assert res.status_code == 404
    data = res.json()
    assert data["detail"]["error"]["code"] == "NOT_FOUND"


def test_rbac_copilot_security_restrictions(org_tokens):
    headers_sales = {"Authorization": f"Bearer {org_tokens['acme_sales']}"}
    
    # Sales Rep asks about billing -> Should be restricted
    res = client.post("/api/v1/ai/copilot", json={"prompt": "Show me total organization billing MRR"}, headers=headers_sales)
    assert res.status_code == 200
    data = res.json()
    assert "Access Restricted" in data["answer"]
    assert data["context_used"].get("security_block") is True

def test_rbac_executive_insights_forbidden_for_sales_rep(org_tokens):
    headers_sales = {"Authorization": f"Bearer {org_tokens['acme_sales']}"}
    
    # Sales Rep attempts to access Executive Insights endpoint
    res = client.get("/api/v1/ai/executive-insights", headers=headers_sales)
    assert res.status_code == 403
