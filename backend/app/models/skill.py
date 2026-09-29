from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Boolean, Text, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship, synonym
from app.core.database import Base

SKILL_LEVEL_MAP = {
    1: "Beginner",
    2: "Novice",
    3: "Intermediate",
    4: "Proficient",
    5: "Advanced",
    6: "Expert",
    7: "Master"
}


class Skill(Base):
    __tablename__ = "skills"

    id = Column(Integer, primary_key=True, index=True)
    profile_id = Column(Integer, ForeignKey("profiles.id", ondelete="CASCADE"), nullable=True, index=True)
    name = Column(String(100), nullable=False)
    category = Column(String(80), nullable=False, default="Technical")
    description = Column(String(255), nullable=True)
    rating = Column(Integer, nullable=False)  # 1 to 7
    is_visible = Column(Boolean, default=True, nullable=False)
    display_order = Column(Integer, default=0, nullable=False)
    metadata_info = Column(Text, default="{}", nullable=False)  # Additional notes or tags
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    # Aliases via SQLAlchemy synonym
    visibility = synonym("is_visible")
    ordering = synonym("display_order")

    __table_args__ = (
        CheckConstraint("rating >= 1 AND rating <= 7", name="check_skill_rating"),
        CheckConstraint("display_order >= 0", name="check_skill_display_order"),
        CheckConstraint("length(trim(name)) > 0", name="check_skill_name_not_empty"),
    )

    profile = relationship("Profile", back_populates="skills")

    @property
    def level_label(self) -> str:
        return SKILL_LEVEL_MAP.get(self.rating, "Unknown")
