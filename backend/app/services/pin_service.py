from datetime import datetime, timedelta, timezone
from typing import Optional, Tuple
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.user import PinSecurity, PinVerificationSession
from app.core.security import hash_pin, verify_pin, validate_pin_format
from app.core.config import settings
from app.core.rate_limit import rate_limiter
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
        if pin_record.locked_until:
            lock_time = pin_record.locked_until
            if lock_time.tzinfo is None:
                lock_time = lock_time.replace(tzinfo=timezone.utc)
            now_utc = datetime.now(timezone.utc)

            if now_utc < lock_time:
                remaining = max(1, int((lock_time - now_utc).total_seconds() / 60))
                raise HTTPException(
                    status_code=status.HTTP_423_LOCKED,
                    detail=f"PIN is temporarily locked due to excessive failed attempts. Please retry in {remaining} minute(s)."
                )
            else:
                # Lockout period expired; automatically unlock and reset counter
                pin_record.is_locked = False
                pin_record.failed_attempts = 0
                pin_record.locked_until = None
                db.commit()
        else:
            pin_record.is_locked = False
            pin_record.failed_attempts = 0
            db.commit()


def setup_pin(db: Session, user_id: int, pin: str, username: str, ip_address: Optional[str] = None) -> bool:
    """Set up initial security PIN after validating structural format."""
    validate_pin_format(pin)

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

    # Brute-force rate limit check
    rate_limiter.check(
        f"pin_attempts:{user_id}",
        limit=settings.RATE_LIMIT_PIN_PER_MINUTE,
        window_seconds=60,
        message="Too many PIN verification attempts. Please wait before retrying."
    )

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

    # Verification successful: reset failed attempt counters
    pin_record.failed_attempts = 0
    pin_record.last_verified_at = datetime.now(timezone.utc)
    db.commit()

    # Reset rate limit on success
    rate_limiter.reset(f"pin_attempts:{user_id}")

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
    """
    Change security PIN after validating current PIN.
    Immediately revokes all previous PIN verification session tokens.
    """
    verify_user_pin(db, user_id, current_pin, username, ip_address)
    validate_pin_format(new_pin)

    if current_pin.strip() == new_pin.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New PIN cannot be identical to the current PIN."
        )

    pin_record = get_or_create_pin_record(db, user_id)
    pin_record.hashed_pin = hash_pin(new_pin)
    pin_record.failed_attempts = 0
    pin_record.is_locked = False
    pin_record.locked_until = None
    pin_record.last_verified_at = datetime.now(timezone.utc)

    # Invalidate all prior PIN verification sessions for this user
    db.query(PinVerificationSession).filter(
        PinVerificationSession.admin_user_id == user_id,
        PinVerificationSession.revoked_at.is_(None)
    ).update({"revoked_at": datetime.now(timezone.utc)})

    db.commit()

    log_audit_event(
        db=db,
        event_type="PIN_CHANGED",
        user_id=user_id,
        username=username,
        status="SUCCESS",
        details={"message": "Security PIN successfully updated; prior verification sessions invalidated"},
        ip_address=ip_address
    )
    return True


def revoke_pin_verification_sessions(db: Session, user_id: int) -> int:
    """Manually revoke all active PIN verification sessions for an admin."""
    updated = db.query(PinVerificationSession).filter(
        PinVerificationSession.admin_user_id == user_id,
        PinVerificationSession.revoked_at.is_(None)
    ).update({"revoked_at": datetime.now(timezone.utc)})
    db.commit()
    return updated


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

