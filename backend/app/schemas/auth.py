from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field, ConfigDict


class UserLogin(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=1)


class UserRegister(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user_id: int
    username: str
    role: str
    pin_configured: bool
    permissions: Optional[List[str]] = None


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    email: str
    role: str
    is_active: bool
    pin_configured: bool = False
    permissions: Optional[List[str]] = None
    created_at: datetime


class AuthSessionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    token_identifier: str
    expires_at: datetime
    created_at: datetime
    last_used_at: Optional[datetime] = None
    is_current: bool = False


class LogoutResponse(BaseModel):
    success: bool
    message: str
