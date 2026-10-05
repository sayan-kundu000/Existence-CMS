from typing import List
from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user import User
from app.schemas.hobby import HobbyCreate, HobbyUpdate, HobbyPatch, HobbyOut
from app.api.deps import require_pin_verification
from app.services.profile_service import ProfileService

router = APIRouter()


def get_profile_service(db: Session = Depends(get_db)) -> ProfileService:
    return ProfileService(db)


@router.get("", response_model=List[HobbyOut])
def list_hobbies(
    include_hidden: bool = False,
    service: ProfileService = Depends(get_profile_service)
):
    """Retrieve hobbies ordered by display order and name. Returns empty array if none exist."""
    return service.list_hobbies(include_hidden=include_hidden)


@router.get("/{hobby_id}", response_model=HobbyOut)
def get_hobby(
    hobby_id: int,
    service: ProfileService = Depends(get_profile_service)
):
    """Retrieve a single hobby by ID."""
    return service.get_hobby(hobby_id)


@router.post("", response_model=HobbyOut, status_code=status.HTTP_201_CREATED)
def create_hobby(
    data: HobbyCreate,
    request: Request,
    current_user: User = Depends(require_pin_verification),
    service: ProfileService = Depends(get_profile_service)
):
    """
    Create a new hobby.
    Requires admin privileges and PIN authorization.
    """
    client_ip = request.client.host if request.client else "unknown"
    return service.create_hobby(data, current_user, client_ip)


@router.put("/{hobby_id}", response_model=HobbyOut)
def update_hobby(
    hobby_id: int,
    data: HobbyUpdate,
    request: Request,
    current_user: User = Depends(require_pin_verification),
    service: ProfileService = Depends(get_profile_service)
):
    """
    Update an existing hobby.
    Requires admin privileges and PIN authorization.
    """
    client_ip = request.client.host if request.client else "unknown"
    return service.update_hobby(hobby_id, data, current_user, client_ip)


@router.patch("/{hobby_id}", response_model=HobbyOut)
def patch_hobby(
    hobby_id: int,
    data: HobbyPatch,
    request: Request,
    current_user: User = Depends(require_pin_verification),
    service: ProfileService = Depends(get_profile_service)
):
    """
    Partially update a hobby.
    Requires admin privileges and PIN authorization.
    """
    client_ip = request.client.host if request.client else "unknown"
    return service.patch_hobby(hobby_id, data, current_user, client_ip)


@router.delete("/{hobby_id}")
def delete_hobby(
    hobby_id: int,
    request: Request,
    current_user: User = Depends(require_pin_verification),
    service: ProfileService = Depends(get_profile_service)
):
    """
    Delete a hobby.
    Requires admin privileges and PIN authorization.
    """
    client_ip = request.client.host if request.client else "unknown"
    return service.delete_hobby(hobby_id, current_user, client_ip)
