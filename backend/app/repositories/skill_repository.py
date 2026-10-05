from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, or_
from app.models.skill import Skill
from app.repositories.base import BaseRepository


class SkillRepository(BaseRepository[Skill]):
    def __init__(self, db: Session):
        super().__init__(Skill, db)

    def get_by_id(self, skill_id: int) -> Optional[Skill]:
        """Retrieve single skill by primary key ID."""
        return self.db.query(Skill).filter(Skill.id == skill_id).first()

    def find_by_name(
        self,
        name: str,
        profile_id: Optional[int] = None,
        exclude_id: Optional[int] = None
    ) -> Optional[Skill]:
        """
        Find skill by case-insensitive, whitespace-trimmed name for a given profile.
        Used for race-condition-resistant duplicate prevention.
        """
        normalized_name = name.strip().lower()
        query = self.db.query(Skill).filter(
            func.lower(func.trim(Skill.name)) == normalized_name
        )
        if profile_id is not None:
            query = query.filter(Skill.profile_id == profile_id)
        if exclude_id is not None:
            query = query.filter(Skill.id != exclude_id)
        return query.first()

    def list_skills(
        self,
        profile_id: Optional[int] = None,
        include_hidden: bool = False,
        category: Optional[str] = None,
        domain: Optional[str] = None,
        search: Optional[str] = None,
        rating: Optional[int] = None,
        sort_by: str = "rating"
    ) -> List[Skill]:
        """
        Query skills with optional filtering, search, and deterministic ordering.
        Default ordering: rating descending (Mastery Ratings Level 7 down to Level 1), display_order asc, name asc.
        """
        query = self.db.query(Skill)

        if profile_id is not None:
            query = query.filter(Skill.profile_id == profile_id)

        if not include_hidden:
            query = query.filter(Skill.is_visible == True)

        if category and category.strip().lower() != "all":
            cat_clean = category.strip()
            cat_lower = cat_clean.lower()
            query = query.filter(
                or_(
                    func.lower(Skill.category) == cat_lower,
                    Skill.category.ilike(f"%, {cat_clean}%"),
                    Skill.category.ilike(f"%{cat_clean}, %"),
                    Skill.category.ilike(f"%,{cat_clean}%"),
                    Skill.category.ilike(f"%{cat_clean}%"),
                )
            )

        if domain and domain.strip().lower() != "all":
            dom_clean = domain.strip()
            dom_lower = dom_clean.lower()
            query = query.filter(
                or_(
                    func.lower(Skill.domain) == dom_lower,
                    Skill.domain.ilike(f"%, {dom_clean}%"),
                    Skill.domain.ilike(f"%{dom_clean}, %"),
                    Skill.domain.ilike(f"%,{dom_clean}%"),
                    Skill.domain.ilike(f"%{dom_clean}%"),
                )
            )

        if rating is not None and 1 <= rating <= 7:
            query = query.filter(Skill.rating == rating)

        if search:
            pattern = f"%{search.strip()}%"
            query = query.filter(
                or_(
                    Skill.name.ilike(pattern),
                    Skill.domain.ilike(pattern),
                    Skill.category.ilike(pattern),
                    Skill.description.ilike(pattern)
                )
            )

        if sort_by == "order":
            query = query.order_by(Skill.display_order.asc(), Skill.name.asc(), Skill.id.asc())
        elif sort_by == "name":
            query = query.order_by(Skill.name.asc(), Skill.display_order.asc())
        else:
            # Deterministic default: rating descending (Mastery Ratings Level 7 down to Level 1), display_order asc, name asc, id asc
            query = query.order_by(Skill.rating.desc(), Skill.display_order.asc(), Skill.name.asc(), Skill.id.asc())

        return query.all()

    def get_max_display_order(self, profile_id: Optional[int] = None) -> int:
        """Get the current maximum display_order for ordering calculation."""
        query = self.db.query(func.coalesce(func.max(Skill.display_order), -1))
        if profile_id is not None:
            query = query.filter(Skill.profile_id == profile_id)
        return query.scalar() or -1

    def count(self, profile_id: Optional[int] = None, include_hidden: bool = True) -> int:
        """Count total skills matching criteria."""
        query = self.db.query(func.count(Skill.id))
        if profile_id is not None:
            query = query.filter(Skill.profile_id == profile_id)
        if not include_hidden:
            query = query.filter(Skill.is_visible == True)
        return query.scalar() or 0

    def update_ordering(self, skill_id: int, new_order: int) -> None:
        """Update display ordering for a single skill."""
        self.db.query(Skill).filter(Skill.id == skill_id).update(
            {"display_order": new_order},
            synchronize_session="fetch"
        )
        self.db.commit()

    def bulk_reorder(self, items: List[Dict[str, int]], profile_id: Optional[int] = None) -> None:
        """
        Atomically update display orders for multiple skills.
        Caller handles transaction boundary.
        """
        for item in items:
            q = self.db.query(Skill).filter(Skill.id == item["id"])
            if profile_id is not None:
                q = q.filter(Skill.profile_id == profile_id)
            q.update({"display_order": item["ordering"]}, synchronize_session="fetch")
        self.db.flush()
