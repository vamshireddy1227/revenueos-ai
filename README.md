# RevenueOS AI — Enterprise B2B AI Revenue & Customer Operations Platform

RevenueOS AI is an enterprise-grade, modular B2B SaaS platform designed to unify AI Sales, CRM, AI Customer Support, Customer 360 Intelligence, Revenue Forecasting, Workflow Automation, and RAG Knowledge Bases with strict multi-tenant isolation and role-based access control (RBAC).

---

## 🌟 Platform Architecture

```
                    WEB APPLICATION (React + TypeScript + Vite)
                                      │
                                      ▼
                      API LAYER (FastAPI + Pydantic v2)
                                      │
       ┌──────────────────────────────┼──────────────────────────────┐
       ▼                              ▼                              ▼
 SALES INTELLIGENCE            SUPPORT OPERATIONS            CUSTOMER 360
  • ML Lead Scoring             • AI Intent & Sentiment       • Customer Health (0-100)
  • 6-Stage Deal Kanban         • Auto SLA Priority           • Churn Risk Prediction
  • Revenue Forecasting         • RAG Knowledge Search        • Upsell Intelligence
       │                              │                              │
       └──────────────────────────────┼──────────────────────────────┘
                                      ▼
                      GLOBAL AI BUSINESS COPILOT
                                      │
                              POSTGRESQL / SQLITE
```

---

## 🚀 Key Enterprise Features & Go-Live Hardening

1. **Multi-Tenant SaaS Security**: Strict tenant isolation (`organization_id` FK) enforced at application and database query levels.
2. **Role-Based Access Control (RBAC)**: Matrix supporting 7 personas (`Organization Owner`, `Admin`, `Sales Manager`, `Sales Representative`, `Support Manager`, `Support Agent`, `Executive`). Copilot restricts non-executive access to natural language billing queries.
3. **AI Sales & ML Lead Scoring**: Dynamic 0-100 score, conversion probability, risk level attribution, and recommended action steps.
4. **AI Customer Support & RAG Knowledge Base**: Auto intent/sentiment ticket tagging, grounded vector search query engine with citation sources.
5. **Customer 360 & Churn Intelligence**: Single-pane operational dashboard with health scores, churn probability, and expansion upsell recommendations.
6. **Executive Revenue Intelligence**: Live ARR/MRR summaries, weighted deal forecasting, and generative AI executive reports.
7. **Global AI Business Copilot & AI Status Endpoint**: Context-aware conversational assistant + `GET /api/v1/ai/status` administrative observability endpoint.
8. **Workflow Automation & Integration Center**: Trigger-action execution engine with operational mode indicators (`MOCK`, `SANDBOX`, `PRODUCTION`) for HubSpot, Salesforce, SendGrid, Slack, and Stripe.
9. **SaaS Billing & Audit Logging**: Tiered subscription plans (`Starter`, `Growth`, `Business`, `Enterprise`), usage metering progress bars, Stripe webhook signature handler, and compliance audit trail.
10. **Database Bootstrap & Backups**: `backend/app/seed/init_db.py` zero-init script and `scripts/backup_restore.py` administration utility.

---

## 🛠️ Tech Stack

- **Backend**: Python 3.10+, FastAPI, SQLAlchemy 2.0, Pydantic v2, PyJWT, Pytest
- **Frontend**: React 18, TypeScript, Vite, Tailwind CSS, Lucide Icons
- **Database & Vectors**: PostgreSQL + pgvector (or instant local zero-setup SQLite/Numpy adapter)
- **Infrastructure**: Docker, Docker Compose, GitHub Actions CI/CD

---

## ⚡ Quick Start & Development

### 1. Unified Launcher
```bash
python run_dev.py
```
- **Frontend App**: `http://localhost:5173`
- **Backend API & Swagger Docs**: `http://localhost:8000/docs`
- **AI Status Endpoint**: `http://localhost:8000/api/v1/ai/status`
- **Health Check**: `http://localhost:8000/health`

### 2. Database Bootstrap & Integrity Check
```bash
python backend/app/seed/init_db.py
```

### 3. Database Backup & Restore
```bash
# Perform snapshot backup
python scripts/backup_restore.py backup

# Perform database restore
python scripts/backup_restore.py restore --file ./backups/revenueos_backup_20260812_181900.sql
```

### 4. Run Automated Security & Pytest Suite
```bash
pytest backend/tests/
```

---

## 🔑 Demo Personas & Login Credentials

| Role | Email | Password |
|---|---|---|
| Organization Owner | `owner@acme.com` | `Password123!` |
| Sales Manager | `sales.mgr@acme.com` | `Password123!` |
| Support Agent | `support@acme.com` | `Password123!` |
| Executive | `ceo@acme.com` | `Password123!` |
