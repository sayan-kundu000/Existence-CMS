import re
from datetime import datetime
from typing import List, Optional, Literal, Union, Dict, Any
from pydantic import BaseModel, Field, ConfigDict, field_validator, model_validator
from app.models.project import PROJECT_STATUSES, LINK_TYPES, TECH_CATEGORIES

ProjectStatus = Literal["Planned", "In Progress", "Completed", "Archived"]
ProjectLinkType = Literal[
    "Live Demo",
    "Deployment",
    "GitHub",
    "Repository",
    "Documentation",
    "API",
    "Video Demo",
    "Case Study",
    "Other"
]
TechCategory = Literal[
    "Programming Language",
    "Framework",
    "Database",
    "Cloud/Deployment",
    "Frontend",
    "Backend",
    "DevOps",
    "Testing",
    "Data/AI",
    "Other"
]


def validate_url_protocol(url: str) -> str:
    if not url or not isinstance(url, str):
        raise ValueError("URL must not be empty.")
    trimmed = url.strip()
    if not trimmed:
        raise ValueError("URL cannot be empty or whitespace-only.")
    if len(trimmed) > 1000:
        raise ValueError("URL cannot exceed 1000 characters.")
    lowered = trimmed.lower()
    if lowered.startswith(("javascript:", "data:", "vbscript:", "file:", "blob:")):
        raise ValueError("Unsafe URL scheme detected.")
    if not (lowered.startswith("http://") or lowered.startswith("https://")):
        raise ValueError("URL must begin with http:// or https://.")
    from app.core.sanitizer import validate_safe_url
    return validate_safe_url(trimmed)



# -----------------------------------------------------------------------------
# Technology Schemas
# -----------------------------------------------------------------------------

class TechnologyBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    category: TechCategory = Field(default="Other")

    @field_validator("name")
    @classmethod
    def clean_name(cls, v: str) -> str:
        clean = v.strip()
        if not clean:
            raise ValueError("Technology name cannot be empty.")
        return clean


class TechnologyCreate(TechnologyBase):
    pass


class TechnologyOut(TechnologyBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime


class ProjectTechnologyOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    technology_id: int
    name: str
    category: str
    display_order: int


class ProjectTechnologyInput(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    category: Optional[TechCategory] = "Other"
    technology_id: Optional[int] = None
    display_order: Optional[int] = 0

    @field_validator("name")
    @classmethod
    def clean_name(cls, v: str) -> str:
        clean = v.strip()
        if not clean:
            raise ValueError("Technology name cannot be empty.")
        return clean


# -----------------------------------------------------------------------------
# Project Link Schemas
# -----------------------------------------------------------------------------

class ProjectLinkBase(BaseModel):
    label: str = Field(..., min_length=1, max_length=100)
    url: str = Field(..., min_length=1, max_length=1000)
    link_type: ProjectLinkType = Field(default="Live Demo")
    is_primary: bool = Field(default=False)
    is_visible: bool = Field(default=True)
    display_order: int = Field(default=0, ge=0)

    @field_validator("label")
    @classmethod
    def clean_label(cls, v: str) -> str:
        clean = v.strip()
        if not clean:
            raise ValueError("Link label cannot be empty.")
        return clean

    @field_validator("url")
    @classmethod
    def check_url(cls, v: str) -> str:
        return validate_url_protocol(v)


class ProjectLinkCreate(ProjectLinkBase):
    pass


class ProjectLinkUpdate(ProjectLinkBase):
    pass


class ProjectLinkPatch(BaseModel):
    label: Optional[str] = Field(None, min_length=1, max_length=100)
    url: Optional[str] = Field(None, min_length=1, max_length=1000)
    link_type: Optional[ProjectLinkType] = None
    is_primary: Optional[bool] = None
    is_visible: Optional[bool] = None
    display_order: Optional[int] = Field(None, ge=0)

    @field_validator("label")
    @classmethod
    def clean_label(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            clean = v.strip()
            if not clean:
                raise ValueError("Link label cannot be empty.")
            return clean
        return v

    @field_validator("url")
    @classmethod
    def check_url(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            return validate_url_protocol(v)
        return v


class ProjectLinkOut(ProjectLinkBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    project_id: int
    created_at: datetime
    updated_at: datetime


class ProjectLinkReorderItem(BaseModel):
    id: int
    display_order: int = Field(..., ge=0)


# -----------------------------------------------------------------------------
# Associated Skill Schemas
# -----------------------------------------------------------------------------

class ProjectSkillOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    category: str
    rating: int
    level_label: str


# -----------------------------------------------------------------------------
# Project Schemas
# -----------------------------------------------------------------------------

class ProjectBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=150)
    short_description: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    status: Optional[ProjectStatus] = "Completed"
    start_month: Optional[int] = Field(None, ge=1, le=12)
    start_year: Optional[int] = Field(None, gt=0)
    end_month: Optional[int] = Field(None, ge=1, le=12)
    end_year: Optional[int] = Field(None, gt=0)
    is_current: bool = Field(default=False)
    is_featured: bool = Field(default=False)
    is_visible: bool = Field(default=True)
    display_order: int = Field(default=0, ge=0)

    @field_validator("name")
    @classmethod
    def clean_name(cls, v: str) -> str:
        clean = v.strip()
        if not clean:
            raise ValueError("Project name cannot be empty or whitespace-only.")
        return clean

    @field_validator("short_description")
    @classmethod
    def clean_short_desc(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            clean = v.strip()
            return clean if clean else None
        return v

    @field_validator("description")
    @classmethod
    def clean_desc(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            clean = v.strip()
            return clean if clean else None
        return v

    @model_validator(mode="after")
    def validate_dates(self) -> "ProjectBase":
        if self.is_current:
            if self.end_month is not None or self.end_year is not None:
                raise ValueError("Active/current projects cannot have an end date.")
        else:
            if self.start_year is not None and self.end_year is not None:
                if self.end_year < self.start_year:
                    raise ValueError("End year cannot be earlier than start year.")
                elif self.end_year == self.start_year:
                    if self.start_month is not None and self.end_month is not None:
                        if self.end_month < self.start_month:
                            raise ValueError("End month cannot be earlier than start month within the same year.")
        return self


class ProjectCreate(ProjectBase):
    technologies: Optional[List[Union[str, ProjectTechnologyInput]]] = Field(
        default=None,
        description="List of technology names or structured technology inputs"
    )
    links: Optional[List[ProjectLinkCreate]] = Field(
        default=None,
        description="Multiple deployment or demo links"
    )
    skill_ids: Optional[List[int]] = Field(
        default=None,
        description="IDs of existing skills to associate with this project"
    )


class ProjectUpdate(ProjectBase):
    technologies: Optional[List[Union[str, ProjectTechnologyInput]]] = None
    links: Optional[List[ProjectLinkCreate]] = None
    skill_ids: Optional[List[int]] = None


class ProjectPatch(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=150)
    short_description: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    status: Optional[ProjectStatus] = None
    start_month: Optional[int] = Field(None, ge=1, le=12)
    start_year: Optional[int] = Field(None, gt=0)
    end_month: Optional[int] = Field(None, ge=1, le=12)
    end_year: Optional[int] = Field(None, gt=0)
    is_current: Optional[bool] = None
    is_featured: Optional[bool] = None
    is_visible: Optional[bool] = None
    display_order: Optional[int] = Field(None, ge=0)
    technologies: Optional[List[Union[str, ProjectTechnologyInput]]] = None
    links: Optional[List[ProjectLinkCreate]] = None
    skill_ids: Optional[List[int]] = None

    @field_validator("name")
    @classmethod
    def clean_name(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            clean = v.strip()
            if not clean:
                raise ValueError("Project name cannot be empty.")
            return clean
        return v


class ProjectOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    profile_id: Optional[int] = None
    name: str
    short_description: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = "Completed"
    start_month: Optional[int] = None
    start_year: Optional[int] = None
    end_month: Optional[int] = None
    end_year: Optional[int] = None
    is_current: bool = False
    is_featured: bool = False
    is_visible: bool = True
    visibility: bool = True
    display_order: int = 0
    ordering: int = 0
    technologies: List[ProjectTechnologyOut] = Field(default_factory=list)
    links: List[ProjectLinkOut] = Field(default_factory=list)
    skills: List[ProjectSkillOut] = Field(default_factory=list)
    primary_link: Optional[ProjectLinkOut] = None
    created_at: datetime
    updated_at: datetime


class ProjectReorderItem(BaseModel):
    id: int
    display_order: int = Field(..., ge=0)


class ProjectCategoriesOut(BaseModel):
    statuses: List[str]
    link_types: List[str]
    tech_categories: List[str]


# -----------------------------------------------------------------------------
# GitHub Extraction Schemas
# -----------------------------------------------------------------------------

class GitHubExtractionRequest(BaseModel):
    github_url: str = Field(..., description="GitHub Profile URL (e.g. https://github.com/username) or Repository URL")
    custom_token: Optional[str] = Field(None, description="Optional GitHub Personal Access Token for higher rate limits")

    @field_validator("github_url")
    @classmethod
    def clean_github_url(cls, v: str) -> str:
        clean = v.strip()
        if not clean:
            raise ValueError("GitHub URL cannot be empty.")
        return clean


class ExtractedProjectLinkOut(BaseModel):
    label: str
    url: str
    link_type: str = "GitHub"
    is_primary: bool = False
    is_visible: bool = True
    display_order: int = 0


class ExtractedTechnologyOut(BaseModel):
    name: str
    category: str = "Other"


class ExtractedProjectOut(BaseModel):
    name: str
    short_description: Optional[str] = None
    description: Optional[str] = None
    full_ai_dossier: Optional[str] = None
    status: Optional[str] = "Completed"
    technologies: List[ExtractedTechnologyOut] = Field(default_factory=list)
    links: List[ExtractedProjectLinkOut] = Field(default_factory=list)
    stars: int = 0
    forks: int = 0
    repo_url: str
    homepage_url: Optional[str] = None
    is_featured: bool = False
    start_month: Optional[int] = None
    start_year: Optional[int] = None
    end_month: Optional[int] = None
    end_year: Optional[int] = None


class GitHubExtractionResponse(BaseModel):
    username: str
    source_type: str
    projects_count: int
    projects: List[ExtractedProjectOut]


class ProjectBulkImportRequest(BaseModel):
    projects: List[ProjectCreate] = Field(..., min_length=1, description="List of projects to import in bulk")


# -----------------------------------------------------------------------------
# GitHub Account Link & Sync Schemas
# -----------------------------------------------------------------------------

class GitHubAccountLinkCreate(BaseModel):
    github_url: str = Field(..., description="GitHub Profile URL (e.g. https://github.com/username) or handle")
    custom_token: Optional[str] = Field(None, description="Optional GitHub Personal Access Token")
    auto_sync: bool = Field(default=True, description="Enable automatic periodic and webhook syncing")
    webhook_secret: Optional[str] = Field(None, description="Optional secret for GitHub webhook verification")

    @field_validator("github_url")
    @classmethod
    def clean_github_url(cls, v: str) -> str:
        clean = v.strip()
        if not clean:
            raise ValueError("GitHub URL cannot be empty.")
        return clean


class GitHubAccountLinkUpdate(BaseModel):
    github_url: Optional[str] = None
    custom_token: Optional[str] = None
    auto_sync: Optional[bool] = None
    webhook_secret: Optional[str] = None


class GitHubAccountLinkOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    profile_id: int
    github_url: str
    username: str
    auto_sync: bool
    webhook_secret: Optional[str] = None
    last_synced_at: Optional[datetime] = None
    last_sync_status: str = "idle"
    last_sync_summary: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class GitHubSyncResultOut(BaseModel):
    status: str
    message: str
    username: str
    total_found: int
    created_count: int
    updated_count: int
    created_projects: List[str]
    updated_projects: List[str]
    synced_at: datetime


class ProjectAiDossierGenerateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=200, description="Project name")
    raw_description: Optional[str] = Field(None, description="Optional short summary or raw notes about the project")
    language: Optional[str] = Field(None, description="Primary programming language")
    technologies: List[Union[str, Dict[str, Any]]] = Field(default_factory=list, description="List of tech names or tech objects")
    topics: List[str] = Field(default_factory=list, description="Keywords or topic tags")
    links: List[Dict[str, Any]] = Field(default_factory=list, description="Optional links")
    stars: int = Field(0, ge=0)
    forks: int = Field(0, ge=0)


class ProjectAiDossierGenerateResponse(BaseModel):
    short_description: str
    description: str



