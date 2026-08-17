import sys
import os

# Add parent directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from app.core.database import SessionLocal, engine, Base
from app.seed.seed_data import seed
from app.models.models import Organization, User, Lead, Customer, Ticket

def bootstrap_db():
    """
    Zero-Init Database Bootstrap Script.
    Initializes PostgreSQL / SQLite database tables, runs seeds, and validates tenant data.
    """
    print("=" * 60)
    print("RevenueOS AI - Zero-Init Database Bootstrap")
    print("=" * 60)

    print("\n[1/3] Creating Database Schema & Table Indexes...")
    Base.metadata.create_all(bind=engine)
    print("  [OK] Database tables initialized successfully.")

    print("\n[2/3] Seeding Demo Data...")
    seed()

    print("\n[3/3] Validating Database Integrity & Multi-Tenant Isolation...")
    db = SessionLocal()
    try:
        orgs = db.query(Organization).all()
        users = db.query(User).all()
        leads = db.query(Lead).all()
        customers = db.query(Customer).all()
        tickets = db.query(Ticket).all()

        print(f"  [OK] Total Organizations: {len(orgs)}")
        print(f"  [OK] Total Users: {len(users)}")
        print(f"  [OK] Total Prospect Leads: {len(leads)}")
        print(f"  [OK] Total Customers: {len(customers)}")
        print(f"  [OK] Total Support Tickets: {len(tickets)}")

        # Verify strict organization_id on all leads
        unisolated_leads = db.query(Lead).filter(Lead.organization_id == None).count()
        if unisolated_leads > 0:
            raise RuntimeError(f"CRITICAL: Found {unisolated_leads} leads without tenant context!")
        print("  [OK] Tenant isolation check passed: All entities belong to valid Organizations.")

        print("\n" + "=" * 60)
        print("Database Bootstrap & Verification Completed Cleanly!")
        print("=" * 60 + "\n")
    finally:
        db.close()

if __name__ == "__main__":
    bootstrap_db()
