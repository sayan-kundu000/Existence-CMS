from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.hobby import Hobby
from app.repositories.base import BaseRepository


class HobbyRepository(BaseRepository[Hobby]):
    def __init__(self, db: Session):
        super().__init__(Hobby, db)

    def list_hobbies(self, include_hidden: bool = False) -> List[Hobby]:
        query = self.db.query(Hobby)
        if not include_hidden:
            query = query.filter(Hobby.visibility == True)
        return query.order_by(Hobby.ordering.asc(), Hobby.name.asc()).all()
