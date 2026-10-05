from datetime import datetime, timezone
from typing import Optional, Callable
from fastapi import Depends, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.dependencies.database import get_db
from app.core.security import decode_access_token
from app.core.permissions import has_permission, Permissions
from app.core.exceptions import AuthenticationFailedError, PermissionDeniedError
from app.models.user import User, AuthSession

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)


def get_current_user(
    request: Request,
    token: Optional[str] = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """
    Extract and validate bearer token, returning the authenticated user.
    Enforces server-side session tracking and revocation verification.
    """
    if not token:
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]

    if not token:
        raise AuthenticationFailedError("Authentication token required.")

    payload = decode_access_token(token)
    if not payload or not payload.get("sub"):
        raise AuthenticationFailedError("Invalid or expired authentication token.")

    try:
        user_id = int(payload["sub"])
    except (ValueError, TypeError):
        raise AuthenticationFailedError("Malformed token subject.")

    # Server-side AuthSession revocation verification if jti was embedded
    jti = payload.get("jti")
    if jti:
        session = db.query(AuthSession).filter(
            AuthSession.token_identifier == jti,
            AuthSession.admin_user_id == user_id
        ).first()

        if session:
            if session.revoked_at is not None:
                raise AuthenticationFailedError("This session has been revoked. Please log in again.")

            now_utc = datetime.now(timezone.utc)
            expires_at = session.expires_at
            if expires_at.tzinfo is None:
                expires_at = expires_at.replace(tzinfo=timezone.utc)

            if now_utc > expires_at:
                raise AuthenticationFailedError("Session has expired.")

            # Update last activity timestamp
            session.last_used_at = now_utc
            db.commit()

        request.state.current_token_jti = jti

    user = db.query(User).filter(User.id == user_id, User.is_active == True).first()
    if not user:
        raise AuthenticationFailedError("User account not found or deactivated.")

    request.state.current_user = user
    return user


def get_optional_current_user(
    request: Request,
    token: Optional[str] = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """
    Optional user extractor for endpoints that deliver differentiated responses
    for public visitors vs authenticated administrators without throwing 401.
    """
    try:
        return get_current_user(request=request, token=token, db=db)
    except Exception:
        return None


def require_authenticated_user(current_user: User = Depends(get_current_user)) -> User:
    """Enforce that the caller is an active authenticated user."""
    return current_user


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """Enforce administrative role or security management capability."""
    if current_user.role != "admin" and not has_permission(current_user.role, Permissions.SECURITY_MANAGE):
        raise PermissionDeniedError("Administrative privileges required to access this resource.")
    return current_user


def require_permission(permission: str) -> Callable[[User], User]:
    """
    Dependency factory enforcing a specific capability permission.
    Adheres to the centralized RBAC capabilities model.
    """
    def dependency(current_user: User = Depends(get_current_user)) -> User:
        if not has_permission(current_user.role, permission):
            raise PermissionDeniedError(f"Permission '{permission}' is required to perform this action.")
        return current_user
    return dependency
