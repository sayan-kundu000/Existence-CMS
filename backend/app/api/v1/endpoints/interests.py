from typing import List
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.interest import Interest
from app.models.user import User
from app.schemas.interest import InterestCreate, InterestUpdate, InterestPatch, InterestOut
from app.api.deps import require_pin_verification
from app.services.audit_service import log_audit_event, record_content_revision

router = APIRouter()


def interest_to_dict(i: Interest) -> dict:
    return {
        "id": i.id,
        "name": i.name,
        "category": i.category,
        "icon": i.icon,
        "visibility": i.visibility,
        "ordering": i.ordering,
        "created_at": i.created_at,
        "updated_at": i.updated_at
    }


@router.get("", response_model=List[InterestOut])
def list_interests(
    include_hidden: bool = False,
    db: Session = Depends(get_db)
):
    """Retrieve interests ordered by display order and name. Returns empty array if none exist."""
    query = db.query(Interest)
    if not include_hidden:
        query = query.filter(Interest.visibility == True)
    interests = query.order_by(Interest.ordering.asc(), Interest.name.asc()).all()
    return interests


@router.get("/{interest_id}", response_model=InterestOut)
def get_interest(interest_id: int, db: Session = Depends(get_db)):
    """Retrieve a single interest by ID."""
    i = db.query(Interest).filter(Interest.id == interest_id).first()
    if not i:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Interest not found")
    return i


@router.post("", response_model=InterestOut, status_code=status.HTTP_201_CREATED)
def create_interest(
    data: InterestCreate,
    request: Request,
    current_user: User = Depends(require_pin_verification),
    db: Session = Depends(get_db)
):
    """
    Create a new interest.
    Requires admin privileges and PIN verification via X-Action-PIN header.
    """
    new_interest = Interest(
        name=data.name.strip(),
        category=data.category.strip() if data.category else None,
        icon=data.icon.strip() if data.icon else None,
        visibility=data.visibility,
        ordering=data.ordering
    )
    db.add(new_interest)
    db.commit()
    db.refresh(new_interest)

    curr_dict = interest_to_dict(new_interest)

    record_content_revision(
        db=db,
        entity_name="interest",
        action="CREATE",
        entity_id=str(new_interest.id),
        editor_username=current_user.username,
        change_summary=f"Added interest: {new_interest.name}",
        previous_snapshot=None,
        current_snapshot=curr_dict
    )

    client_ip = request.client.host if request.client else "unknown"
    log_audit_event(
        db=db,
        event_type="INTEREST_CREATED",
        status="SUCCESS",
        user_id=current_user.id,
        username=current_user.username,
        details={"interest_id": new_interest.id, "name": new_interest.name},
        ip_address=client_ip
    )

    return new_interest


@router.put("/{interest_id}", response_model=InterestOut)
def update_interest(
    interest_id: int,
    data: InterestUpdate,
    request: Request,
    current_user: User = Depends(require_pin_verification),
    db: Session = Depends(get_db)
):
    """
    Update an existing interest.
    Requires admin privileges and PIN verification via X-Action-PIN header.
    """
    i = db.query(Interest).filter(Interest.id == interest_id).first()
    if not i:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Interest not found")

    prev_dict = interest_to_dict(i)

    i.name = data.name.strip()
    i.category = data.category.strip() if data.category else None
    i.icon = data.icon.strip() if data.icon else None
    i.visibility = data.visibility
    i.ordering = data.ordering
    i.updated_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(i)

    curr_dict = interest_to_dict(i)

    record_content_revision(
        db=db,
        entity_name="interest",
        action="UPDATE",
        entity_id=str(i.id),
        editor_username=current_user.username,
        change_summary=f"Updated interest: {i.name}",
        previous_snapshot=prev_dict,
        current_snapshot=curr_dict
    )

    client_ip = request.client.host if request.client else "unknown"
    log_audit_event(
        db=db,
        event_type="INTEREST_UPDATED",
        status="SUCCESS",
        user_id=current_user.id,
        username=current_user.username,
        details={"interest_id": i.id},
        ip_address=client_ip
    )

    return i


@router.patch("/{interest_id}", response_model=InterestOut)
def patch_interest(
    interest_id: int,
    data: InterestPatch,
    request: Request,
    current_user: User = Depends(require_pin_verification),
    db: Session = Depends(get_db)
):
    """
    Partially update an existing interest.
    Requires admin privileges and PIN verification via X-Action-PIN header.
    """
    i = db.query(Interest).filter(Interest.id == interest_id).first()
    if not i:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Interest not found")

    prev_dict = interest_to_dict(i)

    if data.name is not None:
        i.name = data.name.strip()
    if data.category is not None:
        i.category = data.category.strip() if data.category else None
    if data.icon is not None:
        i.icon = data.icon.strip() if data.icon else None
    if data.visibility is not None:
        i.visibility = data.visibility
    if data.ordering is not None:
        i.ordering = data.ordering

    i.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(i)

    curr_dict = interest_to_dict(i)

    record_content_revision(
        db=db,
        entity_name="interest",
        action="PATCH",
        entity_id=str(i.id),
        editor_username=current_user.username,
        change_summary=f"Patched interest: {i.name}",
        previous_snapshot=prev_dict,
        current_snapshot=curr_dict
    )

    client_ip = request.client.host if request.client else "unknown"
    log_audit_event(
        db=db,
        event_type="INTEREST_PATCHED",
        status="SUCCESS",
        user_id=current_user.id,
        username=current_user.username,
        details={"interest_id": i.id},
        ip_address=client_ip
    )

    return i


@router.delete("/{interest_id}", status_code=status.HTTP_200_OK)
def delete_interest(
    interest_id: int,
    request: Request,
    current_user: User = Depends(require_pin_verification),
    db: Session = Depends(get_db)
):
    """
    Delete an interest.
    Requires admin privileges and PIN verification via X-Action-PIN header.
    """
    i = db.query(Interest).filter(Interest.id == interest_id).first()
    if not i:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Interest not found")

    prev_dict = interest_to_dict(i)

    db.delete(i)
    db.commit()

    record_content_revision(
        db=db,
        entity_name="interest",
        action="DELETE",
        entity_id=str(interest_id),
        editor_username=current_user.username,
        change_summary=f"Deleted interest: {prev_dict['name']}",
        previous_snapshot=prev_dict,
        current_snapshot=None
    )

    client_ip = request.client.host if request.client else "unknown"
    log_audit_event(
        db=db,
        event_type="INTEREST_DELETED",
        status="SUCCESS",
        user_id=current_user.id,
        username=current_user.username,
        details={"interest_id": interest_id},
        ip_address=client_ip
    )

    return {"success": True, "message": "Interest deleted"}
