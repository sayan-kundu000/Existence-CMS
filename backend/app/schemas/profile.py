import re
from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, EmailStr, Field, ConfigDict, field_validator
from app.schemas.education import EducationOut
from app.schemas.experience import ExperienceOut
from app.schemas.skill import SkillOut
from app.schemas.hobby import HobbyOut
from app.schemas.interest import InterestOut
from app.schemas.project import ProjectOut


class ProfileEmailBase(BaseModel):
    email: EmailStr
    label: str = Field(default="Primary", max_length=50)
    is_primary: bool = Field(default=False)
    is_public: bool = Field(default=True)
    display_order: int = Field(default=0, ge=0)


class ProfileEmailCreate(ProfileEmailBase):
    pass


class ProfileEmailUpdate(BaseModel):
    email: Optional[EmailStr] = None
    label: Optional[str] = Field(None, max_length=50)
    is_primary: Optional[bool] = None
    is_public: Optional[bool] = None
    display_order: Optional[int] = Field(None, ge=0)


class ProfileEmailOut(ProfileEmailBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    profile_id: int
    created_at: datetime
    updated_at: datetime
    assessments_reset: Optional[bool] = None


class ProfileBase(BaseModel):
    name: Optional[str] = Field(None, max_length=120)
    email_ids: List[str] = Field(default_factory=list)
    mobile_number: Optional[str] = Field(None, max_length=30)
    linkedin: Optional[str] = Field(None, max_length=255)
    about: Optional[str] = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        trimmed = v.strip()
        if len(trimmed) == 0:
            raise ValueError("Name cannot be empty or blank whitespace.")
        return trimmed

    @field_validator("about")
    @classmethod
    def validate_about(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        trimmed = v.strip()
        if "<script" in trimmed.lower():
            raise ValueError("Raw executable scripts are not permitted in about narrative.")
        from app.core.sanitizer import sanitize_text
        return sanitize_text(trimmed)


    @field_validator("mobile_number")
    @classmethod
    def validate_mobile(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        trimmed = v.strip()
        if len(trimmed) == 0:
            return None
        # Validates international phone representation with digits and standard formatting symbols
        if not re.match(r"^\+?[0-9\s\-().]{7,25}$", trimmed):
            raise ValueError("Invalid phone number format. Must contain 7 to 25 valid digits with optional country code.")
        return trimmed

    @field_validator("linkedin")
    @classmethod
    def validate_linkedin(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        trimmed = v.strip()
        if len(trimmed) == 0:
            return None
        if not (trimmed.startswith("http://") or trimmed.startswith("https://")):
            raise ValueError("LinkedIn must be a valid URL starting with https:// or http://.")
        if "linkedin.com" not in trimmed.lower():
            raise ValueError("LinkedIn URL must point to a valid linkedin.com domain.")
        return trimmed


class ProfileUpdate(ProfileBase):
    pass


class ProfileOut(ProfileBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    is_empty: bool = True
    emails: Optional[List[ProfileEmailOut]] = None
    assessments_reset: Optional[bool] = None
    created_at: datetime
    updated_at: datetime


class ProfileCompletenessOut(BaseModel):
    percentage: float = Field(..., description="Overall completeness percentage from 0.0 to 100.0")
    completed_count: int = Field(..., description="Number of completed dimensions out of 9")
    total_dimensions: int = Field(default=9, description="Total profile dimensions tracked")
    dimension_status: Dict[str, bool] = Field(..., description="Boolean completion state for each dimension")
    completed_dimensions: List[str] = Field(default_factory=list)
    missing_dimensions: List[str] = Field(default_factory=list)
    score_percentage: Optional[float] = None
    dimensions_completed: Optional[int] = None
    dimensions_total: Optional[int] = None
    breakdown: Optional[Dict[str, bool]] = None


class ConsolidatedPublicProfile(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: Optional[str] = None
    about: Optional[str] = None
    linkedin: Optional[str] = None
    mobile_number: Optional[str] = None
    primary_email: Optional[str] = None
    public_emails: List[str] = Field(default_factory=list)
    emails: List[ProfileEmailOut] = Field(default_factory=list)
    education: List[EducationOut] = Field(default_factory=list)
    experience: List[ExperienceOut] = Field(default_factory=list)
    skills: List[SkillOut] = Field(default_factory=list)
    projects: List[ProjectOut] = Field(default_factory=list)
    hobbies: List[HobbyOut] = Field(default_factory=list)
    interests: List[InterestOut] = Field(default_factory=list)
    completeness: ProfileCompletenessOut
    is_empty: bool = True
    created_at: datetime
    updated_at: datetime
    profile: Optional[Dict[str, Any]] = None
    personality: Optional[Dict[str, Any]] = None


ConsolidatedPublicProfile.model_rebuild()
