import json
from typing import List
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.skill import Skill, SKILL_LEVEL_MAP
from app.models.user import User
from app.schemas.skill import SkillCreate, SkillUpdate, SkillPatch, SkillOut, SkillReorderItem
from app.api.deps import require_pin_verification
from app.services.audit_service import log_audit_event, record_content_revision

router = APIRouter()


def skill_to_dict(s: Skill) -> dict:
    meta = {}
    try:
        meta = json.loads(s.metadata_info) if s.metadata_info else {}
    except Exception:
        meta = {}

    return {
        "id": s.id,
        "name": s.name,
        "category": s.category,
        "description": getattr(s, "description", None),
        "rating": s.rating,
        "level_label": SKILL_LEVEL_MAP.get(s.rating, "Unknown"),
        "visibility": s.visibility,
        "ordering": s.ordering,
        "metadata_info": meta,
        "created_at": s.created_at,
        "updated_at": s.updated_at
    }


@router.get("", response_model=List[SkillOut])
def list_skills(
    include_hidden: bool = False,
    db: Session = Depends(get_db)
):
    """Retrieve skills ordered by ordering index and name."""
    query = db.query(Skill)
    if not include_hidden:
        query = query.filter(Skill.visibility == True)
    skills = query.order_by(Skill.ordering.asc(), Skill.name.asc()).all()
    return [skill_to_dict(s) for s in skills]


@router.get("/{skill_id}", response_model=SkillOut)
def get_skill(skill_id: int, db: Session = Depends(get_db)):
    """Retrieve single skill item."""
    s = db.query(Skill).filter(Skill.id == skill_id).first()
    if not s:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Skill not found")
    return skill_to_dict(s)


@router.post("", response_model=SkillOut, status_code=status.HTTP_201_CREATED)
def create_skill(
    skill_data: SkillCreate,
    request: Request,
    current_user: User = Depends(require_pin_verification),
    db: Session = Depends(get_db)
):
    """
    Create a new skill with 7-level rating.
    Requires admin privileges and PIN verification via X-Action-PIN header.
    """
    new_skill = Skill(
        name=skill_data.name.strip(),
        category=skill_data.category.strip(),
        description=skill_data.description.strip() if skill_data.description else None,
        rating=skill_data.rating,
        visibility=skill_data.visibility,
        ordering=skill_data.ordering,
        metadata_info=json.dumps(skill_data.metadata_info)
    )
    db.add(new_skill)
    db.commit()
    db.refresh(new_skill)

    curr_dict = skill_to_dict(new_skill)

    record_content_revision(
        db=db,
        entity_name="skill",
        action="CREATE",
        entity_id=str(new_skill.id),
        editor_username=current_user.username,
        change_summary=f"Added skill: {new_skill.name} (Level {new_skill.rating} - {new_skill.level_label})",
        previous_snapshot=None,
        current_snapshot=curr_dict
    )

    client_ip = request.client.host if request.client else "unknown"
    log_audit_event(
        db=db,
        event_type="SKILL_CREATED",
        status="SUCCESS",
        user_id=current_user.id,
        username=current_user.username,
        details={"skill_id": new_skill.id, "name": new_skill.name, "rating": new_skill.rating},
        ip_address=client_ip
    )

    return curr_dict


@router.put("/{skill_id}", response_model=SkillOut)
def update_skill(
    skill_id: int,
    skill_data: SkillUpdate,
    request: Request,
    current_user: User = Depends(require_pin_verification),
    db: Session = Depends(get_db)
):
    """
    Update an existing skill.
    Requires admin privileges and PIN verification via X-Action-PIN header.
    """
    s = db.query(Skill).filter(Skill.id == skill_id).first()
    if not s:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Skill not found")

    prev_dict = skill_to_dict(s)

    s.name = skill_data.name.strip()
    s.category = skill_data.category.strip()
    s.description = skill_data.description.strip() if skill_data.description else None
    s.rating = skill_data.rating
    s.visibility = skill_data.visibility
    s.ordering = skill_data.ordering
    s.metadata_info = json.dumps(skill_data.metadata_info)
    s.updated_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(s)

    curr_dict = skill_to_dict(s)

    record_content_revision(
        db=db,
        entity_name="skill",
        action="UPDATE",
        entity_id=str(s.id),
        editor_username=current_user.username,
        change_summary=f"Updated skill: {s.name} (Level {s.rating} - {s.level_label})",
        previous_snapshot=prev_dict,
        current_snapshot=curr_dict
    )

    client_ip = request.client.host if request.client else "unknown"
    log_audit_event(
        db=db,
        event_type="SKILL_UPDATED",
        status="SUCCESS",
        user_id=current_user.id,
        username=current_user.username,
        details={"skill_id": s.id, "rating": s.rating},
        ip_address=client_ip
    )

    return curr_dict


@router.patch("/{skill_id}", response_model=SkillOut)
def patch_skill(
    skill_id: int,
    skill_data: SkillPatch,
    request: Request,
    current_user: User = Depends(require_pin_verification),
    db: Session = Depends(get_db)
):
    """
    Partially update an existing skill.
    Requires admin privileges and PIN verification via X-Action-PIN header.
    """
    s = db.query(Skill).filter(Skill.id == skill_id).first()
    if not s:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Skill not found")

    prev_dict = skill_to_dict(s)

    if skill_data.name is not None:
        s.name = skill_data.name.strip()
    if skill_data.category is not None:
        s.category = skill_data.category.strip()
    if skill_data.description is not None:
        s.description = skill_data.description.strip() if skill_data.description else None
    if skill_data.rating is not None:
        s.rating = skill_data.rating
    if skill_data.visibility is not None:
        s.visibility = skill_data.visibility
    if skill_data.ordering is not None:
        s.ordering = skill_data.ordering
    if skill_data.metadata_info is not None:
        s.metadata_info = json.dumps(skill_data.metadata_info)

    s.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(s)

    curr_dict = skill_to_dict(s)

    record_content_revision(
        db=db,
        entity_name="skill",
        action="PATCH",
        entity_id=str(s.id),
        editor_username=current_user.username,
        change_summary=f"Patched skill: {s.name} (Level {s.rating} - {s.level_label})",
        previous_snapshot=prev_dict,
        current_snapshot=curr_dict
    )

    client_ip = request.client.host if request.client else "unknown"
    log_audit_event(
        db=db,
        event_type="SKILL_PATCHED",
        status="SUCCESS",
        user_id=current_user.id,
        username=current_user.username,
        details={"skill_id": s.id, "rating": s.rating},
        ip_address=client_ip
    )

    return curr_dict


@router.delete("/{skill_id}", status_code=status.HTTP_200_OK)
def delete_skill(
    skill_id: int,
    request: Request,
    current_user: User = Depends(require_pin_verification),
    db: Session = Depends(get_db)
):
    """
    Delete a skill.
    Requires admin privileges and PIN verification via X-Action-PIN header.
    """
    s = db.query(Skill).filter(Skill.id == skill_id).first()
    if not s:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Skill not found")

    prev_dict = skill_to_dict(s)

    db.delete(s)
    db.commit()

    record_content_revision(
        db=db,
        entity_name="skill",
        action="DELETE",
        entity_id=str(skill_id),
        editor_username=current_user.username,
        change_summary=f"Deleted skill ID {skill_id} ({prev_dict['name']})",
        previous_snapshot=prev_dict,
        current_snapshot=None
    )

    client_ip = request.client.host if request.client else "unknown"
    log_audit_event(
        db=db,
        event_type="SKILL_DELETED",
        status="SUCCESS",
        user_id=current_user.id,
        username=current_user.username,
        details={"skill_id": skill_id},
        ip_address=client_ip
    )

    return {"success": True, "message": "Skill deleted"}


@router.post("/reorder", status_code=status.HTTP_200_OK)
def reorder_skills(
    items: List[SkillReorderItem],
    request: Request,
    current_user: User = Depends(require_pin_verification),
    db: Session = Depends(get_db)
):
    """Reorder skill priorities in bulk."""
    for item in items:
        db.query(Skill).filter(Skill.id == item.id).update({"ordering": item.ordering})
    db.commit()
    return {"success": True, "message": "Skills reordered successfully"}
