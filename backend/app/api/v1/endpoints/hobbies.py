from typing import List
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.hobby import Hobby
from app.models.user import User
from app.schemas.hobby import HobbyCreate, HobbyUpdate, HobbyPatch, HobbyOut
from app.api.deps import require_pin_verification
from app.services.audit_service import log_audit_event, record_content_revision

router = APIRouter()


def hobby_to_dict(h: Hobby) -> dict:
    return {
        "id": h.id,
        "name": h.name,
        "category": h.category,
        "icon": h.icon,
        "visibility": h.visibility,
        "ordering": h.ordering,
        "created_at": h.created_at,
        "updated_at": h.updated_at
    }


@router.get("", response_model=List[HobbyOut])
def list_hobbies(
    include_hidden: bool = False,
    db: Session = Depends(get_db)
):
    """Retrieve hobbies ordered by display order and name. Returns empty array if none exist."""
    query = db.query(Hobby)
    if not include_hidden:
        query = query.filter(Hobby.visibility == True)
    hobbies = query.order_by(Hobby.ordering.asc(), Hobby.name.asc()).all()
    return hobbies


@router.get("/{hobby_id}", response_model=HobbyOut)
def get_hobby(hobby_id: int, db: Session = Depends(get_db)):
    """Retrieve a single hobby by ID."""
    h = db.query(Hobby).filter(Hobby.id == hobby_id).first()
    if not h:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Hobby not found")
    return h


@router.post("", response_model=HobbyOut, status_code=status.HTTP_201_CREATED)
def create_hobby(
    data: HobbyCreate,
    request: Request,
    current_user: User = Depends(require_pin_verification),
    db: Session = Depends(get_db)
):
    """
    Create a new hobby.
    Requires admin privileges and PIN verification via X-Action-PIN header.
    """
    new_hobby = Hobby(
        name=data.name.strip(),
        category=data.category.strip() if data.category else None,
        icon=data.icon.strip() if data.icon else None,
        visibility=data.visibility,
        ordering=data.ordering
    )
    db.add(new_hobby)
    db.commit()
    db.refresh(new_hobby)

    curr_dict = hobby_to_dict(new_hobby)

    record_content_revision(
        db=db,
        entity_name="hobby",
        action="CREATE",
        entity_id=str(new_hobby.id),
        editor_username=current_user.username,
        change_summary=f"Added hobby: {new_hobby.name}",
        previous_snapshot=None,
        current_snapshot=curr_dict
    )

    client_ip = request.client.host if request.client else "unknown"
    log_audit_event(
        db=db,
        event_type="HOBBY_CREATED",
        status="SUCCESS",
        user_id=current_user.id,
        username=current_user.username,
        details={"hobby_id": new_hobby.id, "name": new_hobby.name},
        ip_address=client_ip
    )

    return new_hobby


@router.put("/{hobby_id}", response_model=HobbyOut)
def update_hobby(
    hobby_id: int,
    data: HobbyUpdate,
    request: Request,
    current_user: User = Depends(require_pin_verification),
    db: Session = Depends(get_db)
):
    """
    Update an existing hobby.
    Requires admin privileges and PIN verification via X-Action-PIN header.
    """
    h = db.query(Hobby).filter(Hobby.id == hobby_id).first()
    if not h:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Hobby not found")

    prev_dict = hobby_to_dict(h)

    h.name = data.name.strip()
    h.category = data.category.strip() if data.category else None
    h.icon = data.icon.strip() if data.icon else None
    h.visibility = data.visibility
    h.ordering = data.ordering
    h.updated_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(h)

    curr_dict = hobby_to_dict(h)

    record_content_revision(
        db=db,
        entity_name="hobby",
        action="UPDATE",
        entity_id=str(h.id),
        editor_username=current_user.username,
        change_summary=f"Updated hobby: {h.name}",
        previous_snapshot=prev_dict,
        current_snapshot=curr_dict
    )

    client_ip = request.client.host if request.client else "unknown"
    log_audit_event(
        db=db,
        event_type="HOBBY_UPDATED",
        status="SUCCESS",
        user_id=current_user.id,
        username=current_user.username,
        details={"hobby_id": h.id},
        ip_address=client_ip
    )

    return h


@router.patch("/{hobby_id}", response_model=HobbyOut)
def patch_hobby(
    hobby_id: int,
    data: HobbyPatch,
    request: Request,
    current_user: User = Depends(require_pin_verification),
    db: Session = Depends(get_db)
):
    """
    Partially update an existing hobby.
    Requires admin privileges and PIN verification via X-Action-PIN header.
    """
    h = db.query(Hobby).filter(Hobby.id == hobby_id).first()
    if not h:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Hobby not found")

    prev_dict = hobby_to_dict(h)

    if data.name is not None:
        h.name = data.name.strip()
    if data.category is not None:
        h.category = data.category.strip() if data.category else None
    if data.icon is not None:
        h.icon = data.icon.strip() if data.icon else None
    if data.visibility is not None:
        h.visibility = data.visibility
    if data.ordering is not None:
        h.ordering = data.ordering

    h.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(h)

    curr_dict = hobby_to_dict(h)

    record_content_revision(
        db=db,
        entity_name="hobby",
        action="PATCH",
        entity_id=str(h.id),
        editor_username=current_user.username,
        change_summary=f"Patched hobby: {h.name}",
        previous_snapshot=prev_dict,
        current_snapshot=curr_dict
    )

    client_ip = request.client.host if request.client else "unknown"
    log_audit_event(
        db=db,
        event_type="HOBBY_PATCHED",
        status="SUCCESS",
        user_id=current_user.id,
        username=current_user.username,
        details={"hobby_id": h.id},
        ip_address=client_ip
    )

    return h


@router.delete("/{hobby_id}", status_code=status.HTTP_200_OK)
def delete_hobby(
    hobby_id: int,
    request: Request,
    current_user: User = Depends(require_pin_verification),
    db: Session = Depends(get_db)
):
    """
    Delete a hobby.
    Requires admin privileges and PIN verification via X-Action-PIN header.
    """
    h = db.query(Hobby).filter(Hobby.id == hobby_id).first()
    if not h:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Hobby not found")

    prev_dict = hobby_to_dict(h)

    db.delete(h)
    db.commit()

    record_content_revision(
        db=db,
        entity_name="hobby",
        action="DELETE",
        entity_id=str(hobby_id),
        editor_username=current_user.username,
        change_summary=f"Deleted hobby: {prev_dict['name']}",
        previous_snapshot=prev_dict,
        current_snapshot=None
    )

    client_ip = request.client.host if request.client else "unknown"
    log_audit_event(
        db=db,
        event_type="HOBBY_DELETED",
        status="SUCCESS",
        user_id=current_user.id,
        username=current_user.username,
        details={"hobby_id": hobby_id},
        ip_address=client_ip
    )

    return {"success": True, "message": "Hobby deleted"}
