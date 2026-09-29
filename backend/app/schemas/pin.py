from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class PinSetupRequest(BaseModel):
    pin: str = Field(..., min_length=4, max_length=8, description="4 to 8 digit/character security PIN")


class PinVerifyRequest(BaseModel):
    pin: str = Field(..., min_length=4, max_length=8, description="Security PIN to verify")


class PinChangeRequest(BaseModel):
    current_pin: str = Field(..., min_length=4, max_length=8)
    new_pin: str = Field(..., min_length=4, max_length=8)


class PinStatusResponse(BaseModel):
    is_configured: bool
    is_locked: bool
    attempts_remaining: int
    locked_until: Optional[datetime] = None
    last_verified_at: Optional[datetime] = None


class PinVerifyResponse(BaseModel):
    success: bool
    message: str
    pin_token: Optional[str] = None  # Temporary authorization token for sensitive actions
