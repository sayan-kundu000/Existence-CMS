from datetime import datetime, timedelta, timezone
from typing import Optional, Tuple
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.user import PinSecurity
from app.core.security import hash_pin, verify_pin
from app.core.config import settings
from app.services.audit_service import log_audit_event


def get_or_create_pin_record(db: Session, user_id: int) -> PinSecurity:
    """Retrieve PIN security record or initialize a blank unconfigured record."""
    pin_record = db.query(PinSecurity).filter(PinSecurity.user_id == user_id).first()
    if not pin_record:
        pin_record = PinSecurity(
            user_id=user_id,
            hashed_pin="",
            is_configured=False,
            failed_attempts=0,
            is_locked=False
        )
        db.add(pin_record)
        db.commit()
        db.refresh(pin_record)
    return pin_record


def check_lockout(pin_record: PinSecurity, db: Session) -> None:
    """Check if the PIN record is currently locked out."""
    if pin_record.is_locked:
        if pin_record.locked_until and datetime.now(timezone.utc) < pin_record.locked_until.replace(tzinfo=timezone.utc):
            remaining = int((pin_record.locked_until.replace(tzinfo=timezone.utc) - datetime.now(timezone.utc)).total_seconds() / 60)
            raise HTTPException(
                status_code=status.HTTP_423_LOCKED,
                detail=f"PIN is temporarily locked due to excessive failed attempts. Please retry in {max(1, remaining)} minute(s)."
            )
        else:
            # Lockout period expired; automatically unlock and reset counter
            pin_record.is_locked = False
            pin_record.failed_attempts = 0
            pin_record.locked_until = None
            db.commit()


def setup_pin(db: Session, user_id: int, pin: str, username: str, ip_address: Optional[str] = None) -> bool:
    """Set up initial security PIN."""
    pin_record = get_or_create_pin_record(db, user_id)
    if pin_record.is_configured:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="PIN is already configured. Use the change PIN endpoint to modify it."
        )

    pin_record.hashed_pin = hash_pin(pin)
    pin_record.is_configured = True
    pin_record.failed_attempts = 0
    pin_record.is_locked = False
    pin_record.locked_until = None
    pin_record.last_verified_at = datetime.now(timezone.utc)
    db.commit()

    log_audit_event(
        db=db,
        event_type="PIN_SETUP",
        user_id=user_id,
        username=username,
        status="SUCCESS",
        details={"message": "Security PIN successfully initialized"},
        ip_address=ip_address
    )
    return True


def verify_user_pin(db: Session, user_id: int, pin: str, username: str, ip_address: Optional[str] = None) -> bool:
    """
    Verify security PIN with strict failure tracking and lockout protection.
    Raises HTTPException if invalid or locked.
    """
    pin_record = get_or_create_pin_record(db, user_id)
    if not pin_record.is_configured:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="PIN has not been configured yet. Please configure your security PIN first."
        )

    check_lockout(pin_record, db)

    if not verify_pin(pin, pin_record.hashed_pin):
        pin_record.failed_attempts += 1
        remaining = max(0, settings.PIN_MAX_FAILED_ATTEMPTS - pin_record.failed_attempts)

        if pin_record.failed_attempts >= settings.PIN_MAX_FAILED_ATTEMPTS:
            pin_record.is_locked = True
            pin_record.locked_until = datetime.now(timezone.utc) + timedelta(minutes=settings.PIN_LOCKOUT_MINUTES)
            db.commit()

            log_audit_event(
                db=db,
                event_type="PIN_LOCKED",
                user_id=user_id,
                username=username,
                status="LOCKED",
                details={"reason": "Maximum failed attempts exceeded", "lockout_minutes": settings.PIN_LOCKOUT_MINUTES},
                ip_address=ip_address
            )
            raise HTTPException(
                status_code=status.HTTP_423_LOCKED,
                detail=f"Incorrect PIN. Maximum attempts exceeded. Locked for {settings.PIN_LOCKOUT_MINUTES} minutes."
            )

        db.commit()
        log_audit_event(
            db=db,
            event_type="PIN_FAILED",
            user_id=user_id,
            username=username,
            status="FAILED",
            details={"attempts_failed": pin_record.failed_attempts, "attempts_remaining": remaining},
            ip_address=ip_address
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid security PIN. {remaining} attempt(s) remaining before temporary lockout."
        )

    # Verification successful
    pin_record.failed_attempts = 0
    pin_record.last_verified_at = datetime.now(timezone.utc)
    db.commit()

    log_audit_event(
        db=db,
        event_type="PIN_VERIFIED",
        user_id=user_id,
        username=username,
        status="SUCCESS",
        details={"message": "PIN verified successfully for sensitive operation"},
        ip_address=ip_address
    )
    return True


def change_pin(db: Session, user_id: int, current_pin: str, new_pin: str, username: str, ip_address: Optional[str] = None) -> bool:
    """Change security PIN after validating current PIN."""
    verify_user_pin(db, user_id, current_pin, username, ip_address)

    pin_record = get_or_create_pin_record(db, user_id)
    pin_record.hashed_pin = hash_pin(new_pin)
    pin_record.failed_attempts = 0
    pin_record.is_locked = False
    pin_record.locked_until = None
    pin_record.last_verified_at = datetime.now(timezone.utc)
    db.commit()

    log_audit_event(
        db=db,
        event_type="PIN_CHANGED",
        user_id=user_id,
        username=username,
        status="SUCCESS",
        details={"message": "Security PIN successfully updated"},
        ip_address=ip_address
    )
    return True


def get_pin_status(db: Session, user_id: int) -> dict:
    """Get current status of user's PIN configuration."""
    pin_record = get_or_create_pin_record(db, user_id)
    remaining = max(0, settings.PIN_MAX_FAILED_ATTEMPTS - pin_record.failed_attempts)
    return {
        "is_configured": pin_record.is_configured,
        "is_locked": pin_record.is_locked,
        "attempts_remaining": remaining,
        "locked_until": pin_record.locked_until,
        "last_verified_at": pin_record.last_verified_at
    }
