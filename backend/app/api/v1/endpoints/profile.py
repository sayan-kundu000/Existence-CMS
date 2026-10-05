from typing import List, Optional
from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.profile import Profile
from app.models.user import User
from app.schemas.profile import (
    ProfileOut,
    ProfileUpdate,
    ProfileEmailOut,
    ProfileEmailCreate,
    ProfileEmailUpdate,
    ProfileCompletenessOut,
    ConsolidatedPublicProfile
)
from app.api.deps import require_pin_verification, get_current_user
from app.services.profile_service import ProfileService

router = APIRouter()


def get_profile_service(db: Session = Depends(get_db)) -> ProfileService:
    return ProfileService(db)


def get_or_create_profile(db: Session) -> Profile:
    return ProfileService(db).get_or_create_profile()


def profile_to_dict(profile: Profile, public: bool = False) -> dict:
    import json
    emails = []
    try:
        emails = json.loads(profile.email_ids) if profile.email_ids else []
    except Exception:
        emails = []

    raw_email_records = profile.emails or []
    if public:
        filtered_emails = [e for e in raw_email_records if getattr(e, "is_public", True)]
    else:
        filtered_emails = raw_email_records

    email_objs = [
        {
            "id": e.id,
            "profile_id": e.profile_id,
            "email": e.email,
            "label": e.label,
            "is_primary": e.is_primary,
            "is_public": getattr(e, "is_public", True),
            "display_order": e.display_order,
            "created_at": e.created_at,
            "updated_at": e.updated_at
        }
        for e in filtered_emails
    ]

    is_empty = (
        not profile.name and
        not profile.about and
        not profile.mobile_number and
        not profile.linkedin and
        len(emails) == 0
    )

    return {
        "id": profile.id,
        "name": profile.name,
        "about": profile.about,
        "mobile_number": profile.mobile_number,
        "linkedin": profile.linkedin,
        "email_ids": emails,
        "emails": email_objs,
        "is_empty": is_empty,
        "created_at": profile.created_at,
        "updated_at": profile.updated_at
    }


# -----------------------------------------------------------------------------
# Public & Consolidated Endpoints
# -----------------------------------------------------------------------------

@router.get("", response_model=ProfileOut)
def get_profile(
    public: bool = False,
    service: ProfileService = Depends(get_profile_service)
):
    """
    Retrieve core profile information.
    When public=True, private emails and internal metadata are filtered out.
    """
    return service.get_profile(public=public)


@router.get("/public", response_model=ConsolidatedPublicProfile)
def get_consolidated_public_profile(
    service: ProfileService = Depends(get_profile_service)
):
    """
    Authoritative consolidated public portfolio endpoint.
    Performs single eager-loaded database query across Profile, Education, Experience,
    Skills, Hobbies, and Interests, strictly eliminating N+1 network requests.
    Excludes all authentication metadata, PIN hashes, passwords, audit logs, and revisions.
    """
    return service.get_consolidated_public_profile()


@router.get("/completeness", response_model=ProfileCompletenessOut)
def get_profile_completeness(
    service: ProfileService = Depends(get_profile_service)
):
    """
    Evaluates authoritative completion across 9 domain dimensions:
    personal_info, about, emails, contact, education, experience, skills, hobbies, interests.
    """
    return service.calculate_completeness()


# -----------------------------------------------------------------------------
# Core Profile Mutations (PIN-Protected)
# -----------------------------------------------------------------------------

@router.put("", response_model=ProfileOut)
def update_profile(
    profile_data: ProfileUpdate,
    request: Request,
    current_user: User = Depends(require_pin_verification),
    service: ProfileService = Depends(get_profile_service)
):
    """
    Update core profile details.
    Protected by PIN authorization (X-Action-PIN header or session token).
    Creates an immutable content revision snapshot and security audit event.
    """
    client_ip = request.client.host if request.client else "unknown"
    return service.update_profile(profile_data, current_user, client_ip)


@router.patch("", response_model=ProfileOut)
def patch_profile(
    profile_data: ProfileUpdate,
    request: Request,
    current_user: User = Depends(require_pin_verification),
    service: ProfileService = Depends(get_profile_service)
):
    """
    Partially update core profile details.
    Protected by PIN authorization (X-Action-PIN header or session token).
    Creates an immutable content revision snapshot and security audit event.
    """
    client_ip = request.client.host if request.client else "unknown"
    return service.patch_profile(profile_data, current_user, client_ip)


# -----------------------------------------------------------------------------
# Profile Email Management
# -----------------------------------------------------------------------------

@router.get("/emails", response_model=List[ProfileEmailOut])
def list_profile_emails(
    public_only: bool = False,
    service: ProfileService = Depends(get_profile_service)
):
    """Retrieve all profile email records. Optional public_only filtering."""
    return service.list_emails(public_only=public_only)


@router.post("/emails", response_model=ProfileEmailOut, status_code=status.HTTP_201_CREATED)
def add_profile_email(
    email_data: ProfileEmailCreate,
    request: Request,
    current_user: User = Depends(require_pin_verification),
    service: ProfileService = Depends(get_profile_service)
):
    """
    Add a new email record to the profile.
    Requires PIN authorization.
    """
    client_ip = request.client.host if request.client else "unknown"
    return service.add_email(email_data, current_user, client_ip)


@router.put("/emails/{email_id}", response_model=ProfileEmailOut)
def update_profile_email(
    email_id: int,
    email_data: ProfileEmailUpdate,
    request: Request,
    current_user: User = Depends(require_pin_verification),
    service: ProfileService = Depends(get_profile_service)
):
    """
    Update profile email record.
    Requires PIN authorization.
    """
    client_ip = request.client.host if request.client else "unknown"
    return service.update_email(email_id, email_data, current_user, client_ip)


@router.delete("/emails/{email_id}")
def delete_profile_email(
    email_id: int,
    request: Request,
    current_user: User = Depends(require_pin_verification),
    service: ProfileService = Depends(get_profile_service)
):
    """
    Delete a profile email record.
    Enforces business rules: Cannot delete the only registered email.
    Requires PIN authorization.
    """
    client_ip = request.client.host if request.client else "unknown"
    return service.delete_email(email_id, current_user, client_ip)


@router.post("/emails/{email_id}/primary", response_model=ProfileEmailOut)
def set_primary_email(
    email_id: int,
    request: Request,
    current_user: User = Depends(require_pin_verification),
    service: ProfileService = Depends(get_profile_service)
):
    """
    Sets target email as primary, safely demoting old primary inside an atomic transaction.
    Requires PIN authorization.
    """
    client_ip = request.client.host if request.client else "unknown"
    return service.set_primary_email(email_id, current_user, client_ip)
