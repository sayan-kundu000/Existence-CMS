from datetime import datetime, timezone
from typing import Optional
from fastapi import Depends, Header, Request
from sqlalchemy.orm import Session
from app.dependencies.database import get_db
from app.dependencies.auth import require_admin
from app.core.exceptions import PinRequiredError
from app.models.user import User, PinVerificationSession
from app.services.pin_service import verify_user_pin


def require_pin_verification(
    request: Request,
    x_action_pin: Optional[str] = Header(None, alias="X-Action-PIN"),
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
) -> User:
    """
    PIN Security Gateway:
    Validates X-Action-PIN header on content mutation and deletion endpoints.
    Accepts either:
    1. A short-lived PinVerificationSession token (UUID) created upon successful verification.
    2. The raw security PIN (e.g. 4-digit PIN), executing full lockout-protected verification.
    """
    if not x_action_pin or not x_action_pin.strip():
        raise PinRequiredError("Security PIN required to execute this modification. Provide header 'X-Action-PIN'.")

    pin_token_candidate = x_action_pin.strip()
    client_ip = request.client.host if request.client else "unknown"

    # 1. Check if token matches an active, unexpired, unrevoked PinVerificationSession
    now_utc = datetime.now(timezone.utc)
    active_sessions = db.query(PinVerificationSession).filter(
        PinVerificationSession.admin_user_id == current_user.id,
        PinVerificationSession.verification_identifier == pin_token_candidate,
        PinVerificationSession.revoked_at.is_(None)
    ).all()

    for s in active_sessions:
        exp = s.expires_at
        if exp.tzinfo is None:
            exp = exp.replace(tzinfo=timezone.utc)
        if exp > now_utc:
            return current_user

    # 2. Otherwise verify as raw PIN with strict attempt tracking & lockout protection
    verify_user_pin(
        db=db,
        user_id=current_user.id,
        pin=pin_token_candidate,
        username=current_user.username,
        ip_address=client_ip
    )
    return current_user
