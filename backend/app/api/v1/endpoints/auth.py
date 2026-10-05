import uuid
from typing import List
from datetime import timedelta, datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import (
    verify_password,
    hash_password,
    create_access_token,
    validate_password_strength
)
from app.core.config import settings
from app.core.permissions import get_role_permissions
from app.core.rate_limit import rate_limiter
from app.models.user import User, AuthSession, PinSecurity
from app.schemas.auth import (
    UserLogin,
    UserRegister,
    TokenResponse,
    UserOut,
    AuthSessionOut,
    LogoutResponse
)
from app.api.deps import get_current_user
from app.services.audit_service import log_audit_event
from app.services.pin_service import get_or_create_pin_record

router = APIRouter()


@router.post("/login", response_model=TokenResponse)
def login(login_data: UserLogin, request: Request, db: Session = Depends(get_db)):
    """Authenticate administrator, create tracked AuthSession, and issue signed JWT access token."""
    client_ip = request.client.host if request.client else "unknown"

    # Enforce brute-force rate limit by client IP and account target
    rate_limiter.check(
        f"login:{client_ip}",
        limit=settings.RATE_LIMIT_LOGIN_PER_MINUTE,
        window_seconds=60,
        message="Too many login attempts. Please wait before retrying."
    )

    user = db.query(User).filter(User.username == login_data.username).first()

    if not user or not verify_password(login_data.password, user.hashed_password):
        log_audit_event(
            db=db,
            event_type="LOGIN_FAILED",
            status="FAILED",
            username=login_data.username,
            details={"reason": "Invalid credentials", "ip": client_ip},
            ip_address=client_ip
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )

    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Account is deactivated")

    # Reset rate limiting counter on successful authentication
    rate_limiter.reset(f"login:{client_ip}")

    # Check if PIN is configured
    pin_record = get_or_create_pin_record(db, user.id)

    # Generate unique session identifier (JTI)
    session_jti = str(uuid.uuid4())
    now_utc = datetime.now(timezone.utc)
    expires_at = now_utc + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    auth_session = AuthSession(
        admin_user_id=user.id,
        token_identifier=session_jti,
        expires_at=expires_at,
        created_at=now_utc,
        last_used_at=now_utc
    )
    db.add(auth_session)

    user.last_login_at = now_utc
    db.commit()

    access_token = create_access_token(
        subject=user.id,
        jti=session_jti,
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        claims={"role": user.role}
    )

    log_audit_event(
        db=db,
        event_type="LOGIN",
        status="SUCCESS",
        user_id=user.id,
        username=user.username,
        details={"role": user.role, "session_id": session_jti},
        ip_address=client_ip
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        "user_id": user.id,
        "username": user.username,
        "role": user.role,
        "pin_configured": pin_record.is_configured,
        "permissions": get_role_permissions(user.role)
    }


@router.post("/logout", response_model=LogoutResponse)
def logout(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Secure server-side logout:
    Revokes the current AuthSession token identifier so it cannot be reused.
    """
    client_ip = request.client.host if request.client else "unknown"
    jti = getattr(request.state, "current_token_jti", None)

    if jti:
        db.query(AuthSession).filter(
            AuthSession.token_identifier == jti,
            AuthSession.admin_user_id == current_user.id
        ).update({"revoked_at": datetime.now(timezone.utc)})
        db.commit()

    log_audit_event(
        db=db,
        event_type="LOGOUT",
        status="SUCCESS",
        user_id=current_user.id,
        username=current_user.username,
        details={"session_id": jti},
        ip_address=client_ip
    )

    return LogoutResponse(
        success=True,
        message="Successfully logged out. Session has been revoked."
    )


@router.post("/logout-all", response_model=LogoutResponse)
def logout_all_sessions(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Revoke all active sessions for the current authenticated user.
    Useful when a credential or session might be compromised.
    """
    client_ip = request.client.host if request.client else "unknown"
    now_utc = datetime.now(timezone.utc)

    revoked_count = db.query(AuthSession).filter(
        AuthSession.admin_user_id == current_user.id,
        AuthSession.revoked_at.is_(None)
    ).update({"revoked_at": now_utc})
    db.commit()

    log_audit_event(
        db=db,
        event_type="LOGOUT_ALL",
        status="SUCCESS",
        user_id=current_user.id,
        username=current_user.username,
        details={"revoked_sessions_count": revoked_count},
        ip_address=client_ip
    )

    return LogoutResponse(
        success=True,
        message=f"All {revoked_count} active sessions have been revoked."
    )


@router.get("/sessions", response_model=List[AuthSessionOut])
def list_active_sessions(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve all non-revoked, unexpired active sessions for the current user."""
    now_utc = datetime.now(timezone.utc)
    current_jti = getattr(request.state, "current_token_jti", None)

    sessions = db.query(AuthSession).filter(
        AuthSession.admin_user_id == current_user.id,
        AuthSession.revoked_at.is_(None)
    ).order_by(AuthSession.created_at.desc()).all()

    active_list = []
    for s in sessions:
        exp = s.expires_at
        if exp.tzinfo is None:
            exp = exp.replace(tzinfo=timezone.utc)
        if exp > now_utc:
            active_list.append(
                AuthSessionOut(
                    id=s.id,
                    token_identifier=s.token_identifier,
                    expires_at=s.expires_at,
                    created_at=s.created_at,
                    last_used_at=s.last_used_at,
                    is_current=(s.token_identifier == current_jti)
                )
            )

    return active_list


@router.post("/register", response_model=UserOut)
def register_admin(reg_data: UserRegister, request: Request, db: Session = Depends(get_db)):
    """
    Register initial admin user or add user.
    Enforces server-side password policy.
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

    # Server-side password strength policy check
    validate_password_strength(reg_data.password)

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

    return UserOut(
        id=new_user.id,
        username=new_user.username,
        email=new_user.email,
        role=new_user.role,
        is_active=new_user.is_active,
        pin_configured=False,
        permissions=get_role_permissions(new_user.role),
        created_at=new_user.created_at
    )


@router.get("/me", response_model=UserOut)
def get_current_user_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve details, permissions, and PIN status for the currently authenticated user."""
    pin_record = get_or_create_pin_record(db, current_user.id)
    return UserOut(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        role=current_user.role,
        is_active=current_user.is_active,
        pin_configured=pin_record.is_configured,
        permissions=get_role_permissions(current_user.role),
        created_at=current_user.created_at
    )
