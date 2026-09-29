from typing import List, Optional
from sqlalchemy.orm import Session
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
