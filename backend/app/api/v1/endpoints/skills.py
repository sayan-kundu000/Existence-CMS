from typing import List, Optional
from fastapi import APIRouter, Depends, Request, status, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user import User
from app.schemas.skill import (
    SkillCreate,
    SkillUpdate,
    SkillPatch,
    SkillOut,
    SkillRatingLevel,
    SkillCategoriesOut,
    SkillReorderItem
)
from app.api.deps import require_pin_verification
from app.services.skill_service import SkillService

router = APIRouter()


def get_skill_service(db: Session = Depends(get_db)) -> SkillService:
    return SkillService(db)


@router.get("/categories", response_model=SkillCategoriesOut)
def get_skill_categories(service: SkillService = Depends(get_skill_service)):
    """
    Retrieve the 17 canonical skill categories.
    Users can assign one or more categories to each skill.
    """
    return SkillCategoriesOut(categories=service.get_categories())


@router.get("/levels", response_model=List[SkillRatingLevel])
def get_rating_levels(service: SkillService = Depends(get_skill_service)):
    """
    Retrieve canonical 7-level skill rating metadata.
    Provides canonical level names (Beginner to Master), descriptions, and display orders.
    """
    return service.get_rating_levels()


@router.get("", response_model=List[SkillOut])
def list_skills(
    include_hidden: bool = Query(False, description="Include private/hidden skills (requires admin context)"),
    category: Optional[str] = Query(None, description="Filter by skill category"),
    domain: Optional[str] = Query(None, description="Filter by skill domain"),
    search: Optional[str] = Query(None, description="Search query across name, domain, category, or description"),
    rating: Optional[int] = Query(None, ge=1, le=7, description="Filter by exact 1-7 skill rating"),
    sort_by: Optional[str] = Query("rating", description="Sort by: 'rating' (descending), 'order', or 'name'"),
    service: SkillService = Depends(get_skill_service)
):
    """
    Retrieve skills ordered deterministically.
    Public view strictly excludes private/hidden skills without leaking unpublished data.
    """
    return service.list_skills(
        include_hidden=include_hidden,
        category=category,
        domain=domain,
        search=search,
        rating=rating,
        sort_by=sort_by or "order"
    )


@router.post("", response_model=SkillOut, status_code=status.HTTP_201_CREATED)
def create_skill(
    skill_data: SkillCreate,
    request: Request,
    current_user: User = Depends(require_pin_verification),
    service: SkillService = Depends(get_skill_service)
):
    """
    Create a new skill with exact 7-level rating.
    Requires administrative authentication and PIN verification.
    """
    client_ip = request.client.host if request.client else "unknown"
    return service.create_skill(skill_data, current_user, client_ip)


# Reorder endpoints placed BEFORE /{skill_id} to prevent path parameter collision
@router.patch("/reorder", status_code=status.HTTP_200_OK)
def patch_reorder_skills(
    items: List[SkillReorderItem],
    request: Request,
    current_user: User = Depends(require_pin_verification),
    service: SkillService = Depends(get_skill_service)
):
    """
    Reorder skills in bulk (PATCH convention).
    Executes transactionally and verifies all IDs.
    """
    client_ip = request.client.host if request.client else "unknown"
    return service.reorder_skills(items, current_user, client_ip)


@router.post("/reorder", status_code=status.HTTP_200_OK)
def post_reorder_skills(
    items: List[SkillReorderItem],
    request: Request,
    current_user: User = Depends(require_pin_verification),
    service: SkillService = Depends(get_skill_service)
):
    """
    Reorder skills in bulk (POST convention for backward compatibility).
    Executes transactionally and verifies all IDs.
    """
    client_ip = request.client.host if request.client else "unknown"
    return service.reorder_skills(items, current_user, client_ip)


@router.get("/{skill_id}", response_model=SkillOut)
def get_skill(
    skill_id: int,
    service: SkillService = Depends(get_skill_service)
):
    """Retrieve single skill item by ID."""
    return service.get_skill(skill_id)


@router.put("/{skill_id}", response_model=SkillOut)
def update_skill(
    skill_id: int,
    skill_data: SkillUpdate,
    request: Request,
    current_user: User = Depends(require_pin_verification),
    service: SkillService = Depends(get_skill_service)
):
    """
    Update an existing skill.
    Requires administrative authentication and PIN verification.
    """
    client_ip = request.client.host if request.client else "unknown"
    return service.update_skill(skill_id, skill_data, current_user, client_ip)


@router.patch("/{skill_id}", response_model=SkillOut)
def patch_skill(
    skill_id: int,
    skill_data: SkillPatch,
    request: Request,
    current_user: User = Depends(require_pin_verification),
    service: SkillService = Depends(get_skill_service)
):
    """
    Partially update an existing skill.
    Requires administrative authentication and PIN verification.
    """
    client_ip = request.client.host if request.client else "unknown"
    return service.patch_skill(skill_id, skill_data, current_user, client_ip)


@router.delete("/{skill_id}", status_code=status.HTTP_200_OK)
def delete_skill(
    skill_id: int,
    request: Request,
    current_user: User = Depends(require_pin_verification),
    service: SkillService = Depends(get_skill_service)
):
    """
    Delete a skill record safely.
    Requires administrative authentication and PIN verification.
    """
    client_ip = request.client.host if request.client else "unknown"
    return service.delete_skill(skill_id, current_user, client_ip)
