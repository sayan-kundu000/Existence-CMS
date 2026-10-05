import re
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    Text,
    DateTime,
    ForeignKey,
    CheckConstraint,
    UniqueConstraint,
    Index,
    func
)
from sqlalchemy.orm import relationship, validates, synonym
from app.core.database import Base

PROJECT_STATUSES = ("Planned", "In Progress", "Completed", "Archived")

LINK_TYPES = (
    "Live Demo",
    "Deployment",
    "GitHub",
    "Repository",
    "Documentation",
    "API",
    "Video Demo",
    "Case Study",
    "Other"
)

TECH_CATEGORIES = (
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
)


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    profile_id = Column(Integer, ForeignKey("profiles.id", ondelete="CASCADE"), nullable=True, index=True)
    name = Column(String(150), nullable=False)
    short_description = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)  # Detailed description
    status = Column(String(50), nullable=True, default="Completed")

    # Normalized numeric period fields (aligned with Experience & Education)
    start_month = Column(Integer, nullable=True)
    start_year = Column(Integer, nullable=True)
    end_month = Column(Integer, nullable=True)
    end_year = Column(Integer, nullable=True)

    is_current = Column(Boolean, default=False, nullable=False)
    is_featured = Column(Boolean, default=False, nullable=False)
    is_visible = Column(Boolean, default=True, nullable=False)
    display_order = Column(Integer, default=0, nullable=False)

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    # Synonyms for seamless domain and legacy property compatibility
    visibility = synonym("is_visible")
    ordering = synonym("display_order")
    currently_active = synonym("is_current")

    __table_args__ = (
        CheckConstraint("length(trim(name)) > 0", name="check_project_name_not_empty"),
        CheckConstraint("display_order >= 0", name="check_project_display_order"),
        CheckConstraint("start_month IS NULL OR (start_month >= 1 AND start_month <= 12)", name="check_project_start_month"),
        CheckConstraint("end_month IS NULL OR (end_month >= 1 AND end_month <= 12)", name="check_project_end_month"),
        CheckConstraint("start_year IS NULL OR start_year > 0", name="check_project_start_year"),
        CheckConstraint("end_year IS NULL OR end_year > 0", name="check_project_end_year"),
        CheckConstraint(f"status IS NULL OR status IN {PROJECT_STATUSES}", name="check_project_status"),
        CheckConstraint(
            "is_current = 0 OR is_current = FALSE OR (end_month IS NULL AND end_year IS NULL)",
            name="check_project_current_no_end"
        ),
        CheckConstraint(
            "is_current = 1 OR is_current = TRUE OR start_year IS NULL OR end_year IS NULL OR ("
            "end_year > start_year OR (end_year = start_year AND (end_month IS NULL OR start_month IS NULL OR end_month >= start_month))"
            ")",
            name="check_project_dates"
        ),
        Index("ix_projects_profile_lower_name", "profile_id", func.lower(name), unique=True),
        Index("ix_projects_visibility", "is_visible"),
        Index("ix_projects_is_featured", "is_featured"),
        Index("ix_projects_status", "status"),
    )

    profile = relationship("Profile", back_populates="projects")
    links = relationship("ProjectLink", back_populates="project", cascade="all, delete-orphan", order_by="ProjectLink.display_order")
    project_technologies = relationship("ProjectTechnology", back_populates="project", cascade="all, delete-orphan", order_by="ProjectTechnology.display_order")
    project_skills = relationship("ProjectSkill", back_populates="project", cascade="all, delete-orphan")

    @validates("name")
    def validate_name(self, key, value):
        if not value or not isinstance(value, str):
            raise ValueError("Project name must not be empty.")
        clean = value.strip()
        if not clean:
            raise ValueError("Project name must not be empty or whitespace-only.")
        if len(clean) > 150:
            raise ValueError("Project name cannot exceed 150 characters.")
        return clean

    @property
    def primary_link(self) -> Optional["ProjectLink"]:
        for link in self.links:
            if link.is_primary:
                return link
        return None


class ProjectLink(Base):
    __tablename__ = "project_links"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    label = Column(String(100), nullable=False)
    url = Column(String(1000), nullable=False)
    link_type = Column(String(50), default="Live Demo", nullable=False)
    is_primary = Column(Boolean, default=False, nullable=False)
    is_visible = Column(Boolean, default=True, nullable=False)
    display_order = Column(Integer, default=0, nullable=False)

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    visibility = synonym("is_visible")
    ordering = synonym("display_order")

    __table_args__ = (
        CheckConstraint("length(trim(label)) > 0", name="check_project_link_label_not_empty"),
        CheckConstraint("length(trim(url)) > 0", name="check_project_link_url_not_empty"),
        CheckConstraint("display_order >= 0", name="check_project_link_display_order"),
        CheckConstraint(f"link_type IN {LINK_TYPES}", name="check_project_link_type"),
        Index("ix_project_links_project_id", "project_id"),
        Index("ix_project_links_is_primary", "project_id", "is_primary"),
    )

    project = relationship("Project", back_populates="links")

    @validates("label")
    def validate_label(self, key, value):
        if not value or not isinstance(value, str):
            raise ValueError("Link label must not be empty.")
        clean = value.strip()
        if not clean:
            raise ValueError("Link label must not be whitespace-only.")
        if len(clean) > 100:
            raise ValueError("Link label cannot exceed 100 characters.")
        return clean

    @validates("url")
    def validate_url(self, key, value):
        if not value or not isinstance(value, str):
            raise ValueError("Link URL must not be empty.")
        clean = value.strip()
        if not clean:
            raise ValueError("Link URL must not be whitespace-only.")
        if len(clean) > 1000:
            raise ValueError("Link URL cannot exceed 1000 characters.")
        if clean.lower().startswith("javascript:") or clean.lower().startswith("data:"):
            raise ValueError("Unsafe URL scheme detected.")
        if not (clean.startswith("http://") or clean.startswith("https://")):
            raise ValueError("URL must start with http:// or https://.")
        return clean


class Technology(Base):
    __tablename__ = "technologies"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)
    category = Column(String(50), default="Other", nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    __table_args__ = (
        CheckConstraint("length(trim(name)) > 0", name="check_tech_name_not_empty"),
        CheckConstraint(f"category IN {TECH_CATEGORIES}", name="check_tech_category"),
        Index("ix_technologies_lower_name", func.lower(name), unique=True),
    )

    project_technologies = relationship("ProjectTechnology", back_populates="technology", cascade="all, delete-orphan")

    @validates("name")
    def validate_name(self, key, value):
        if not value or not isinstance(value, str):
            raise ValueError("Technology name must not be empty.")
        clean = value.strip()
        if not clean:
            raise ValueError("Technology name cannot be empty.")
        if len(clean) > 100:
            raise ValueError("Technology name cannot exceed 100 characters.")
        return clean


class ProjectTechnology(Base):
    __tablename__ = "project_technologies"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    technology_id = Column(Integer, ForeignKey("technologies.id", ondelete="CASCADE"), nullable=False, index=True)
    display_order = Column(Integer, default=0, nullable=False)

    __table_args__ = (
        UniqueConstraint("project_id", "technology_id", name="uq_project_technology"),
        CheckConstraint("display_order >= 0", name="check_proj_tech_display_order"),
    )

    project = relationship("Project", back_populates="project_technologies")
    technology = relationship("Technology", back_populates="project_technologies")


class ProjectSkill(Base):
    __tablename__ = "project_skills"

    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), primary_key=True)
    skill_id = Column(Integer, ForeignKey("skills.id", ondelete="CASCADE"), primary_key=True)

    project = relationship("Project", back_populates="project_skills")
    skill = relationship("Skill")


class GitHubAccountLink(Base):
    __tablename__ = "github_account_links"

    id = Column(Integer, primary_key=True, index=True)
    profile_id = Column(Integer, ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    github_url = Column(String(255), nullable=False)
    username = Column(String(100), nullable=False)
    custom_token = Column(String(255), nullable=True)
    auto_sync = Column(Boolean, default=True, nullable=False)
    webhook_secret = Column(String(100), nullable=True)
    last_synced_at = Column(DateTime(timezone=True), nullable=True)
    last_sync_status = Column(String(50), default="idle", nullable=False)
    last_sync_summary = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    profile = relationship("Profile", backref="github_link_config")
