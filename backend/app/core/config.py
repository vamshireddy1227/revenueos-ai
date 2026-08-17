import os
from typing import List, Optional

try:
    from pydantic_settings import BaseSettings
    from pydantic import Field
except ImportError:
    try:
        from pydantic import BaseSettings, Field
    except ImportError:
        from pydantic import BaseModel
        class BaseSettings(BaseModel):
            pass
        def Field(*args, **kwargs):
            return kwargs.get("default")

class Settings(BaseSettings):
    PROJECT_NAME: str = "RevenueOS AI"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = "development"  # development, staging, production
    
    # Security
    JWT_SECRET: str = "super-secret-key-change-in-production-revenueos-2026"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Database: prefer DATABASE_URL from environment for Postgres/prod, else fall back to local SQLite for dev
    DATABASE_URL: str = Field(
        default_factory=lambda: os.getenv("DATABASE_URL", "sqlite:///./revenueos.db")
    )
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # AI Provider
    AI_PROVIDER: str = "mock"  # mock, openai, gemini, anthropic
    AI_API_KEY: Optional[str] = None
    AI_MODEL: str = "gpt-4o-mini"
    
    # Integrations Optional Credentials
    STRIPE_SECRET_KEY: Optional[str] = None
    STRIPE_WEBHOOK_SECRET: Optional[str] = None
    SENDGRID_API_KEY: Optional[str] = None
    
    # CORS & URLs
    FRONTEND_URL: str = "http://localhost:5173"
    BACKEND_URL: str = "http://localhost:8000"
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
        "*"
    ]

    def validate_production_settings(self):
        """Validate required configuration settings when running in production mode."""
        if self.ENVIRONMENT == "production":
            if self.JWT_SECRET == "super-secret-key-change-in-production-revenueos-2026":
                print("[WARNING] SECURITY RISK: Running in production with default JWT_SECRET!")
            if self.DATABASE_URL.startswith("sqlite"):
                print("[WARNING] PRODUCTION NOTICE: SQLite is active. PostgreSQL is recommended for high-concurrency production.")
            if self.AI_PROVIDER != "mock" and not self.AI_API_KEY:
                print(f"[WARNING] AI PROVIDER NOTICE: AI_PROVIDER set to '{self.AI_PROVIDER}' but AI_API_KEY is missing. Falling back safely to Local AI Provider.")

settings = Settings()
settings.validate_production_settings()
