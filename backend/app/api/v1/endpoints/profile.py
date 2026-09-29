import json
from datetime import datetime, timezone
from typing import List, Optional
from fastapi import APIRouter, Depends, Request, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.profile import Profile, ProfileEmail
from app.models.user import User
from app.schemas.profile import (
    ProfileOut,
    ProfileUpdate,
    ProfileEmailOut,
    ProfileEmailCreate,
    ProfileEmailUpdate
)
from app.api.deps import require_pin_verification
from app.services.audit_service import log_audit_event, record_content_revision

router = APIRouter()


def get_or_create_profile(db: Session) -> Profile:
    """Retrieve existing profile or initialize an empty template."""
    profile = db.query(Profile).first()
    if not profile:
        profile = Profile(
            name=None,
            email_ids="[]",
            mobile_number=None,
            linkedin=None,
            about=None
        )
        db.add(profile)
        db.commit()
        db.refresh(profile)
    return profile


def profile_to_dict(profile: Profile) -> dict:
    emails = []
    try:
        emails = json.loads(profile.email_ids) if profile.email_ids else []
    except Exception:
        emails = []

    email_objs = []
    if hasattr(profile, "emails") and profile.emails:
        email_objs = [
            ProfileEmailOut(
                id=e.id,
                profile_id=e.profile_id,
                email=e.email,
                label=e.label,
                is_primary=e.is_primary,
                display_order=e.display_order,
                created_at=e.created_at,
                updated_at=e.updated_at
            )
            for e in sorted(profile.emails, key=lambda x: x.display_order)
        ]

    is_empty = not any([
        profile.name,
        emails,
        profile.mobile_number,
        profile.linkedin,
        profile.about
    ])

    return {
        "id": profile.id,
        "name": profile.name,
        "email_ids": emails,
        "emails": email_objs if email_objs else None,
        "mobile_number": profile.mobile_number,
        "linkedin": profile.linkedin,
        "about": profile.about,
        "is_empty": is_empty,
        "created_at": profile.created_at,
        "updated_at": profile.updated_at
    }


def sync_profile_email_ids(db: Session, profile: Profile):
    """Sync profile_emails table into the profile.email_ids JSON list."""
    current_emails = db.query(ProfileEmail).filter(ProfileEmail.profile_id == profile.id).order_by(ProfileEmail.display_order).all()
    profile.email_ids = json.dumps([e.email for e in current_emails])
    profile.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(profile)


@router.get("", response_model=ProfileOut)
def get_public_profile(db: Session = Depends(get_db)):
    """Retrieve public profile information. Displays safe empty states if unpopulated."""
    profile = get_or_create_profile(db)
    return profile_to_dict(profile)


@router.get("/emails", response_model=List[ProfileEmailOut])
def list_profile_emails(db: Session = Depends(get_db)):
    """Retrieve all associated profile email addresses."""
    profile = get_or_create_profile(db)
    emails = db.query(ProfileEmail).filter(ProfileEmail.profile_id == profile.id).order_by(ProfileEmail.display_order).all()
    return emails


@router.post("/emails", response_model=ProfileEmailOut, status_code=status.HTTP_201_CREATED)
def add_profile_email(
    email_data: ProfileEmailCreate,
    request: Request,
    current_user: User = Depends(require_pin_verification),
    db: Session = Depends(get_db)
):
    """Add a new email record to the profile. Requires PIN verification."""
    profile = get_or_create_profile(db)

    # Check for duplicate email in this profile
    existing = db.query(ProfileEmail).filter(
        ProfileEmail.profile_id == profile.id,
        ProfileEmail.email == email_data.email
    ).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered in profile.")

    # If is_primary, unset any existing primary email
    if email_data.is_primary:
        db.query(ProfileEmail).filter(
            ProfileEmail.profile_id == profile.id,
            ProfileEmail.is_primary == True
        ).update({"is_primary": False})

    new_email = ProfileEmail(
        profile_id=profile.id,
        email=email_data.email,
        label=email_data.label,
        is_primary=email_data.is_primary,
        display_order=email_data.display_order
    )
    db.add(new_email)
    db.commit()
    db.refresh(new_email)

    sync_profile_email_ids(db, profile)

    client_ip = request.client.host if request.client else "unknown"
    log_audit_event(
        db=db,
        event_type="EMAIL_ADDED",
        status="SUCCESS",
        user_id=current_user.id,
        username=current_user.username,
        details={"email_id": new_email.id, "email": new_email.email},
        ip_address=client_ip
    )
    return new_email


@router.put("/emails/{email_id}", response_model=ProfileEmailOut)
def update_profile_email(
    email_id: int,
    email_data: ProfileEmailUpdate,
    request: Request,
    current_user: User = Depends(require_pin_verification),
    db: Session = Depends(get_db)
):
    """Update an existing profile email record. Requires PIN verification."""
    profile = get_or_create_profile(db)
    email_rec = db.query(ProfileEmail).filter(
        ProfileEmail.id == email_id,
        ProfileEmail.profile_id == profile.id
    ).first()
    if not email_rec:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile email record not found.")

    if email_data.email is not None:
        email_rec.email = email_data.email
    if email_data.label is not None:
        email_rec.label = email_data.label
    if email_data.display_order is not None:
        email_rec.display_order = email_data.display_order
    if email_data.is_primary is not None:
        if email_data.is_primary:
            db.query(ProfileEmail).filter(
                ProfileEmail.profile_id == profile.id,
                ProfileEmail.id != email_id,
                ProfileEmail.is_primary == True
            ).update({"is_primary": False})
        email_rec.is_primary = email_data.is_primary

    email_rec.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(email_rec)

    sync_profile_email_ids(db, profile)

    client_ip = request.client.host if request.client else "unknown"
    log_audit_event(
        db=db,
        event_type="EMAIL_UPDATED",
        status="SUCCESS",
        user_id=current_user.id,
        username=current_user.username,
        details={"email_id": email_rec.id, "email": email_rec.email},
        ip_address=client_ip
    )
    return email_rec


@router.delete("/emails/{email_id}")
def delete_profile_email(
    email_id: int,
    request: Request,
    current_user: User = Depends(require_pin_verification),
    db: Session = Depends(get_db)
):
    """Delete a profile email record. Requires PIN verification."""
    profile = get_or_create_profile(db)
    email_rec = db.query(ProfileEmail).filter(
        ProfileEmail.id == email_id,
        ProfileEmail.profile_id == profile.id
    ).first()
    if not email_rec:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile email record not found.")

    deleted_email_addr = email_rec.email
    db.delete(email_rec)
    db.commit()

    sync_profile_email_ids(db, profile)

    client_ip = request.client.host if request.client else "unknown"
    log_audit_event(
        db=db,
        event_type="EMAIL_DELETED",
        status="SUCCESS",
        user_id=current_user.id,
        username=current_user.username,
        details={"email_id": email_id, "email": deleted_email_addr},
        ip_address=client_ip
    )
    return {"success": True, "message": f"Email {deleted_email_addr} deleted successfully."}


@router.put("", response_model=ProfileOut)
def update_profile(
    profile_data: ProfileUpdate,
    request: Request,
    current_user: User = Depends(require_pin_verification),
    db: Session = Depends(get_db)
):
    """
    Update profile details.
    Protected by PIN verification via X-Action-PIN header.
    Creates an immutable content revision and audit log.
    """
    profile = get_or_create_profile(db)
    previous_snapshot = profile_to_dict(profile)

    # Apply updates
    profile.name = profile_data.name.strip() if profile_data.name else None
    profile.email_ids = json.dumps(profile_data.email_ids)
    profile.mobile_number = profile_data.mobile_number.strip() if profile_data.mobile_number else None
    profile.linkedin = profile_data.linkedin.strip() if profile_data.linkedin else None
    profile.about = profile_data.about.strip() if profile_data.about else None
    profile.updated_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(profile)

    current_snapshot = profile_to_dict(profile)

    # Record Content Revision
    record_content_revision(
        db=db,
        entity_name="profile",
        action="UPDATE",
        entity_id=str(profile.id),
        editor_username=current_user.username,
        change_summary="Profile details updated via CMS",
        previous_snapshot=previous_snapshot,
        current_snapshot=current_snapshot
    )

    # Log Audit Event
    client_ip = request.client.host if request.client else "unknown"
    log_audit_event(
        db=db,
        event_type="PROFILE_UPDATED",
        status="SUCCESS",
        user_id=current_user.id,
        username=current_user.username,
        details={"profile_id": profile.id},
        ip_address=client_ip
    )

    return current_snapshot


@router.patch("", response_model=ProfileOut)
def patch_profile(
    profile_data: ProfileUpdate,
    request: Request,
    current_user: User = Depends(require_pin_verification),
    db: Session = Depends(get_db)
):
    """
    Partially update profile details.
    Protected by PIN verification via X-Action-PIN header.
    Creates an immutable content revision and audit log.
    """
    profile = get_or_create_profile(db)
    previous_snapshot = profile_to_dict(profile)

    if profile_data.name is not None:
        profile.name = profile_data.name.strip() if profile_data.name else None
    if profile_data.email_ids is not None:
        profile.email_ids = json.dumps(profile_data.email_ids)
    if profile_data.mobile_number is not None:
        profile.mobile_number = profile_data.mobile_number.strip() if profile_data.mobile_number else None
    if profile_data.linkedin is not None:
        profile.linkedin = profile_data.linkedin.strip() if profile_data.linkedin else None
    if profile_data.about is not None:
        profile.about = profile_data.about.strip() if profile_data.about else None

    profile.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(profile)

    current_snapshot = profile_to_dict(profile)

    record_content_revision(
        db=db,
        entity_name="profile",
        action="PATCH",
        entity_id=str(profile.id),
        editor_username=current_user.username,
        change_summary="Profile details patched via CMS",
        previous_snapshot=previous_snapshot,
        current_snapshot=current_snapshot
    )

    client_ip = request.client.host if request.client else "unknown"
    log_audit_event(
        db=db,
        event_type="PROFILE_PATCHED",
        status="SUCCESS",
        user_id=current_user.id,
        username=current_user.username,
        details={"profile_id": profile.id},
        ip_address=client_ip
    )

    return current_snapshot
