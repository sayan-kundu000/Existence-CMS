from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.education import Education
from app.repositories.base import BaseRepository


class EducationRepository(BaseRepository[Education]):
    def __init__(self, db: Session):
        super().__init__(Education, db)

    def list_ordered(self, skip: int = 0, limit: int = 100) -> List[Education]:
        """
        Returns education records ordered by:
        1. Academic level hierarchy: Doctorate -> Post Graduate -> Graduate -> Diploma -> High School -> Matriculation
        2. Explicit manual ordering (ordering / display_order asc)
        3. Currently active studies first (currently_studying desc)
        4. Starting year and month descending (most recent first)
        """
        from sqlalchemy import case

        level_hierarchy = case(
            {
                "Doctorate": 1,
                "Post Graduate": 2,
                "Graduate": 3,
                "Diploma": 4,
                "Undergraduate": 4,
                "High School": 5,
                "Matriculation": 6,
            },
            value=Education.level,
            else_=99
        )

        return (
            self.db.query(Education)
            .order_by(
                level_hierarchy.asc(),
                Education.ordering.asc(),
                Education.currently_studying.desc(),
                Education.start_year.desc().nullslast(),
                Education.start_month.desc().nullslast(),
                Education.created_at.desc()
            )
            .offset(skip)
            .limit(limit)
            .all()
        )

    def find_duplicate(
        self,
        level: str,
        stream: Optional[str],
        starting_month_year: str,
        institution: Optional[str] = None,
        exclude_id: Optional[int] = None
    ) -> Optional[Education]:
        query = self.db.query(Education).filter(
            func.lower(func.trim(Education.level)) == level.strip().lower(),
            func.lower(func.trim(Education.starting_month_year)) == starting_month_year.strip().lower()
        )
        if stream and stream.strip():
            query = query.filter(func.lower(func.trim(Education.stream)) == stream.strip().lower())
        else:
            query = query.filter((Education.stream.is_(None)) | (Education.stream == ""))

        if institution and institution.strip():
            query = query.filter(func.lower(func.trim(Education.institution)) == institution.strip().lower())
        if exclude_id:
            query = query.filter(Education.id != exclude_id)
        return query.first()
