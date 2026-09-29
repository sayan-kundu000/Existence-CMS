from typing import List, Optional
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.hobby_interest import HobbyInterest
from app.models.user import User
from app.schemas.hobby_interest import HobbyInterestCreate, HobbyInterestUpdate, HobbyInterestOut
from app.api.deps import require_pin_verification
from app.services.audit_service import log_audit_event, record_content_revision

router = APIRouter()


def hi_to_dict(hi: HobbyInterest) -> dict:
    return {
        "id": hi.id,
        "type": hi.type,
        "name": hi.name,
        "category": hi.category,
        "icon": hi.icon,
        "ordering": hi.ordering,
        "created_at": hi.created_at,
        "updated_at": hi.updated_at
    }


@router.get("", response_model=List[HobbyInterestOut])
def list_hobbies_interests(
    item_type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Retrieve hobbies and interests, optionally filtered by type."""
    query = db.query(HobbyInterest)
    if item_type:
        query = query.filter(HobbyInterest.type == item_type)
    return query.order_by(HobbyInterest.ordering.asc(), HobbyInterest.name.asc()).all()


@router.post("", response_model=HobbyInterestOut, status_code=status.HTTP_201_CREATED)
def create_hobby_interest(
    data: HobbyInterestCreate,
    request: Request,
    current_user: User = Depends(require_pin_verification),
    db: Session = Depends(get_db)
):
    """
    Add a new hobby or interest.
    Requires admin privileges and PIN verification via X-Action-PIN header.
    """
    new_item = HobbyInterest(
        type=data.type,
        name=data.name.strip(),
        category=data.category.strip() if data.category else None,
        icon=data.icon.strip() if data.icon else None,
        ordering=data.ordering
    )
    db.add(new_item)
    db.commit()
    db.refresh(new_item)

    curr_dict = hi_to_dict(new_item)

    record_content_revision(
        db=db,
        entity_name="hobby_interest",
        action="CREATE",
        entity_id=str(new_item.id),
        editor_username=current_user.username,
        change_summary=f"Added {new_item.type}: {new_item.name}",
        previous_snapshot=None,
        current_snapshot=curr_dict
    )

    client_ip = request.client.host if request.client else "unknown"
    log_audit_event(
        db=db,
        event_type="HOBBY_INTEREST_CREATED",
        status="SUCCESS",
        user_id=current_user.id,
        username=current_user.username,
        details={"item_id": new_item.id, "type": new_item.type, "name": new_item.name},
        ip_address=client_ip
    )

    return new_item


@router.put("/{item_id}", response_model=HobbyInterestOut)
def update_hobby_interest(
    item_id: int,
    data: HobbyInterestUpdate,
    request: Request,
    current_user: User = Depends(require_pin_verification),
    db: Session = Depends(get_db)
):
    """Update an existing hobby or interest."""
    item = db.query(HobbyInterest).filter(HobbyInterest.id == item_id).first()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")

    prev_dict = hi_to_dict(item)

    item.type = data.type
    item.name = data.name.strip()
    item.category = data.category.strip() if data.category else None
    item.icon = data.icon.strip() if data.icon else None
    item.ordering = data.ordering
    item.updated_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(item)

    curr_dict = hi_to_dict(item)

    record_content_revision(
        db=db,
        entity_name="hobby_interest",
        action="UPDATE",
        entity_id=str(item.id),
        editor_username=current_user.username,
        change_summary=f"Updated {item.type}: {item.name}",
        previous_snapshot=prev_dict,
        current_snapshot=curr_dict
    )

    return item


@router.delete("/{item_id}", status_code=status.HTTP_200_OK)
def delete_hobby_interest(
    item_id: int,
    request: Request,
    current_user: User = Depends(require_pin_verification),
    db: Session = Depends(get_db)
):
    """Delete a hobby or interest."""
    item = db.query(HobbyInterest).filter(HobbyInterest.id == item_id).first()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")

    prev_dict = hi_to_dict(item)
    db.delete(item)
    db.commit()

    record_content_revision(
        db=db,
        entity_name="hobby_interest",
        action="DELETE",
        entity_id=str(item_id),
        editor_username=current_user.username,
        change_summary=f"Deleted {prev_dict['type']}: {prev_dict['name']}",
        previous_snapshot=prev_dict,
        current_snapshot=None
    )

    return {"success": True, "message": "Item deleted"}
