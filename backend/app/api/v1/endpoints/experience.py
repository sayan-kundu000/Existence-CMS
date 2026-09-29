from typing import List
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.experience import Experience
from app.models.user import User
from app.schemas.experience import ExperienceCreate, ExperienceUpdate, ExperiencePatch, ExperienceOut
from app.utils.date_helpers import validate_date_order
from app.api.deps import require_pin_verification
from app.services.audit_service import log_audit_event, record_content_revision

router = APIRouter()


def exp_to_dict(exp: Experience) -> dict:
    return {
        "id": exp.id,
        "role": exp.role,
        "employer": exp.employer,
        "work_mode": exp.work_mode,
        "location": exp.location,
        "starting_month_year": exp.starting_month_year,
        "ending_month_year": exp.ending_month_year,
        "currently_working": exp.currently_working,
        "ordering": exp.ordering,
        "created_at": exp.created_at,
        "updated_at": exp.updated_at
    }


@router.get("", response_model=List[ExperienceOut])
def list_experience(db: Session = Depends(get_db)):
    """Retrieve all work experience records."""
    records = db.query(Experience).order_by(Experience.ordering.asc(), Experience.created_at.desc()).all()
    return records


@router.get("/{experience_id}", response_model=ExperienceOut)
def get_experience_item(experience_id: int, db: Session = Depends(get_db)):
    """Retrieve single work experience item."""
    item = db.query(Experience).filter(Experience.id == experience_id).first()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Experience record not found")
    return item


@router.post("", response_model=ExperienceOut, status_code=status.HTTP_201_CREATED)
def create_experience(
    exp_data: ExperienceCreate,
    request: Request,
    current_user: User = Depends(require_pin_verification),
    db: Session = Depends(get_db)
):
    """
    Create a new work experience record.
    Requires admin privileges and PIN verification via X-Action-PIN header.
    """
    new_exp = Experience(
        role=exp_data.role,
        employer=exp_data.employer,
        work_mode=exp_data.work_mode,
        location=exp_data.location,
        starting_month_year=exp_data.starting_month_year,
        ending_month_year=exp_data.ending_month_year,
        currently_working=exp_data.currently_working,
        ordering=exp_data.ordering
    )
    db.add(new_exp)
    db.commit()
    db.refresh(new_exp)

    curr_dict = exp_to_dict(new_exp)

    record_content_revision(
        db=db,
        entity_name="experience",
        action="CREATE",
        entity_id=str(new_exp.id),
        editor_username=current_user.username,
        change_summary=f"Added experience: {new_exp.role} at {new_exp.employer}",
        previous_snapshot=None,
        current_snapshot=curr_dict
    )

    client_ip = request.client.host if request.client else "unknown"
    log_audit_event(
        db=db,
        event_type="EXPERIENCE_CREATED",
        status="SUCCESS",
        user_id=current_user.id,
        username=current_user.username,
        details={"experience_id": new_exp.id, "role": new_exp.role, "employer": new_exp.employer},
        ip_address=client_ip
    )

    return new_exp


@router.put("/{experience_id}", response_model=ExperienceOut)
def update_experience(
    experience_id: int,
    exp_data: ExperienceUpdate,
    request: Request,
    current_user: User = Depends(require_pin_verification),
    db: Session = Depends(get_db)
):
    """
    Update an existing work experience record.
    Requires admin privileges and PIN verification via X-Action-PIN header.
    """
    item = db.query(Experience).filter(Experience.id == experience_id).first()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Experience record not found")

    prev_dict = exp_to_dict(item)

    item.role = exp_data.role
    item.employer = exp_data.employer
    item.work_mode = exp_data.work_mode
    item.location = exp_data.location
    item.starting_month_year = exp_data.starting_month_year
    item.ending_month_year = exp_data.ending_month_year
    item.currently_working = exp_data.currently_working
    item.ordering = exp_data.ordering
    item.updated_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(item)

    curr_dict = exp_to_dict(item)

    record_content_revision(
        db=db,
        entity_name="experience",
        action="UPDATE",
        entity_id=str(item.id),
        editor_username=current_user.username,
        change_summary=f"Updated experience: {item.role} at {item.employer}",
        previous_snapshot=prev_dict,
        current_snapshot=curr_dict
    )

    client_ip = request.client.host if request.client else "unknown"
    log_audit_event(
        db=db,
        event_type="EXPERIENCE_UPDATED",
        status="SUCCESS",
        user_id=current_user.id,
        username=current_user.username,
        details={"experience_id": item.id},
        ip_address=client_ip
    )

    return item


@router.patch("/{experience_id}", response_model=ExperienceOut)
def patch_experience(
    experience_id: int,
    exp_data: ExperiencePatch,
    request: Request,
    current_user: User = Depends(require_pin_verification),
    db: Session = Depends(get_db)
):
    """
    Partially update an existing work experience record.
    Requires admin privileges and PIN verification via X-Action-PIN header.
    """
    item = db.query(Experience).filter(Experience.id == experience_id).first()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Experience record not found")

    prev_dict = exp_to_dict(item)

    # Prospective state
    new_role = exp_data.role if exp_data.role is not None else item.role
    new_employer = exp_data.employer if exp_data.employer is not None else item.employer
    new_mode = exp_data.work_mode if exp_data.work_mode is not None else item.work_mode
    new_location = exp_data.location if exp_data.location is not None else item.location
    new_start = exp_data.starting_month_year if exp_data.starting_month_year is not None else item.starting_month_year
    new_working = exp_data.currently_working if exp_data.currently_working is not None else item.currently_working
    new_end = exp_data.ending_month_year if exp_data.ending_month_year is not None else item.ending_month_year
    new_ordering = exp_data.ordering if exp_data.ordering is not None else item.ordering

    # 1. Conditional Location Rule
    if new_mode in ["On-site", "Hybrid"]:
        if not new_location or not new_location.strip() or new_location.strip() == "Remote":
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Location is required when work mode is {new_mode}."
            )
    elif new_mode == "Remote":
        new_location = "Remote"

    # 2. Conditional Ending Date Rule
    if new_working:
        new_end = None
    else:
        if not new_end or not new_end.strip():
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Ending Month & Year is required when not currently working."
            )

    # 3. Date Precedence
    if new_end:
        try:
            validate_date_order(new_start, new_end)
        except ValueError as ve:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=str(ve)
            )

    item.role = new_role
    item.employer = new_employer
    item.work_mode = new_mode
    item.location = new_location
    item.starting_month_year = new_start
    item.ending_month_year = new_end
    item.currently_working = new_working
    item.ordering = new_ordering
    item.updated_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(item)

    curr_dict = exp_to_dict(item)

    record_content_revision(
        db=db,
        entity_name="experience",
        action="PATCH",
        entity_id=str(item.id),
        editor_username=current_user.username,
        change_summary=f"Patched experience: {item.role} at {item.employer}",
        previous_snapshot=prev_dict,
        current_snapshot=curr_dict
    )

    client_ip = request.client.host if request.client else "unknown"
    log_audit_event(
        db=db,
        event_type="EXPERIENCE_PATCHED",
        status="SUCCESS",
        user_id=current_user.id,
        username=current_user.username,
        details={"experience_id": item.id},
        ip_address=client_ip
    )

    return item


@router.delete("/{experience_id}", status_code=status.HTTP_200_OK)
def delete_experience(
    experience_id: int,
    request: Request,
    current_user: User = Depends(require_pin_verification),
    db: Session = Depends(get_db)
):
    """
    Delete a work experience record.
    Requires admin privileges and PIN verification via X-Action-PIN header.
    """
    item = db.query(Experience).filter(Experience.id == experience_id).first()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Experience record not found")

    prev_dict = exp_to_dict(item)

    db.delete(item)
    db.commit()

    record_content_revision(
        db=db,
        entity_name="experience",
        action="DELETE",
        entity_id=str(experience_id),
        editor_username=current_user.username,
        change_summary=f"Deleted experience ID {experience_id}",
        previous_snapshot=prev_dict,
        current_snapshot=None
    )

    client_ip = request.client.host if request.client else "unknown"
    log_audit_event(
        db=db,
        event_type="EXPERIENCE_DELETED",
        status="SUCCESS",
        user_id=current_user.id,
        username=current_user.username,
        details={"experience_id": experience_id},
        ip_address=client_ip
    )

    return {"success": True, "message": "Experience record deleted"}
