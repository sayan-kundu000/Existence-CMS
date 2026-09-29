from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field, ConfigDict


class ProfileEmailBase(BaseModel):
    email: EmailStr
    label: str = Field(default="Primary", max_length=50)
    is_primary: bool = Field(default=False)
    display_order: int = Field(default=0, ge=0)


class ProfileEmailCreate(ProfileEmailBase):
    pass


class ProfileEmailUpdate(BaseModel):
    email: Optional[EmailStr] = None
    label: Optional[str] = Field(None, max_length=50)
    is_primary: Optional[bool] = None
    display_order: Optional[int] = Field(None, ge=0)


class ProfileEmailOut(ProfileEmailBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    profile_id: int
    created_at: datetime
    updated_at: datetime


class ProfileBase(BaseModel):
    name: Optional[str] = Field(None, max_length=120)
    email_ids: List[str] = Field(default_factory=list)
    mobile_number: Optional[str] = Field(None, max_length=30)
    linkedin: Optional[str] = Field(None, max_length=255)
    about: Optional[str] = None


class ProfileUpdate(ProfileBase):
    pass


class ProfileOut(ProfileBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    is_empty: bool = True
    emails: Optional[List[ProfileEmailOut]] = None
    created_at: datetime
    updated_at: datetime
