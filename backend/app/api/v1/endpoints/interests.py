from typing import List
from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user import User
from app.schemas.interest import InterestCreate, InterestUpdate, InterestPatch, InterestOut
from app.api.deps import require_pin_verification
from app.services.profile_service import ProfileService

router = APIRouter()


def get_profile_service(db: Session = Depends(get_db)) -> ProfileService:
    return ProfileService(db)


@router.get("", response_model=List[InterestOut])
def list_interests(
    include_hidden: bool = False,
    service: ProfileService = Depends(get_profile_service)
):
    """Retrieve interests ordered by display order and name. Returns empty array if none exist."""
    return service.list_interests(include_hidden=include_hidden)


@router.get("/{interest_id}", response_model=InterestOut)
def get_interest(
    interest_id: int,
    service: ProfileService = Depends(get_profile_service)
):
    """Retrieve a single interest by ID."""
    return service.get_interest(interest_id)


@router.post("", response_model=InterestOut, status_code=status.HTTP_201_CREATED)
def create_interest(
    data: InterestCreate,
    request: Request,
    current_user: User = Depends(require_pin_verification),
    service: ProfileService = Depends(get_profile_service)
):
    """
    Create a new interest.
    Requires admin privileges and PIN authorization.
    """
    client_ip = request.client.host if request.client else "unknown"
    return service.create_interest(data, current_user, client_ip)


@router.put("/{interest_id}", response_model=InterestOut)
def update_interest(
    interest_id: int,
    data: InterestUpdate,
    request: Request,
    current_user: User = Depends(require_pin_verification),
    service: ProfileService = Depends(get_profile_service)
):
    """
    Update an existing interest.
    Requires admin privileges and PIN authorization.
    """
    client_ip = request.client.host if request.client else "unknown"
    return service.update_interest(interest_id, data, current_user, client_ip)


@router.patch("/{interest_id}", response_model=InterestOut)
def patch_interest(
    interest_id: int,
    data: InterestPatch,
    request: Request,
    current_user: User = Depends(require_pin_verification),
    service: ProfileService = Depends(get_profile_service)
):
    """
    Partially update an interest.
    Requires admin privileges and PIN authorization.
    """
    client_ip = request.client.host if request.client else "unknown"
    return service.patch_interest(interest_id, data, current_user, client_ip)


@router.delete("/{interest_id}")
def delete_interest(
    interest_id: int,
    request: Request,
    current_user: User = Depends(require_pin_verification),
    service: ProfileService = Depends(get_profile_service)
):
    """
    Delete an interest.
    Requires admin privileges and PIN authorization.
    """
    client_ip = request.client.host if request.client else "unknown"
    return service.delete_interest(interest_id, current_user, client_ip)
