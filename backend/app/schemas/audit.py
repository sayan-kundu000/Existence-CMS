from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, ConfigDict


class ContentRevisionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    revision_id: str
    entity_name: str
    entity_id: Optional[str] = None
    action: str
    editor_username: str
    change_summary: Optional[str] = None
    previous_snapshot: Optional[Dict[str, Any]] = None
    current_snapshot: Optional[Dict[str, Any]] = None
    created_at: datetime


class AuditEventOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    event_type: str
    username: Optional[str] = None
    status: str
    details: Optional[Dict[str, Any]] = None
    ip_address: Optional[str] = None
    timestamp: datetime


class DashboardStatsOut(BaseModel):
    profile_configured: bool
    education_count: int
    experience_count: int
    work_experience_count: Optional[int] = None
    skills_count: int
    hobbies_interests_count: int
    hobbies_count: int = 0
    interests_count: int = 0
    assessments_completed: int
    personality_assessment_completed: Optional[bool] = None
    pin_configured: bool
    revisions_count: int = 0
    last_audit_event: Optional[datetime] = None
