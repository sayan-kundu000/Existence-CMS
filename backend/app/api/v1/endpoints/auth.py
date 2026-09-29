from datetime import timedelta, datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import verify_password, hash_password, create_access_token
from app.core.config import settings
from app.models.user import User, PinSecurity
from app.schemas.auth import UserLogin, UserRegister, TokenResponse, UserOut
from app.api.deps import get_current_user
from app.services.audit_service import log_audit_event
from app.services.pin_service import get_or_create_pin_record

router = APIRouter()


@router.post("/login", response_model=TokenResponse)
def login(login_data: UserLogin, request: Request, db: Session = Depends(get_db)):
    """Authenticate administrator and issue JWT access token."""
    client_ip = request.client.host if request.client else "unknown"
    user = db.query(User).filter(User.username == login_data.username).first()

    if not user or not verify_password(login_data.password, user.hashed_password):
        log_audit_event(
            db=db,
            event_type="LOGIN_FAILED",
            status="FAILED",
            username=login_data.username,
            details={"reason": "Invalid credentials"},
            ip_address=client_ip
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )

    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Account is deactivated")

    # Check if PIN is configured
    pin_record = get_or_create_pin_record(db, user.id)

    access_token = create_access_token(
        subject=user.id,
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    log_audit_event(
        db=db,
        event_type="LOGIN",
        status="SUCCESS",
        user_id=user.id,
        username=user.username,
        details={"role": user.role},
        ip_address=client_ip
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        "user_id": user.id,
        "username": user.username,
        "role": user.role,
        "pin_configured": pin_record.is_configured
    }


@router.post("/register", response_model=UserOut)
def register_admin(reg_data: UserRegister, request: Request, db: Session = Depends(get_db)):
    """
    Register initial admin user or add user.
    If no users exist in the system, bootstrap registration is open to initialize the administrator.
    Once an admin exists, registration requires an existing admin.
    """
    total_users = db.query(User).count()
    if total_users > 0:
        # Check if caller has admin authorization header
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin user already initialized. Additional registrations require admin authorization."
            )

    existing_user = db.query(User).filter(
        (User.username == reg_data.username) | (User.email == reg_data.email)
    ).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already registered."
        )

    new_user = User(
        username=reg_data.username,
        email=reg_data.email,
        hashed_password=hash_password(reg_data.password),
        role="admin",
        is_active=True
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Initialize unconfigured PIN record
    get_or_create_pin_record(db, new_user.id)

    log_audit_event(
        db=db,
        event_type="USER_REGISTERED",
        status="SUCCESS",
        user_id=new_user.id,
        username=new_user.username,
        details={"role": new_user.role}
    )

    return new_user


@router.get("/me", response_model=UserOut)
def get_current_user_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve details and PIN status for the currently authenticated admin."""
    pin_record = get_or_create_pin_record(db, current_user.id)
    return UserOut(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        role=current_user.role,
        is_active=current_user.is_active,
        pin_configured=pin_record.is_configured,
        created_at=current_user.created_at
    )
