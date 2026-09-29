import uuid
from datetime import datetime, timezone
from sqlalchemy import (
    Column, Integer, Float, String, Text, Boolean, DateTime, ForeignKey,
    UniqueConstraint, CheckConstraint
)
from sqlalchemy.orm import relationship, synonym
from app.core.database import Base

VALID_SESSION_STATUSES = ("NOT_STARTED", "IN_PROGRESS", "COMPLETED", "ABANDONED")


class AssessmentDefinition(Base):
    __tablename__ = "assessment_definitions"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(30), unique=True, nullable=False, index=True)  # "MBTI", "DISC", "BIG_FIVE"
    name = Column(String(120), nullable=False)
    version = Column(String(20), default="1.0", nullable=False)
    tagline = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    question_count = Column(Integer, default=0, nullable=False)
    estimated_minutes = Column(Integer, default=5, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    assessment_type = Column(String(30), default="", nullable=True)
    is_configured = Column(Boolean, default=True, nullable=True)

    def __init__(self, **kwargs):
        if "code" in kwargs and "assessment_type" not in kwargs:
            kwargs["assessment_type"] = kwargs["code"]
        elif "assessment_type" in kwargs and "code" not in kwargs:
            kwargs["code"] = kwargs["assessment_type"]
        if "is_active" in kwargs and "is_configured" not in kwargs:
            kwargs["is_configured"] = kwargs["is_active"]
        super().__init__(**kwargs)

    questions = relationship("AssessmentQuestion", back_populates="definition", cascade="all, delete-orphan")
    sessions = relationship("AssessmentSession", back_populates="definition")


class AssessmentQuestion(Base):
    __tablename__ = "assessment_questions"

    id = Column(String(50), primary_key=True, index=True)
    assessment_definition_id = Column(Integer, ForeignKey("assessment_definitions.id", ondelete="CASCADE"), nullable=True, index=True)
    definition_type = Column(String(30), nullable=True, index=True)
    question_key = Column(String(50), nullable=True)
    dimension = Column(String(50), nullable=False, index=True)
    question_text = Column(Text, nullable=False)
    positive_pole = Column(String(100), nullable=True)
    negative_pole = Column(String(100), nullable=True)
    scale_type = Column(String(30), default="likert_5", nullable=False)
    scoring_configuration = Column(Text, default="{}", nullable=False)
    question_order = Column(Integer, default=0, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    text = Column(Text, default="", nullable=True)
    ordering = Column(Integer, default=0, nullable=True)

    def __init__(self, **kwargs):
        if "question_text" in kwargs and "text" not in kwargs:
            kwargs["text"] = kwargs["question_text"]
        elif "text" in kwargs and "question_text" not in kwargs:
            kwargs["question_text"] = kwargs["text"]
        if "question_order" in kwargs and "ordering" not in kwargs:
            kwargs["ordering"] = kwargs["question_order"]
        elif "ordering" in kwargs and "question_order" not in kwargs:
            kwargs["question_order"] = kwargs["ordering"]
        super().__init__(**kwargs)

    definition = relationship("AssessmentDefinition", back_populates="questions")


class AssessmentSession(Base):
    __tablename__ = "assessment_sessions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    profile_id = Column(Integer, ForeignKey("profiles.id", ondelete="SET NULL"), nullable=True, index=True)
    assessment_definition_id = Column(Integer, ForeignKey("assessment_definitions.id", ondelete="CASCADE"), nullable=True, index=True)
    assessment_type = Column(String(30), nullable=False, index=True)  # "MBTI", "DISC", "BIG_FIVE"
    status = Column(String(20), default="IN_PROGRESS", nullable=False)  # "NOT_STARTED", "IN_PROGRESS", "COMPLETED", "ABANDONED"
    started_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    client_info = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    __table_args__ = (
        CheckConstraint(
            f"status IN {VALID_SESSION_STATUSES}",
            name="check_assessment_session_status"
        ),
    )

    definition = relationship("AssessmentDefinition", back_populates="sessions")
    profile = relationship("Profile")
    responses = relationship("AssessmentResponse", back_populates="session", cascade="all, delete-orphan")
    result = relationship("AssessmentResult", back_populates="session", uselist=False, cascade="all, delete-orphan")


class AssessmentResponse(Base):
    __tablename__ = "assessment_responses"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(36), ForeignKey("assessment_sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    question_id = Column(String(50), nullable=False, index=True)
    dimension = Column(String(50), nullable=False)
    response_value = Column(Integer, nullable=False)
    answered_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    # Alias
    selected_value = synonym("response_value")

    __table_args__ = (
        # Mandatory constraint from Section 25: prevents duplicate responses for the same question per session
        UniqueConstraint("session_id", "question_id", name="uq_assessment_response_session_question"),
    )

    session = relationship("AssessmentSession", back_populates="responses")


class AssessmentResult(Base):
    __tablename__ = "assessment_results"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(36), ForeignKey("assessment_sessions.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    assessment_definition_id = Column(Integer, ForeignKey("assessment_definitions.id", ondelete="SET NULL"), nullable=True, index=True)
    assessment_type = Column(String(30), nullable=False, index=True)
    result_code = Column(String(50), nullable=False)
    result_title = Column(String(120), nullable=False)
    result_version = Column(String(20), default="1.0", nullable=False)
    scores_json = Column(Text, nullable=False)
    soft_skills_json = Column(Text, default="[]", nullable=False)
    strengths_json = Column(Text, default="[]", nullable=False)
    weaknesses_json = Column(Text, default="[]", nullable=False)
    summary = Column(Text, nullable=True)
    summary_data = Column(Text, nullable=True)
    completed_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    session = relationship("AssessmentSession", back_populates="result")
    trait_scores = relationship("PersonalityTraitScore", back_populates="result", cascade="all, delete-orphan")
    soft_skills = relationship("SoftSkillRecord", back_populates="result", cascade="all, delete-orphan")
    strengths = relationship("StrengthRecord", back_populates="result", cascade="all, delete-orphan")
    weaknesses = relationship("WeaknessRecord", back_populates="result", cascade="all, delete-orphan")


class PersonalityTraitScore(Base):
    __tablename__ = "personality_trait_scores"

    id = Column(Integer, primary_key=True, index=True)
    result_id = Column(Integer, ForeignKey("assessment_results.id", ondelete="CASCADE"), nullable=False, index=True)
    trait_code = Column(String(80), nullable=False, index=True)
    score = Column(Float, nullable=False)
    normalized_score = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    # Aliases
    trait_name = synonym("trait_code")
    score_value = synonym("score")
    percentage = synonym("normalized_score")

    result = relationship("AssessmentResult", back_populates="trait_scores")


class SoftSkillRecord(Base):
    __tablename__ = "soft_skill_records"

    id = Column(Integer, primary_key=True, index=True)
    profile_id = Column(Integer, ForeignKey("profiles.id", ondelete="CASCADE"), nullable=True, index=True)
    result_id = Column(Integer, ForeignKey("assessment_results.id", ondelete="CASCADE"), nullable=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(String(255), nullable=True)
    category = Column(String(80), default="General", nullable=False)
    source = Column(String(50), default="ASSESSMENT", nullable=False)  # "MBTI", "DISC", "BIG_FIVE", "SYNTHESIS", "MANUAL"
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    profile = relationship("Profile", back_populates="soft_skills")
    result = relationship("AssessmentResult", back_populates="soft_skills")


class StrengthRecord(Base):
    __tablename__ = "strength_records"

    id = Column(Integer, primary_key=True, index=True)
    profile_id = Column(Integer, ForeignKey("profiles.id", ondelete="CASCADE"), nullable=True, index=True)
    result_id = Column(Integer, ForeignKey("assessment_results.id", ondelete="CASCADE"), nullable=True, index=True)
    title = Column(String(255), nullable=False)
    source = Column(String(50), default="ASSESSMENT", nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    description = synonym("title")

    profile = relationship("Profile", back_populates="strengths")
    result = relationship("AssessmentResult", back_populates="strengths")


class WeaknessRecord(Base):
    __tablename__ = "weakness_records"

    id = Column(Integer, primary_key=True, index=True)
    profile_id = Column(Integer, ForeignKey("profiles.id", ondelete="CASCADE"), nullable=True, index=True)
    result_id = Column(Integer, ForeignKey("assessment_results.id", ondelete="CASCADE"), nullable=True, index=True)
    title = Column(String(255), nullable=False)
    source = Column(String(50), default="ASSESSMENT", nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    description = synonym("title")

    profile = relationship("Profile", back_populates="weaknesses")
    result = relationship("AssessmentResult", back_populates="weaknesses")


class PersonalitySynthesis(Base):
    __tablename__ = "personality_synthesis"

    id = Column(Integer, primary_key=True, index=True)
    key_soft_skills = Column(Text, default="[]", nullable=False)
    key_strengths = Column(Text, default="[]", nullable=False)
    key_weaknesses = Column(Text, default="[]", nullable=False)
    summary_notes = Column(Text, nullable=True)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
