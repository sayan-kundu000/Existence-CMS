from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict, model_validator


class InterestBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    category: Optional[str] = Field(None, max_length=80)
    icon: Optional[str] = Field(None, max_length=50)
    visibility: bool = Field(default=True)
    is_visible: Optional[bool] = None
    ordering: int = Field(default=0)
    display_order: Optional[int] = None
    profile_id: Optional[int] = None

    @model_validator(mode="after")
    def sync_aliases(self):
        if self.is_visible is not None:
            self.visibility = self.is_visible
        else:
            self.is_visible = self.visibility

        if self.display_order is not None and self.ordering == 0:
            self.ordering = self.display_order
        elif self.ordering != 0 and self.display_order is None:
            self.display_order = self.ordering
        return self


class InterestCreate(InterestBase):
    pass


class InterestUpdate(InterestBase):
    pass


class InterestPatch(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    category: Optional[str] = Field(None, max_length=80)
    icon: Optional[str] = Field(None, max_length=50)
    visibility: Optional[bool] = None
    is_visible: Optional[bool] = None
    ordering: Optional[int] = None
    display_order: Optional[int] = None
    profile_id: Optional[int] = None


class InterestOut(InterestBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime
