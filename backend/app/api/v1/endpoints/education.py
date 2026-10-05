from typing import List
from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user import User
from app.schemas.education import EducationCreate, EducationUpdate, EducationPatch, EducationOut
from app.api.deps import require_pin_verification
from app.services.profile_service import ProfileService

router = APIRouter()


def get_profile_service(db: Session = Depends(get_db)) -> ProfileService:
    return ProfileService(db)


@router.get("", response_model=List[EducationOut])
def list_education(service: ProfileService = Depends(get_profile_service)):
    """Retrieve all education records ordered chronologically / by user preference."""
    return service.list_education()


@router.get("/{education_id}", response_model=EducationOut)
def get_education_item(
    education_id: int,
    service: ProfileService = Depends(get_profile_service)
):
    """Retrieve single education record."""
    return service.get_education(education_id)


@router.post("", response_model=EducationOut, status_code=status.HTTP_201_CREATED)
def create_education(
    edu_data: EducationCreate,
    request: Request,
    current_user: User = Depends(require_pin_verification),
    service: ProfileService = Depends(get_profile_service)
):
    """
    Create a new education record.
    Requires admin privileges and PIN authorization.
    """
    client_ip = request.client.host if request.client else "unknown"
    return service.create_education(edu_data, current_user, client_ip)


@router.put("/{education_id}", response_model=EducationOut)
def update_education(
    education_id: int,
    edu_data: EducationUpdate,
    request: Request,
    current_user: User = Depends(require_pin_verification),
    service: ProfileService = Depends(get_profile_service)
):
    """
    Update an existing education record.
    Requires admin privileges and PIN authorization.
    """
    client_ip = request.client.host if request.client else "unknown"
    return service.update_education(education_id, edu_data, current_user, client_ip)


@router.patch("/{education_id}", response_model=EducationOut)
def patch_education(
    education_id: int,
    edu_data: EducationPatch,
    request: Request,
    current_user: User = Depends(require_pin_verification),
    service: ProfileService = Depends(get_profile_service)
):
    """
    Partially update an education record.
    Requires admin privileges and PIN authorization.
    """
    client_ip = request.client.host if request.client else "unknown"
    return service.patch_education(education_id, edu_data, current_user, client_ip)


@router.delete("/{education_id}")
def delete_education(
    education_id: int,
    request: Request,
    current_user: User = Depends(require_pin_verification),
    service: ProfileService = Depends(get_profile_service)
):
    """
    Delete an education record.
    Requires admin privileges and PIN authorization.
    """
    client_ip = request.client.host if request.client else "unknown"
    return service.delete_education(education_id, current_user, client_ip)
