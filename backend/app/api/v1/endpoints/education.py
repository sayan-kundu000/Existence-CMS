from typing import List
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.education import Education
from app.models.user import User
from app.schemas.education import EducationCreate, EducationUpdate, EducationPatch, EducationOut
from app.utils.date_helpers import validate_date_order
from app.api.deps import require_pin_verification
from app.services.audit_service import log_audit_event, record_content_revision

router = APIRouter()


def edu_to_dict(edu: Education) -> dict:
    return {
        "id": edu.id,
        "level": edu.level,
        "stream": edu.stream,
        "institution": edu.institution,
        "starting_month_year": edu.starting_month_year,
        "ending_month_year": edu.ending_month_year,
        "currently_studying": edu.currently_studying,
        "ordering": edu.ordering,
        "created_at": edu.created_at,
        "updated_at": edu.updated_at
    }


@router.get("", response_model=List[EducationOut])
def list_education(db: Session = Depends(get_db)):
    """Retrieve all education records ordered by user preference."""
    records = db.query(Education).order_by(Education.ordering.asc(), Education.created_at.desc()).all()
    return records


@router.get("/{education_id}", response_model=EducationOut)
def get_education_item(education_id: int, db: Session = Depends(get_db)):
    """Retrieve single education record."""
    item = db.query(Education).filter(Education.id == education_id).first()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Education record not found")
    return item


@router.post("", response_model=EducationOut, status_code=status.HTTP_201_CREATED)
def create_education(
    edu_data: EducationCreate,
    request: Request,
    current_user: User = Depends(require_pin_verification),
    db: Session = Depends(get_db)
):
    """
    Create a new education record.
    Requires admin privileges and PIN verification via X-Action-PIN header.
    """
    new_edu = Education(
        level=edu_data.level,
        stream=edu_data.stream,
        institution=edu_data.institution,
        starting_month_year=edu_data.starting_month_year,
        ending_month_year=edu_data.ending_month_year,
        currently_studying=edu_data.currently_studying,
        ordering=edu_data.ordering
    )
    db.add(new_edu)
    db.commit()
    db.refresh(new_edu)

    curr_dict = edu_to_dict(new_edu)

    record_content_revision(
        db=db,
        entity_name="education",
        action="CREATE",
        entity_id=str(new_edu.id),
        editor_username=current_user.username,
        change_summary=f"Added education: {new_edu.level} in {new_edu.stream}",
        previous_snapshot=None,
        current_snapshot=curr_dict
    )

    client_ip = request.client.host if request.client else "unknown"
    log_audit_event(
        db=db,
        event_type="EDUCATION_CREATED",
        status="SUCCESS",
        user_id=current_user.id,
        username=current_user.username,
        details={"education_id": new_edu.id, "level": new_edu.level},
        ip_address=client_ip
    )

    return new_edu


@router.put("/{education_id}", response_model=EducationOut)
def update_education(
    education_id: int,
    edu_data: EducationUpdate,
    request: Request,
    current_user: User = Depends(require_pin_verification),
    db: Session = Depends(get_db)
):
    """
    Update an existing education record.
    Requires admin privileges and PIN verification via X-Action-PIN header.
    """
    item = db.query(Education).filter(Education.id == education_id).first()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Education record not found")

    prev_dict = edu_to_dict(item)

    item.level = edu_data.level
    item.stream = edu_data.stream
    item.institution = edu_data.institution
    item.starting_month_year = edu_data.starting_month_year
    item.ending_month_year = edu_data.ending_month_year
    item.currently_studying = edu_data.currently_studying
    item.ordering = edu_data.ordering
    item.updated_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(item)

    curr_dict = edu_to_dict(item)

    record_content_revision(
        db=db,
        entity_name="education",
        action="UPDATE",
        entity_id=str(item.id),
        editor_username=current_user.username,
        change_summary=f"Updated education: {item.level} in {item.stream}",
        previous_snapshot=prev_dict,
        current_snapshot=curr_dict
    )

    client_ip = request.client.host if request.client else "unknown"
    log_audit_event(
        db=db,
        event_type="EDUCATION_UPDATED",
        status="SUCCESS",
        user_id=current_user.id,
        username=current_user.username,
        details={"education_id": item.id},
        ip_address=client_ip
    )

    return item


@router.patch("/{education_id}", response_model=EducationOut)
def patch_education(
    education_id: int,
    edu_data: EducationPatch,
    request: Request,
    current_user: User = Depends(require_pin_verification),
    db: Session = Depends(get_db)
):
    """
    Partially update an existing education record.
    Requires admin privileges and PIN verification via X-Action-PIN header.
    """
    item = db.query(Education).filter(Education.id == education_id).first()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Education record not found")

    prev_dict = edu_to_dict(item)

    # Determine prospective new state to validate business rules
    new_level = edu_data.level if edu_data.level is not None else item.level
    new_stream = edu_data.stream if edu_data.stream is not None else item.stream
    new_institution = edu_data.institution if edu_data.institution is not None else item.institution
    new_start = edu_data.starting_month_year if edu_data.starting_month_year is not None else item.starting_month_year
    new_studying = edu_data.currently_studying if edu_data.currently_studying is not None else item.currently_studying
    new_end = edu_data.ending_month_year if edu_data.ending_month_year is not None else item.ending_month_year
    new_ordering = edu_data.ordering if edu_data.ordering is not None else item.ordering

    # Validate conditional rules
    if new_studying:
        new_end = None
    else:
        if not new_end or not new_end.strip():
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Ending Month & Year is required when not currently studying."
            )

    if new_end:
        try:
            validate_date_order(new_start, new_end)
        except ValueError as ve:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=str(ve)
            )

    item.level = new_level
    item.stream = new_stream
    item.institution = new_institution
    item.starting_month_year = new_start
    item.ending_month_year = new_end
    item.currently_studying = new_studying
    item.ordering = new_ordering
    item.updated_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(item)

    curr_dict = edu_to_dict(item)

    record_content_revision(
        db=db,
        entity_name="education",
        action="PATCH",
        entity_id=str(item.id),
        editor_username=current_user.username,
        change_summary=f"Patched education: {item.level} in {item.stream}",
        previous_snapshot=prev_dict,
        current_snapshot=curr_dict
    )

    client_ip = request.client.host if request.client else "unknown"
    log_audit_event(
        db=db,
        event_type="EDUCATION_PATCHED",
        status="SUCCESS",
        user_id=current_user.id,
        username=current_user.username,
        details={"education_id": item.id},
        ip_address=client_ip
    )

    return item


@router.delete("/{education_id}", status_code=status.HTTP_200_OK)
def delete_education(
    education_id: int,
    request: Request,
    current_user: User = Depends(require_pin_verification),
    db: Session = Depends(get_db)
):
    """
    Delete an education record.
    Requires admin privileges and PIN verification via X-Action-PIN header.
    """
    item = db.query(Education).filter(Education.id == education_id).first()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Education record not found")

    prev_dict = edu_to_dict(item)

    db.delete(item)
    db.commit()

    record_content_revision(
        db=db,
        entity_name="education",
        action="DELETE",
        entity_id=str(education_id),
        editor_username=current_user.username,
        change_summary=f"Deleted education ID {education_id}",
        previous_snapshot=prev_dict,
        current_snapshot=None
    )

    client_ip = request.client.host if request.client else "unknown"
    log_audit_event(
        db=db,
        event_type="EDUCATION_DELETED",
        status="SUCCESS",
        user_id=current_user.id,
        username=current_user.username,
        details={"education_id": education_id},
        ip_address=client_ip
    )

    return {"success": True, "message": "Education record deleted"}
