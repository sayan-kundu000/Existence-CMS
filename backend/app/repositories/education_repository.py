from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.education import Education
from app.repositories.base import BaseRepository


class EducationRepository(BaseRepository[Education]):
    def __init__(self, db: Session):
        super().__init__(Education, db)

    def list_ordered(self, skip: int = 0, limit: int = 100) -> List[Education]:
        return (
            self.db.query(Education)
            .order_by(Education.ordering.asc(), Education.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
