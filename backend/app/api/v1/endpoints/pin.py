from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user import User
from app.api.deps import get_current_user
from app.schemas.pin import (
    PinSetupRequest,
    PinVerifyRequest,
    PinChangeRequest,
    PinStatusResponse,
    PinVerifyResponse
)
from app.services.pin_service import (
    get_pin_status,
    setup_pin,
    verify_user_pin,
    change_pin
)

router = APIRouter()


@router.get("/status", response_model=PinStatusResponse)
def check_pin_status(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Check whether PIN is configured, locked, or remaining attempts."""
    status_info = get_pin_status(db, current_user.id)
    return status_info


@router.post("/setup", response_model=PinVerifyResponse)
def initialize_pin(
    req: PinSetupRequest,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Set up initial security PIN for the account."""
    client_ip = request.client.host if request.client else "unknown"
    setup_pin(
        db=db,
        user_id=current_user.id,
        pin=req.pin,
        username=current_user.username,
        ip_address=client_ip
    )
    return PinVerifyResponse(success=True, message="Security PIN successfully configured.")


@router.post("/verify", response_model=PinVerifyResponse)
def verify_pin_action(
    req: PinVerifyRequest,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Verify security PIN to authorize sensitive editing operations and issue short-lived verification token."""
    import uuid
    from datetime import datetime, timedelta, timezone
    from app.models.user import PinVerificationSession

    client_ip = request.client.host if request.client else "unknown"
    verify_user_pin(
        db=db,
        user_id=current_user.id,
        pin=req.pin,
        username=current_user.username,
        ip_address=client_ip
    )

    # Issue a 15-minute verification session token
    verif_id = str(uuid.uuid4())
    expires = datetime.now(timezone.utc) + timedelta(minutes=15)
    verif_session = PinVerificationSession(
        admin_user_id=current_user.id,
        verification_identifier=verif_id,
        expires_at=expires
    )
    db.add(verif_session)
    db.commit()

    return PinVerifyResponse(
        success=True,
        message="PIN verified successfully.",
        pin_token=verif_id
    )


@router.post("/change", response_model=PinVerifyResponse)
def modify_pin(
    req: PinChangeRequest,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Change security PIN by confirming current PIN."""
    client_ip = request.client.host if request.client else "unknown"
    change_pin(
        db=db,
        user_id=current_user.id,
        current_pin=req.current_pin,
        new_pin=req.new_pin,
        username=current_user.username,
        ip_address=client_ip
    )
    return PinVerifyResponse(success=True, message="Security PIN successfully changed.")
