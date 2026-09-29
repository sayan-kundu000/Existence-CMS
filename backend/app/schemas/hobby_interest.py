from datetime import datetime
from typing import Optional, Literal
from pydantic import BaseModel, Field, ConfigDict

HobbyInterestType = Literal["hobby", "interest"]


class HobbyInterestBase(BaseModel):
    type: HobbyInterestType
    name: str = Field(..., min_length=1, max_length=100)
    category: Optional[str] = Field(None, max_length=80)
    icon: Optional[str] = Field(None, max_length=50)
    ordering: int = Field(default=0)


class HobbyInterestCreate(HobbyInterestBase):
    pass


class HobbyInterestUpdate(HobbyInterestBase):
    pass


class HobbyInterestOut(HobbyInterestBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime
