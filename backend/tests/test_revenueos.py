import os
import sys
import pytest
from fastapi.testclient import TestClient

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from main import app
from app.services.ml_engine import ml_engine
from app.services.rag_engine import rag_engine

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"

def test_login_demo_user():
    response = client.post("/api/v1/auth/login", json={
        "email": "owner@acme.com",
        "password": "Password123!"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["user"]["email"] == "owner@acme.com"

def test_lead_scoring_ml():
    res = ml_engine.calculate_lead_score(
        company_size="1000+",
        industry="Technology",
        source="Inbound Demo",
        deal_value=85000,
        activity_count=4
    )
    assert res["score"] >= 80
    assert res["risk_level"] == "Low"
    assert len(res["factors"]) > 0

def test_rag_chunking_and_similarity():
    text = "RevenueOS AI provides unified lead scoring, RAG support ticketing, and customer health analytics."
    chunks = rag_engine.chunk_text(text, chunk_size=10, overlap=2)
    assert len(chunks) > 0
    
    vec1 = [1.0, 0.0, 0.0]
    vec2 = [1.0, 0.0, 0.0]
    sim = rag_engine.cosine_similarity(vec1, vec2)
    assert sim == 1.0
