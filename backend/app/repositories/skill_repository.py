from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.skill import Skill
from app.repositories.base import BaseRepository


class SkillRepository(BaseRepository[Skill]):
    def __init__(self, db: Session):
        super().__init__(Skill, db)

    def list_skills(self, include_hidden: bool = False, category: Optional[str] = None) -> List[Skill]:
        query = self.db.query(Skill)
        if not include_hidden:
            query = query.filter(Skill.visibility == True)
        if category:
            query = query.filter(Skill.category == category)
        return query.order_by(Skill.ordering.asc(), Skill.name.asc()).all()

    def update_ordering(self, skill_id: int, new_order: int) -> None:
        self.db.query(Skill).filter(Skill.id == skill_id).update({"ordering": new_order})
        self.db.commit()
