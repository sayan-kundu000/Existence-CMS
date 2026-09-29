import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime, CheckConstraint
from sqlalchemy.orm import synonym
from app.core.database import Base

VALID_REVISION_ACTIONS = ("CREATE", "UPDATE", "DELETE", "RESTORE", "PATCH")


class ContentRevision(Base):
    __tablename__ = "content_revisions"

    id = Column(Integer, primary_key=True, index=True)
    revision_id = Column(String(36), default=lambda: str(uuid.uuid4()), index=True, nullable=False)
    entity_type = Column(String(50), nullable=False, index=True)
    entity_id = Column(String(50), nullable=True, index=True)
    revision_number = Column(Integer, default=1, nullable=False)
    action = Column(String(20), nullable=False)  # CREATE, UPDATE, DELETE, RESTORE, PATCH
    changed_by = Column(String(50), default="admin", nullable=False)
    change_summary = Column(String(255), nullable=True)
    previous_snapshot = Column(Text, nullable=True)  # JSON string
    snapshot = Column(Text, nullable=True)           # JSON string
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    # Aliases
    entity_name = synonym("entity_type")
    editor_username = synonym("changed_by")
    current_snapshot = synonym("snapshot")

    __table_args__ = (
        CheckConstraint(
            f"action IN {VALID_REVISION_ACTIONS}",
            name="check_content_revision_action"
        ),
    )


class AuditEvent(Base):
    __tablename__ = "audit_events"

    id = Column(Integer, primary_key=True, index=True)
    actor_id = Column(Integer, nullable=True, index=True)
    username = Column(String(50), nullable=True)
    action = Column(String(50), nullable=False, index=True)
    entity_type = Column(String(50), nullable=True, index=True)
    entity_id = Column(String(50), nullable=True, index=True)
    request_id = Column(String(64), nullable=True, index=True)
    status = Column(String(20), default="SUCCESS", nullable=False)  # SUCCESS, FAILED, LOCKED
    metadata_json = Column(Text, nullable=True)  # JSON string
    ip_address = Column(String(60), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    # Aliases
    user_id = synonym("actor_id")
    event_type = synonym("action")
    details = synonym("metadata_json")
    timestamp = synonym("created_at")
