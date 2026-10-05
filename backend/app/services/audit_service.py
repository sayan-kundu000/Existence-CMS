import json
from datetime import datetime, timezone
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from app.models.audit import AuditEvent, ContentRevision
from app.core.sanitizer import sanitize_audit_metadata


def log_audit_event(
    db: Session,
    event_type: str,
    status: str = "SUCCESS",
    user_id: Optional[int] = None,
    username: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None,
    ip_address: Optional[str] = None,
    request_id: Optional[str] = None
) -> Optional[AuditEvent]:
    """
    Record a security or system audit event.
    Automatically scrubs sensitive credentials, tokens, and PINs from metadata.
    """
    try:
        clean_details = sanitize_audit_metadata(details) if details else None
        details_str = json.dumps(clean_details, default=str) if clean_details else None
        event = AuditEvent(
            action=event_type,
            status=status,
            actor_id=user_id,
            username=username,
            metadata_json=details_str,
            ip_address=ip_address,
            request_id=request_id,
            created_at=datetime.now(timezone.utc)
        )
        db.add(event)
        db.commit()
        db.refresh(event)
        return event
    except Exception as e:
        db.rollback()
        # Logging failure should not disrupt main execution flow
        print(f"[Audit Warning] Failed to write audit event: {e}")
        return None


def record_content_revision(
    db: Session,
    entity_name: str,
    action: str,
    entity_id: Optional[str] = None,
    editor_username: str = "admin",
    change_summary: Optional[str] = None,
    previous_snapshot: Optional[Dict[str, Any]] = None,
    current_snapshot: Optional[Dict[str, Any]] = None
) -> Optional[ContentRevision]:
    """
    Record an immutable version snapshot of a modified or deleted content entity.
    Automatically scrubs sensitive fields before persistence.
    """
    try:
        clean_prev = sanitize_audit_metadata(previous_snapshot) if previous_snapshot else None
        clean_curr = sanitize_audit_metadata(current_snapshot) if current_snapshot else None

        prev_str = json.dumps(clean_prev, default=str) if clean_prev else None
        curr_str = json.dumps(clean_curr, default=str) if clean_curr else None
        
        revision = ContentRevision(
            entity_type=entity_name,
            entity_id=str(entity_id) if entity_id is not None else None,
            action=action.upper(),
            changed_by=editor_username,
            change_summary=change_summary,
            previous_snapshot=prev_str,
            snapshot=curr_str,
            created_at=datetime.now(timezone.utc)
        )
        db.add(revision)
        db.commit()
        db.refresh(revision)
        return revision
    except Exception as e:
        db.rollback()
        print(f"[Revision Warning] Failed to record content revision: {e}")
        return None

