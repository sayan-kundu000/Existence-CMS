from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime
from app.core.database import Base


class HobbyInterest(Base):
    __tablename__ = "hobbies_interests"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(String(20), nullable=False)  # "hobby" or "interest"
    name = Column(String(100), nullable=False)
    category = Column(String(80), nullable=True)
    icon = Column(String(50), nullable=True)
    ordering = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
