from typing import Optional
from fastapi import Depends, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.dependencies.database import get_db
from app.core.security import decode_access_token
from app.core.exceptions import AuthenticationFailedError, PermissionDeniedError
from app.models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)


def get_current_user(
    request: Request,
    token: Optional[str] = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """Extract and validate bearer token, returning the authenticated user."""
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

    user = db.query(User).filter(User.id == user_id, User.is_active == True).first()
    if not user:
        raise AuthenticationFailedError("User account not found or deactivated.")

    return user


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """Enforce administrative role."""
    if current_user.role != "admin":
        raise PermissionDeniedError("Administrative privileges required to access this resource.")
    return current_user
