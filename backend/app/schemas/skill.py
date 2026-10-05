import json
from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, ConfigDict, field_validator, model_validator
from app.models.skill import (
    SKILL_LEVEL_MAP,
    SKILL_LEVEL_METADATA,
    SKILL_CATEGORIES,
    SKILL_CATEGORY_MAP,
    normalize_skill_categories,
    normalize_skill_domains,
)


class SkillRatingLevel(BaseModel):
    rating: int = Field(..., ge=1, le=7, description="Rating scale integer 1 to 7")
    level: str = Field(..., description="Canonical level name: Beginner through Master")
    description: str = Field(..., description="Implementation-oriented description")
    display_order: int = Field(..., ge=1, le=7)


class SkillCategoriesOut(BaseModel):
    categories: List[str] = Field(..., description="17 canonical skill categories")


class SkillBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    domain: Optional[str] = Field(None, max_length=500, description="Skill domain such as AIML, Web Development, Mechanical Engineering")
    domains: List[str] = Field(default_factory=list, description="Multiple domains associated with this skill")
    category: str = Field(default="Technical", max_length=255)
    categories: List[str] = Field(default_factory=lambda: ["Technical"])
    description: Optional[str] = Field(None, max_length=255)
    rating: int = Field(..., ge=1, le=7, description="Rating from 1 (Beginner) to 7 (Master)")
    visibility: bool = Field(default=True)
    is_visible: Optional[bool] = None
    ordering: int = Field(default=0, ge=0)
    display_order: Optional[int] = None
    profile_id: Optional[int] = None
    metadata_info: Dict[str, Any] = Field(default_factory=dict)

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        if not v or not isinstance(v, str):
            raise ValueError("Skill name cannot be empty.")
        cleaned = v.strip()
        if not cleaned:
            raise ValueError("Skill name cannot be empty or whitespace-only.")
        if len(cleaned) > 100:
            raise ValueError("Skill name cannot exceed 100 characters.")
        return cleaned

    @field_validator("domain")
    @classmethod
    def validate_domain(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            cleaned = v.strip()
            return cleaned if cleaned else None
        return None

    @field_validator("rating")
    @classmethod
    def validate_rating(cls, v: Any) -> int:
        if isinstance(v, bool) or not isinstance(v, int):
            raise ValueError(f"Rating must be an integer between 1 and 7, got {v}")
        if v not in SKILL_LEVEL_MAP:
            raise ValueError(f"Rating must be an integer between 1 and 7, got {v}")
        return v

    @field_validator("category")
    @classmethod
    def validate_category(cls, v: Optional[str]) -> str:
        if not v or not isinstance(v, str) or not v.strip():
            return "Technical"
        cleaned = v.strip()
        if len(cleaned) > 255:
            raise ValueError("Category cannot exceed 255 characters.")
        return cleaned

    @field_validator("metadata_info", mode="before")
    @classmethod
    def parse_metadata_info(cls, v: Any) -> Dict[str, Any]:
        if isinstance(v, str):
            try:
                return json.loads(v) if v else {}
            except Exception:
                return {}
        if isinstance(v, dict):
            return v
        return {}

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

        # Sync categories and category
        if self.categories and (not self.category or self.category == "Technical"):
            cat_str, cat_list = normalize_skill_categories(self.categories)
            self.category = cat_str
            self.categories = cat_list
        else:
            cat_str, cat_list = normalize_skill_categories(self.category or self.categories)
            self.category = cat_str
            self.categories = cat_list

        # Sync domain and domains
        if self.domains:
            dom_str, dom_list = normalize_skill_domains(self.domains)
            self.domain = dom_str
            self.domains = dom_list
        elif self.domain:
            dom_str, dom_list = normalize_skill_domains(self.domain)
            self.domain = dom_str
            self.domains = dom_list
        return self



class SkillCreate(SkillBase):
    pass


class SkillUpdate(SkillBase):
    pass


class SkillPatch(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    domain: Optional[str] = Field(None, max_length=500)
    domains: Optional[List[str]] = None
    category: Optional[str] = Field(None, max_length=255)
    categories: Optional[List[str]] = None
    description: Optional[str] = Field(None, max_length=255)
    rating: Optional[int] = Field(None, ge=1, le=7)
    visibility: Optional[bool] = None
    is_visible: Optional[bool] = None
    ordering: Optional[int] = Field(None, ge=0)
    display_order: Optional[int] = Field(None, ge=0)
    profile_id: Optional[int] = None
    metadata_info: Optional[Dict[str, Any]] = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            if not isinstance(v, str):
                raise ValueError("Skill name must be a string.")
            cleaned = v.strip()
            if not cleaned:
                raise ValueError("Skill name cannot be empty or whitespace-only.")
            if len(cleaned) > 100:
                raise ValueError("Skill name cannot exceed 100 characters.")
            return cleaned
        return v

    @field_validator("domain")
    @classmethod
    def validate_domain(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            cleaned = v.strip()
            return cleaned if cleaned else None
        return None

    @field_validator("rating")
    @classmethod
    def validate_rating(cls, v: Any) -> Optional[int]:
        if v is not None:
            if isinstance(v, bool) or not isinstance(v, int):
                raise ValueError(f"Rating must be an integer between 1 and 7, got {v}")
            if v not in SKILL_LEVEL_MAP:
                raise ValueError(f"Rating must be an integer between 1 and 7, got {v}")
        return v

    @field_validator("category")
    @classmethod
    def validate_category(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            cleaned = v.strip()
            if not cleaned:
                return "Technical"
            if len(cleaned) > 255:
                raise ValueError("Category cannot exceed 255 characters.")
            return cleaned
        return v

    @field_validator("metadata_info", mode="before")
    @classmethod
    def parse_metadata_info(cls, v: Any) -> Optional[Dict[str, Any]]:
        if v is None:
            return None
        if isinstance(v, str):
            try:
                return json.loads(v) if v else {}
            except Exception:
                return {}
        if isinstance(v, dict):
            return v
        return {}

    @model_validator(mode="after")
    def sync_patch_categories(self):
        if self.categories is not None:
            cat_str, cat_list = normalize_skill_categories(self.categories)
            self.category = cat_str
            self.categories = cat_list
        elif self.category is not None:
            cat_str, cat_list = normalize_skill_categories(self.category)
            self.category = cat_str
            self.categories = cat_list

        if self.domains is not None:
            dom_str, dom_list = normalize_skill_domains(self.domains)
            self.domain = dom_str
            self.domains = dom_list
        elif self.domain is not None:
            dom_str, dom_list = normalize_skill_domains(self.domain)
            self.domain = dom_str
            self.domains = dom_list
        return self


class SkillOut(SkillBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    level_label: str
    level: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    @model_validator(mode="after")
    def sync_out_fields(self):
        if not self.level:
            self.level = self.level_label
        if not self.categories:
            self.categories = normalize_skill_categories(self.category)[1]
        if not self.domains:
            self.domains = normalize_skill_domains(self.domain)[1]
        return self


class SkillReorderItem(BaseModel):
    id: int = Field(..., gt=0)
    ordering: int = Field(default=0, ge=0)


class SkillReorderRequest(BaseModel):
    items: List[SkillReorderItem] = Field(..., min_length=1)
