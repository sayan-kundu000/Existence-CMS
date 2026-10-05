from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.interest import Interest
from app.repositories.base import BaseRepository


class InterestRepository(BaseRepository[Interest]):
    def __init__(self, db: Session):
        super().__init__(Interest, db)

    def list_interests(self, include_hidden: bool = False) -> List[Interest]:
        query = self.db.query(Interest)
        if not include_hidden:
            query = query.filter(Interest.visibility == True)
        return query.order_by(Interest.ordering.asc(), Interest.name.asc()).all()

    def find_by_normalized_name(self, name: str, exclude_id: Optional[int] = None) -> Optional[Interest]:
        clean = name.strip().lower()
        query = self.db.query(Interest).filter(func.lower(func.trim(Interest.name)) == clean)
        if exclude_id:
            query = query.filter(Interest.id != exclude_id)
        return query.first()
