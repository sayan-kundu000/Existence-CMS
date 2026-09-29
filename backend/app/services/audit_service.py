import json
from datetime import datetime, timezone
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from app.models.audit import AuditEvent, ContentRevision


def log_audit_event(
    db: Session,
    event_type: str,
    status: str = "SUCCESS",
    user_id: Optional[int] = None,
    username: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None,
    ip_address: Optional[str] = None
) -> AuditEvent:
    """Record a security or system audit event."""
    try:
        details_str = json.dumps(details, default=str) if details else None
        event = AuditEvent(
            event_type=event_type,
            status=status,
            user_id=user_id,
            username=username,
            details=details_str,
            ip_address=ip_address,
            timestamp=datetime.now(timezone.utc)
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
) -> ContentRevision:
    """Record an immutable version snapshot of a modified or deleted content entity."""
    try:
        prev_str = json.dumps(previous_snapshot, default=str) if previous_snapshot else None
        curr_str = json.dumps(current_snapshot, default=str) if current_snapshot else None
        
        revision = ContentRevision(
            entity_name=entity_name,
            entity_id=str(entity_id) if entity_id is not None else None,
            action=action.upper(),
            editor_username=editor_username,
            change_summary=change_summary,
            previous_snapshot=prev_str,
            current_snapshot=curr_str,
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
