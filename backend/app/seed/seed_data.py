import sys
import os
import random

# Ensure parent directory is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from app.core.database import SessionLocal, engine, Base
from app.core.security import get_password_hash
from app.models.models import (
    Organization, User, Lead, Deal, Customer, Ticket, TicketEvent,
    Document, DocumentChunk, Workflow, Integration, AuditLog, Subscription
)
from app.services.ml_engine import ml_engine
from app.services.ai_provider import ai_provider

def seed():
    print("Initializing Database tables...")
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        # Check if already seeded
        if db.query(Organization).first():
            print("Database already contains data. Skipping seed.")
            return

        print("Seeding Enterprise Demo Data for RevenueOS AI...")

        # 1. Organizations
        org_acme = Organization(name="Acme Enterprise Inc.", slug="acme-enterprise", plan="Enterprise")
        org_horizon = Organization(name="Horizon Tech Cloud", slug="horizon-tech", plan="Growth")
        org_apex = Organization(name="Apex Solutions Group", slug="apex-solutions", plan="Business")

        db.add_all([org_acme, org_horizon, org_apex])
        db.flush()

        # 2. Users for Acme
        owner = User(
            organization_id=org_acme.id,
            email="owner@acme.com",
            hashed_password=get_password_hash("Password123!"),
            full_name="Sarah Jenkins",
            role="Organization Owner"
        )
        sales_mgr = User(
            organization_id=org_acme.id,
            email="sales.mgr@acme.com",
            hashed_password=get_password_hash("Password123!"),
            full_name="Marcus Vance",
            role="Sales Manager"
        )
        sales_rep = User(
            organization_id=org_acme.id,
            email="sales.rep@acme.com",
            hashed_password=get_password_hash("Password123!"),
            full_name="Alex Rivera",
            role="Sales Representative"
        )
        support_agent = User(
            organization_id=org_acme.id,
            email="support@acme.com",
            hashed_password=get_password_hash("Password123!"),
            full_name="Elena Rostova",
            role="Support Agent"
        )
        exec_user = User(
            organization_id=org_acme.id,
            email="ceo@acme.com",
            hashed_password=get_password_hash("Password123!"),
            full_name="David Sterling",
            role="Executive"
        )

        db.add_all([owner, sales_mgr, sales_rep, support_agent, exec_user])
        db.flush()

        # 3. Leads for Acme
        companies_data = [
            ("CloudScale Systems", "Technology", "1000+", 85000, "Website"),
            ("FinTech Global", "Finance", "201-1000", 65000, "Inbound Demo"),
            ("HealthCare Plus", "Healthcare", "51-200", 42000, "Referral"),
            ("Nexus Logistics", "Logistics", "1000+", 120000, "Website"),
            ("DataFlow AI", "Technology", "11-50", 18000, "Outbound"),
            ("Apex Retailers", "Retail", "201-1000", 35000, "Inbound Demo"),
            ("CyberShield Security", "Cybersecurity", "1000+", 95000, "Referral"),
            ("BioGen Labs", "Biotech", "51-200", 50000, "Website"),
            ("Solaris Energy", "Clean Energy", "201-1000", 78000, "Outbound"),
            ("Vortex Media", "Media", "11-50", 15000, "Website")
        ]

        leads_list = []
        for i in range(50):
            idx = i % len(companies_data)
            comp, ind, sz, val, src = companies_data[idx]
            name = f"Executive Lead {i+1}"
            email = f"lead{i+1}@{comp.lower().replace(' ', '')}.com"
            
            ml_res = ml_engine.calculate_lead_score(sz, ind, src, val, activity_count=random.randint(1, 4))
            status = random.choice(["New", "Contacted", "Qualified", "Nurturing", "Converted", "Lost"])

            lead = Lead(
                organization_id=org_acme.id,
                owner_id=sales_rep.id if i % 2 == 0 else sales_mgr.id,
                name=f"John Doe {i+1}",
                email=email,
                company_name=f"{comp} #{i+1}",
                industry=ind,
                company_size=sz,
                source=src,
                status=status,
                deal_value=float(val),
                score=ml_res["score"],
                conversion_prob=ml_res["conversion_prob"],
                risk_level=ml_res["risk_level"],
                score_factors=ml_res["factors"],
                recommended_action=ml_res["recommended_action"],
                tags=["Enterprise", "Q3-Target"] if val > 50000 else ["Mid-Market"]
            )
            leads_list.append(lead)

        db.add_all(leads_list)

        # 4. Deals
        deal_stages = ["New Lead", "Qualified", "Discovery", "Proposal", "Negotiation", "Won", "Lost"]
        deals = []
        for idx in range(12):
            stage = deal_stages[idx % len(deal_stages)]
            val = float((idx + 1) * 25000)
            risk = "High" if idx in [3, 7] else "Low"
            deal = Deal(
                organization_id=org_acme.id,
                owner_id=sales_rep.id,
                name=f"Enterprise License - Deal #{idx+1}",
                value=val,
                probability=0.8 if stage == "Negotiation" else 0.5,
                stage=stage,
                risk_level=risk,
                ai_recommendation=f"High priority deal (${val:,.0f}). Schedule executive sponsor review before contract execution."
            )
            deals.append(deal)
        db.add_all(deals)

        # 5. Customers (including At-Risk for demo)
        c1 = Customer(
            organization_id=org_acme.id,
            name="Global Dynamics Corp",
            email="contact@globaldynamics.com",
            industry="Technology",
            region="North America",
            subscription_plan="Enterprise",
            mrr=12500.0,
            arr=150000.0,
            health_score=92,
            health_status="Healthy",
            churn_risk_score=0.08,
            churn_risk_factors=["High product activity", "Consistently pays on time"]
        )
        c2 = Customer(
            organization_id=org_acme.id,
            name="OmniCorp Logistics",
            email="support@omnicorp.com",
            industry="Logistics",
            region="Europe",
            subscription_plan="Business",
            mrr=4500.0,
            arr=54000.0,
            health_score=45,
            health_status="At Risk",
            churn_risk_score=0.68,
            churn_risk_factors=["Reduced activity in last 30 days", "3 unresolved support tickets logged"]
        )
        c3 = Customer(
            organization_id=org_acme.id,
            name="Starlight Media",
            email="billing@starlight.io",
            industry="Media",
            region="Asia Pacific",
            subscription_plan="Growth",
            mrr=2200.0,
            arr=26400.0,
            health_score=35,
            health_status="Critical",
            churn_risk_score=0.85,
            churn_risk_factors=["Negative sentiment detected in ticket conversations", "Contract renewal in 14 days"]
        )
        db.add_all([c1, c2, c3])
        db.flush()

        # 6. Support Tickets
        t1 = Ticket(
            ticket_code="TICK-8801",
            organization_id=org_acme.id,
            customer_id=c2.id,
            assigned_agent_id=support_agent.id,
            subject="API Rate Limit Exceeded on Batch Processing",
            description="Our automated data pipeline keeps returning HTTP 429 error rate limit exceeded when pushing end of day reports.",
            category="Technical issue",
            intent="Technical issue",
            sentiment="Negative",
            urgency="High",
            priority="High",
            status="In Progress"
        )
        t2 = Ticket(
            ticket_code="TICK-8802",
            organization_id=org_acme.id,
            customer_id=c3.id,
            assigned_agent_id=support_agent.id,
            subject="Billing Discrepancy on Annual Invoice",
            description="We were charged for 50 additional user seats that we did not request on our latest monthly invoice statement.",
            category="Billing",
            intent="Billing",
            sentiment="Angry",
            urgency="Critical",
            priority="Critical",
            status="Open"
        )
        db.add_all([t1, t2])

        # 7. Knowledge Base Document
        doc_content = """
        RevenueOS AI Enterprise Knowledge Base & Support Guidelines:
        1. Refund Policy: Enterprise customers are eligible for a 30-day money-back guarantee if SLA guarantees are breached.
        2. API Quota Limits: Growth tier accounts include 10,000 requests/day. Business tier includes 100,000 requests/day. Enterprise includes custom dedicated instances.
        3. Security & SLA: We guarantee 99.99% uptime with 24/7 dedicated support for Enterprise accounts.
        """
        doc = Document(
            organization_id=org_acme.id,
            title="RevenueOS Enterprise Service & Policy Guide.txt",
            file_type="txt",
            file_size=len(doc_content.encode('utf-8')),
            chunk_count=2,
            is_indexed=True
        )
        db.add(doc)
        db.flush()

        chunk1 = DocumentChunk(
            document_id=doc.id,
            organization_id=org_acme.id,
            chunk_index=0,
            content=doc_content,
            embedding_json=ai_provider.get_embedding(doc_content),
            metadata_json={"doc_title": doc.title, "chunk_index": 0}
        )
        db.add(chunk1)

        # 8. Workflows
        wf = Workflow(
            organization_id=org_acme.id,
            name="High Score Lead Immediate Alert",
            description="Notify sales team immediately when a lead score exceeds 75.",
            trigger_event="lead_created",
            actions_json=[{"type": "send_notification", "title": "High Intent Lead Created", "priority": "high"}]
        )
        db.add(wf)

        # 9. Audit Logs
        audit = AuditLog(
            organization_id=org_acme.id,
            user_id=owner.id,
            user_email=owner.email,
            action="SYSTEM_INITIALIZED",
            resource_type="Organization",
            resource_id=org_acme.id,
            details_json={"message": "RevenueOS AI platform demo dataset initialized cleanly."}
        )
        db.add(audit)

        db.commit()
        print("Demo data seeded successfully!")

    except Exception as e:
        db.rollback()
        print(f"Error seeding demo data: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed()
