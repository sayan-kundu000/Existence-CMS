import json
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, Request, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.audit import AuditEvent, ContentRevision
from app.models.user import User
from app.api.deps import require_admin, require_pin_verification
from app.schemas.audit import AuditEventOut, ContentRevisionOut

router = APIRouter()


@router.get("/events", response_model=List[AuditEventOut])
@router.get("/logs", response_model=List[AuditEventOut])
def list_audit_events(
    limit: int = Query(50, ge=1, le=200),
    event_type: Optional[str] = None,
    action: Optional[str] = None,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Retrieve security audit events in reverse chronological order."""
    query = db.query(AuditEvent)
    filter_type = event_type or action
    if filter_type:
        query = query.filter(AuditEvent.event_type == filter_type)
    events = query.order_by(AuditEvent.timestamp.desc()).limit(limit).all()

    result = []
    for ev in events:
        details_dict = None
        try:
            details_dict = json.loads(ev.details) if ev.details else None
        except Exception:
            pass

        result.append(
            AuditEventOut(
                id=ev.id,
                event_type=ev.event_type,
                username=ev.username,
                status=ev.status,
                details=details_dict,
                ip_address=ev.ip_address,
                timestamp=ev.timestamp
            )
        )
    return result


@router.get("/revisions", response_model=List[ContentRevisionOut])
def list_content_revisions(
    limit: int = Query(50, ge=1, le=200),
    entity_name: Optional[str] = None,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Retrieve immutable content revisions and snapshots for audit inspection."""
    query = db.query(ContentRevision)
    if entity_name:
        query = query.filter(ContentRevision.entity_name == entity_name)
    revisions = query.order_by(ContentRevision.created_at.desc()).limit(limit).all()

    result = []
    for rev in revisions:
        prev_snap = None
        curr_snap = None
        try:
            prev_snap = json.loads(rev.previous_snapshot) if rev.previous_snapshot else None
        except Exception:
            pass
        try:
            curr_snap = json.loads(rev.current_snapshot) if rev.current_snapshot else None
        except Exception:
            pass

        result.append(
            ContentRevisionOut(
                id=rev.id,
                revision_id=rev.revision_id,
                entity_name=rev.entity_name,
                entity_id=rev.entity_id,
                action=rev.action,
                editor_username=rev.editor_username,
                change_summary=rev.change_summary,
                previous_snapshot=prev_snap,
                current_snapshot=curr_snap,
                created_at=rev.created_at
            )
        )
    return result


@router.post("/revisions/{revision_id}/restore")
def restore_content_revision(
    revision_id: str,
    request: Request,
    current_user: User = Depends(require_pin_verification),
    db: Session = Depends(get_db)
):
    """
    Restore an entity snapshot from a historical revision.
    Requires admin privileges and security PIN verification via X-Action-PIN.
    Creates a new revision record (action='RESTORE') and audit trail.
    """
    from app.services.audit_service import log_audit_event, record_content_revision

    query = db.query(ContentRevision)
    if revision_id.isdigit():
        rev = query.filter((ContentRevision.id == int(revision_id)) | (ContentRevision.revision_id == revision_id)).first()
    else:
        rev = query.filter(ContentRevision.revision_id == revision_id).first()

    if not rev:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Content revision not found.")

    snapshot_raw = rev.current_snapshot or rev.previous_snapshot
    if not snapshot_raw:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Revision has no snapshot data to restore.")

    try:
        snapshot = json.loads(snapshot_raw) if isinstance(snapshot_raw, str) else snapshot_raw
    except Exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Malformed snapshot payload.")

    entity_name = rev.entity_name.lower()
    client_ip = request.client.host if request.client else "unknown"

    if entity_name == "profile":
        from app.models.profile import Profile
        prof = db.query(Profile).first()
        if not prof:
            prof = Profile()
            db.add(prof)
        prev_dict = {
            "name": prof.name,
            "email_ids": prof.email_ids,
            "mobile_number": prof.mobile_number,
            "linkedin": prof.linkedin,
            "about": prof.about
        }
        prof.name = snapshot.get("name")
        if "email_ids" in snapshot:
            emails_val = snapshot.get("email_ids")
            prof.email_ids = json.dumps(emails_val) if isinstance(emails_val, list) else str(emails_val)
        prof.mobile_number = snapshot.get("mobile_number")
        prof.linkedin = snapshot.get("linkedin")
        prof.about = snapshot.get("about")
        db.commit()
        db.refresh(prof)

        record_content_revision(
            db=db,
            entity_name="profile",
            action="RESTORE",
            entity_id=str(prof.id),
            editor_username=current_user.username,
            change_summary=f"Restored profile from revision {rev.id}",
            previous_snapshot=prev_dict,
            current_snapshot=snapshot
        )

    elif entity_name == "education":
        from app.models.education import Education
        edu_id = int(rev.entity_id) if rev.entity_id and rev.entity_id.isdigit() else None
        edu = db.query(Education).filter(Education.id == edu_id).first() if edu_id else None
        if not edu:
            edu = Education(profile_id=snapshot.get("profile_id", 1))
            db.add(edu)
        edu.level = snapshot.get("level", "Graduate")
        edu.stream = snapshot.get("stream", "")
        edu.institution = snapshot.get("institution")
        edu.starting_month_year = snapshot.get("starting_month_year")
        edu.ending_month_year = snapshot.get("ending_month_year")
        edu.currently_studying = bool(snapshot.get("currently_studying", False))
        edu.ordering = int(snapshot.get("ordering", 0))
        db.commit()
        db.refresh(edu)

        record_content_revision(
            db=db,
            entity_name="education",
            action="RESTORE",
            entity_id=str(edu.id),
            editor_username=current_user.username,
            change_summary=f"Restored education from revision {rev.id}",
            previous_snapshot=None,
            current_snapshot=snapshot
        )

    elif entity_name in ("experience", "work_experiences"):
        from app.models.experience import Experience
        exp_id = int(rev.entity_id) if rev.entity_id and rev.entity_id.isdigit() else None
        exp = db.query(Experience).filter(Experience.id == exp_id).first() if exp_id else None
        if not exp:
            exp = Experience(profile_id=snapshot.get("profile_id", 1))
            db.add(exp)
        exp.role = snapshot.get("role", "")
        exp.employer = snapshot.get("employer", "")
        exp.work_mode = snapshot.get("work_mode", "On-site")
        exp.location = snapshot.get("location")
        exp.starting_month_year = snapshot.get("starting_month_year")
        exp.ending_month_year = snapshot.get("ending_month_year")
        exp.currently_working = bool(snapshot.get("currently_working", False))
        exp.ordering = int(snapshot.get("ordering", 0))
        db.commit()
        db.refresh(exp)

        record_content_revision(
            db=db,
            entity_name="experience",
            action="RESTORE",
            entity_id=str(exp.id),
            editor_username=current_user.username,
            change_summary=f"Restored experience from revision {rev.id}",
            previous_snapshot=None,
            current_snapshot=snapshot
        )

    elif entity_name == "skills":
        from app.models.skill import Skill
        sk_id = int(rev.entity_id) if rev.entity_id and rev.entity_id.isdigit() else None
        sk = db.query(Skill).filter(Skill.id == sk_id).first() if sk_id else None
        if not sk:
            sk = Skill(profile_id=snapshot.get("profile_id", 1))
            db.add(sk)
        sk.name = snapshot.get("name", "")
        sk.category = snapshot.get("category", "General")
        sk.rating = int(snapshot.get("rating", 4))
        sk.visibility = bool(snapshot.get("visibility", True))
        sk.ordering = int(snapshot.get("ordering", 0))
        db.commit()
        db.refresh(sk)

        record_content_revision(
            db=db,
            entity_name="skills",
            action="RESTORE",
            entity_id=str(sk.id),
            editor_username=current_user.username,
            change_summary=f"Restored skill from revision {rev.id}",
            previous_snapshot=None,
            current_snapshot=snapshot
        )

    elif entity_name in ("hobbies", "interests", "hobbies_interests"):
        from app.models.hobby_interest import HobbyInterest
        hi_id = int(rev.entity_id) if rev.entity_id and rev.entity_id.isdigit() else None
        hi = db.query(HobbyInterest).filter(HobbyInterest.id == hi_id).first() if hi_id else None
        if not hi:
            hi = HobbyInterest(profile_id=snapshot.get("profile_id", 1))
            db.add(hi)
        hi.type = snapshot.get("type", "hobby")
        hi.name = snapshot.get("name", "")
        hi.category = snapshot.get("category")
        hi.icon = snapshot.get("icon")
        hi.ordering = int(snapshot.get("ordering", 0))
        db.commit()
        db.refresh(hi)

        record_content_revision(
            db=db,
            entity_name="hobbies_interests",
            action="RESTORE",
            entity_id=str(hi.id),
            editor_username=current_user.username,
            change_summary=f"Restored {hi.type} from revision {rev.id}",
            previous_snapshot=None,
            current_snapshot=snapshot
        )

    elif entity_name == "personality_synthesis":
        from app.models.assessment import PersonalitySynthesis
        syn = db.query(PersonalitySynthesis).first()
        if not syn:
            syn = PersonalitySynthesis()
            db.add(syn)
        soft = snapshot.get("key_soft_skills", [])
        syn.key_soft_skills = json.dumps(soft) if isinstance(soft, list) else str(soft)
        str_ = snapshot.get("key_strengths", [])
        syn.key_strengths = json.dumps(str_) if isinstance(str_, list) else str(str_)
        w_ = snapshot.get("key_weaknesses", [])
        syn.key_weaknesses = json.dumps(w_) if isinstance(w_, list) else str(w_)
        syn.summary_notes = snapshot.get("summary_notes")
        db.commit()
        db.refresh(syn)

        record_content_revision(
            db=db,
            entity_name="personality_synthesis",
            action="RESTORE",
            entity_id=str(syn.id),
            editor_username=current_username if 'current_username' in locals() else current_user.username,
            change_summary=f"Restored personality synthesis from revision {rev.id}",
            previous_snapshot=None,
            current_snapshot=snapshot
        )
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Entity '{rev.entity_name}' cannot be restored.")

    log_audit_event(
        db=db,
        event_type="REVISION_RESTORED",
        status="SUCCESS",
        user_id=current_user.id,
        username=current_user.username,
        details={"revision_id": rev.id, "entity_name": rev.entity_name, "entity_id": rev.entity_id},
        ip_address=client_ip
    )

    return {
        "success": True,
        "message": f"Successfully restored {rev.entity_name} revision {rev.id}.",
        "entity_name": rev.entity_name,
        "entity_id": rev.entity_id
    }
