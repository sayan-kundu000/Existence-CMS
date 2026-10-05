from typing import List
from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user import User
from app.schemas.experience import ExperienceCreate, ExperienceUpdate, ExperiencePatch, ExperienceOut
from app.api.deps import require_pin_verification
from app.services.profile_service import ProfileService

router = APIRouter()


def get_profile_service(db: Session = Depends(get_db)) -> ProfileService:
    return ProfileService(db)


@router.get("", response_model=List[ExperienceOut])
def list_experience(service: ProfileService = Depends(get_profile_service)):
    """Retrieve all work experience records ordered chronologically."""
    return service.list_experience()


@router.get("/{experience_id}", response_model=ExperienceOut)
def get_experience_item(
    experience_id: int,
    service: ProfileService = Depends(get_profile_service)
):
    """Retrieve single work experience item."""
    return service.get_experience(experience_id)


@router.post("", response_model=ExperienceOut, status_code=status.HTTP_201_CREATED)
def create_experience(
    exp_data: ExperienceCreate,
    request: Request,
    current_user: User = Depends(require_pin_verification),
    service: ProfileService = Depends(get_profile_service)
):
    """
    Create a new work experience record.
    Requires admin privileges and PIN authorization.
    """
    client_ip = request.client.host if request.client else "unknown"
    return service.create_experience(exp_data, current_user, client_ip)


@router.put("/{experience_id}", response_model=ExperienceOut)
def update_experience(
    experience_id: int,
    exp_data: ExperienceUpdate,
    request: Request,
    current_user: User = Depends(require_pin_verification),
    service: ProfileService = Depends(get_profile_service)
):
    """
    Update an existing work experience record.
    Requires admin privileges and PIN authorization.
    """
    client_ip = request.client.host if request.client else "unknown"
    return service.update_experience(experience_id, exp_data, current_user, client_ip)


@router.patch("/{experience_id}", response_model=ExperienceOut)
def patch_experience(
    experience_id: int,
    exp_data: ExperiencePatch,
    request: Request,
    current_user: User = Depends(require_pin_verification),
    service: ProfileService = Depends(get_profile_service)
):
    """
    Partially update a work experience record.
    Requires admin privileges and PIN authorization.
    """
    client_ip = request.client.host if request.client else "unknown"
    return service.patch_experience(experience_id, exp_data, current_user, client_ip)


@router.delete("/{experience_id}")
def delete_experience(
    experience_id: int,
    request: Request,
    current_user: User = Depends(require_pin_verification),
    service: ProfileService = Depends(get_profile_service)
):
    """
    Delete a work experience record.
    Requires admin privileges and PIN authorization.
    """
    client_ip = request.client.host if request.client else "unknown"
    return service.delete_experience(experience_id, current_user, client_ip)
