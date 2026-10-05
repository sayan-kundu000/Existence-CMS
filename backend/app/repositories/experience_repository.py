from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.experience import Experience
from app.repositories.base import BaseRepository


class ExperienceRepository(BaseRepository[Experience]):
    def __init__(self, db: Session):
        super().__init__(Experience, db)

    def list_ordered(self, skip: int = 0, limit: int = 100) -> List[Experience]:
        """
        Returns work experience records ordered in descending order of timelines:
        1. Currently active employment first (currently_working desc)
        2. Ending year and month descending (most recent conclusion first)
        3. Starting year and month descending (most recent start first)
        4. Manual display ordering and creation fallback
        """
        return (
            self.db.query(Experience)
            .order_by(
                Experience.currently_working.desc(),
                Experience.end_year.desc().nullslast(),
                Experience.end_month.desc().nullslast(),
                Experience.start_year.desc().nullslast(),
                Experience.start_month.desc().nullslast(),
                Experience.ordering.asc(),
                Experience.created_at.desc()
            )
            .offset(skip)
            .limit(limit)
            .all()
        )

    def find_duplicate(
        self,
        role: str,
        employer: str,
        starting_month_year: str,
        exclude_id: Optional[int] = None
    ) -> Optional[Experience]:
        query = self.db.query(Experience).filter(
            func.lower(func.trim(Experience.role)) == role.strip().lower(),
            func.lower(func.trim(Experience.employer)) == employer.strip().lower(),
            func.lower(func.trim(Experience.starting_month_year)) == starting_month_year.strip().lower()
        )
        if exclude_id:
            query = query.filter(Experience.id != exclude_id)
        return query.first()
