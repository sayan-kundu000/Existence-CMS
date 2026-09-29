from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.experience import Experience
from app.repositories.base import BaseRepository


class ExperienceRepository(BaseRepository[Experience]):
    def __init__(self, db: Session):
        super().__init__(Experience, db)

    def list_ordered(self, skip: int = 0, limit: int = 100) -> List[Experience]:
        return (
            self.db.query(Experience)
            .order_by(Experience.ordering.asc(), Experience.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
