from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict, field_validator, model_validator
from app.models.skill import SKILL_LEVEL_MAP


class SkillBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    category: str = Field(default="Technical", max_length=80)
    description: Optional[str] = Field(None, max_length=255)
    rating: int = Field(..., ge=1, le=7, description="Rating from 1 (Beginner) to 7 (Master)")
    visibility: bool = Field(default=True)
    is_visible: Optional[bool] = None
    ordering: int = Field(default=0)
    display_order: Optional[int] = None
    profile_id: Optional[int] = None
    metadata_info: Dict[str, Any] = Field(default_factory=dict)

    @field_validator("rating")
    @classmethod
    def validate_rating(cls, v: int) -> int:
        if v not in SKILL_LEVEL_MAP:
            raise ValueError(f"Rating must be an integer between 1 and 7, got {v}")
        return v

    @model_validator(mode="after")
    def sync_aliases(self):
        if self.is_visible is not None:
            self.visibility = self.is_visible
        else:
            self.is_visible = self.visibility

        if self.display_order is not None and self.ordering == 0:
            self.ordering = self.display_order
        elif self.ordering != 0 and self.display_order is None:
            self.display_order = self.ordering
        return self


class SkillCreate(SkillBase):
    pass


class SkillUpdate(SkillBase):
    pass


class SkillPatch(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    category: Optional[str] = Field(None, max_length=80)
    description: Optional[str] = Field(None, max_length=255)
    rating: Optional[int] = Field(None, ge=1, le=7)
    visibility: Optional[bool] = None
    is_visible: Optional[bool] = None
    ordering: Optional[int] = None
    display_order: Optional[int] = None
    profile_id: Optional[int] = None
    metadata_info: Optional[Dict[str, Any]] = None

    @field_validator("rating")
    @classmethod
    def validate_rating(cls, v: Optional[int]) -> Optional[int]:
        if v is not None and v not in SKILL_LEVEL_MAP:
            raise ValueError(f"Rating must be an integer between 1 and 7, got {v}")
        return v


class SkillOut(SkillBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    level_label: str
    created_at: datetime
    updated_at: datetime


class SkillReorderItem(BaseModel):
    id: int
    ordering: int
