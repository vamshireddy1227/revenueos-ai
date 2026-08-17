from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import verify_password, get_password_hash, create_access_token, create_refresh_token
from app.models.models import User, Organization
from app.schemas.schemas import LoginRequest, TokenResponse, SignupRequest, UserResponse
from app.auth.deps import get_current_user, RequireRole
from app.services.audit_service import audit_service

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/signup", response_model=TokenResponse)
def signup(req: SignupRequest, db: Session = Depends(get_db)):
    # Check if email exists
    existing_user = db.query(User).filter(User.email == req.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": {"code": "EMAIL_EXISTS", "message": "Email is already registered."}}
        )
    
    # Create Organization
    slug = req.org_name.lower().replace(" ", "-") + "-org"
    org = Organization(
        name=req.org_name,
        slug=slug,
        plan=req.plan
    )
    db.add(org)
    db.flush()

    # Create Owner User
    hashed_pwd = get_password_hash(req.password)
    user = User(
        organization_id=org.id,
        email=req.email,
        hashed_password=hashed_pwd,
        full_name=req.full_name,
        role="Organization Owner",
        is_active=True
    )
    db.add(user)
    db.commit()

    audit_service.log(db, org.id, "USER_REGISTERED", "User", user.id, user.email, user.id, {"org_name": org.name})

    access_token = create_access_token({"sub": user.id, "org_id": org.id, "role": user.role})
    refresh_token = create_refresh_token({"sub": user.id})

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user=UserResponse.model_validate(user)
    )

@router.post("/login", response_model=TokenResponse)
def login(req: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == req.email).first()
    if not user or not verify_password(req.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": {"code": "INVALID_CREDENTIALS", "message": "Invalid email or password."}}
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"error": {"code": "USER_INACTIVE", "message": "User account is deactivated."}}
        )

    audit_service.log(db, user.organization_id, "USER_LOGIN", "User", user.id, user.email, user.id)

    access_token = create_access_token({"sub": user.id, "org_id": user.organization_id, "role": user.role})
    refresh_token = create_refresh_token({"sub": user.id})

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user=UserResponse.model_validate(user)
    )

@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return UserResponse.model_validate(current_user)
