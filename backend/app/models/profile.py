import re
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship, validates
from app.core.database import Base


class Profile(Base):
    __tablename__ = "profiles"

    id = Column(Integer, primary_key=True, index=True)
    # Strictly nullable/empty by default to honor "DO NOT INVENT PERSONAL CONTENT"
    name = Column(String(120), nullable=True)
    email_ids = Column(Text, default="[]", nullable=False)  # JSON-encoded array of emails (backwards-compatible)
    mobile_number = Column(String(30), nullable=True)
    linkedin = Column(String(255), nullable=True)
    about = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    # Relational child entities with explicit cascade ownership
    emails = relationship("ProfileEmail", back_populates="profile", cascade="all, delete-orphan", order_by="ProfileEmail.display_order")
    educations = relationship("Education", back_populates="profile", cascade="all, delete-orphan")
    work_experiences = relationship("Experience", back_populates="profile", cascade="all, delete-orphan")
    skills = relationship("Skill", back_populates="profile", cascade="all, delete-orphan")
    hobbies = relationship("Hobby", back_populates="profile", cascade="all, delete-orphan")
    interests = relationship("Interest", back_populates="profile", cascade="all, delete-orphan")
    soft_skills = relationship("SoftSkillRecord", back_populates="profile", cascade="all, delete-orphan")
    strengths = relationship("StrengthRecord", back_populates="profile", cascade="all, delete-orphan")
    weaknesses = relationship("WeaknessRecord", back_populates="profile", cascade="all, delete-orphan")


class ProfileEmail(Base):
    __tablename__ = "profile_emails"

    id = Column(Integer, primary_key=True, index=True)
    profile_id = Column(Integer, ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    email = Column(String(255), nullable=False, index=True)
    label = Column(String(50), default="Primary", nullable=False)
    is_primary = Column(Boolean, default=False, nullable=False)
    display_order = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    __table_args__ = (
        CheckConstraint("display_order >= 0", name="check_profile_email_display_order"),
    )

    profile = relationship("Profile", back_populates="emails")

    @validates("email")
    def validate_email_format(self, key, value):
        if not value or not isinstance(value, str):
            raise ValueError("Email address must not be empty.")
        clean = value.strip()
        if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", clean):
            raise ValueError(f"Invalid email address format: {value}")
        return clean
