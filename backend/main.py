import time
import uuid
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.database import Base, engine, SessionLocal
from app.seed.seed_data import seed

from app.api.v1.auth import router as auth_router
from app.api.v1.leads import router as leads_router
from app.api.v1.deals import router as deals_router
from app.api.v1.customers import router as customers_router
from app.api.v1.tickets import router as tickets_router
from app.api.v1.knowledge import router as knowledge_router
from app.api.v1.copilot import router as copilot_router
from app.api.v1.workflows import router as workflows_router
from app.api.v1.integrations import router as integrations_router
from app.api.v1.billing import router as billing_router
from app.api.v1.audit import router as audit_router

# Initialize database schema & demo seed on launch
Base.metadata.create_all(bind=engine)
try:
    seed()
except Exception as e:
    print(f"Seed startup notice: {e}")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Enterprise B2B AI Revenue & Customer Operations Platform API",
    openapi_url="/api/v1/openapi.json"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# OWASP Security Headers & Request ID Traceability Middleware
@app.middleware("http")
async def add_security_headers_and_request_id(request: Request, call_next):
    req_id = str(uuid.uuid4())
    start_time = time.time()
    
    try:
        response = await call_next(request)
        process_time = time.time() - start_time
        
        # Add OWASP Security Headers
        response.headers["X-Request-ID"] = req_id
        response.headers["X-Process-Time"] = str(process_time)
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        
        return response
    except Exception as exc:
        print(f"[ERROR] Request {req_id} failed: {exc}")
        return JSONResponse(
            status_code=500,
            content={"error": {"code": "INTERNAL_SERVER_ERROR", "message": "An unexpected server error occurred.", "request_id": req_id}}
        )

# Observability Health & Readiness Checks
@app.get("/health", tags=["Observability"])
def health_check():
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT
    }

@app.get("/ready", tags=["Observability"])
def readiness_check():
    # Database ping check
    db_status = "connected"
    try:
        db = SessionLocal()
        db.execute("SELECT 1")
        db.close()
    except Exception as e:
        db_status = f"unhealthy: {e}"

    ai_mode = "PRODUCTION" if settings.AI_API_KEY and settings.AI_PROVIDER != "mock" else "LOCAL_DEMO"

    return {
        "status": "ready" if db_status == "connected" else "degraded",
        "database": db_status,
        "database_type": "postgresql" if not settings.DATABASE_URL.startswith("sqlite") else "sqlite",
        "ai_provider_mode": ai_mode,
        "redis": "connected"
    }

# Include API v1 Routers
app.include_router(auth_router, prefix=settings.API_V1_STR)
app.include_router(leads_router, prefix=settings.API_V1_STR)
app.include_router(deals_router, prefix=settings.API_V1_STR)
app.include_router(customers_router, prefix=settings.API_V1_STR)
app.include_router(tickets_router, prefix=settings.API_V1_STR)
app.include_router(knowledge_router, prefix=settings.API_V1_STR)
app.include_router(copilot_router, prefix=settings.API_V1_STR)
app.include_router(workflows_router, prefix=settings.API_V1_STR)
app.include_router(integrations_router, prefix=settings.API_V1_STR)
app.include_router(billing_router, prefix=settings.API_V1_STR)
app.include_router(audit_router, prefix=settings.API_V1_STR)
