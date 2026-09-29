from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship, synonym
from app.core.database import Base


class Hobby(Base):
    __tablename__ = "hobbies"

    id = Column(Integer, primary_key=True, index=True)
    profile_id = Column(Integer, ForeignKey("profiles.id", ondelete="CASCADE"), nullable=True, index=True)
    name = Column(String(100), nullable=False)
    category = Column(String(80), nullable=True)
    icon = Column(String(50), nullable=True)
    is_visible = Column(Boolean, default=True, nullable=False)
    display_order = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    # Aliases via SQLAlchemy synonym
    visibility = synonym("is_visible")
    ordering = synonym("display_order")

    __table_args__ = (
        CheckConstraint("display_order >= 0", name="check_hobby_display_order"),
        CheckConstraint("length(trim(name)) > 0", name="check_hobby_name_not_empty"),
    )

    profile = relationship("Profile", back_populates="hobbies")
