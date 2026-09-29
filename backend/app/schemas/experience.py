from datetime import datetime
from typing import Optional, Literal
from pydantic import BaseModel, Field, ConfigDict, model_validator
from app.utils.date_helpers import validate_date_order, parse_month_year

WorkModeType = Literal["On-site", "Remote", "Hybrid"]


class ExperienceBase(BaseModel):
    role: str = Field(..., min_length=1, max_length=120)
    employer: str = Field(..., min_length=1, max_length=150)
    work_mode: WorkModeType
    location: Optional[str] = Field(None, max_length=150)
    starting_month_year: str = Field(..., min_length=1, max_length=30)
    ending_month_year: Optional[str] = Field(None, max_length=30)
    currently_working: bool = Field(default=False)
    ordering: int = Field(default=0)
    start_month: Optional[int] = Field(None, ge=1, le=12)
    start_year: Optional[int] = Field(None, gt=0)
    end_month: Optional[int] = Field(None, ge=1, le=12)
    end_year: Optional[int] = Field(None, gt=0)
    display_order: Optional[int] = Field(None, ge=0)
    profile_id: Optional[int] = None

    @model_validator(mode="after")
    def validate_conditional_rules(self):
        # Sync display_order and ordering
        if self.display_order is not None and self.ordering == 0:
            self.ordering = self.display_order
        elif self.ordering != 0 and self.display_order is None:
            self.display_order = self.ordering

        # 1. Conditional Location Rule:
        if self.work_mode in ["On-site", "Hybrid"]:
            if not self.location or not self.location.strip():
                raise ValueError(f"Location is required when work mode is {self.work_mode}.")
        elif self.work_mode == "Remote":
            # Prevent stale location data
            if not self.location or not self.location.strip() or self.location.strip() != "Remote":
                self.location = "Remote"

        # Sync start date
        if self.starting_month_year:
            dt = parse_month_year(self.starting_month_year)
            if dt:
                self.start_month = dt.month
                self.start_year = dt.year

        # 2. Conditional Ending Date Rule:
        if self.currently_working:
            self.ending_month_year = None
            self.end_month = None
            self.end_year = None
        else:
            if not self.ending_month_year or not self.ending_month_year.strip():
                raise ValueError("Ending Month & Year is required when not currently working.")
            dt = parse_month_year(self.ending_month_year)
            if dt:
                self.end_month = dt.month
                self.end_year = dt.year

        # 3. Date Order Rule:
        if self.ending_month_year:
            validate_date_order(self.starting_month_year, self.ending_month_year)

        return self


class ExperienceCreate(ExperienceBase):
    pass


class ExperienceUpdate(ExperienceBase):
    pass


class ExperiencePatch(BaseModel):
    role: Optional[str] = Field(None, min_length=1, max_length=120)
    employer: Optional[str] = Field(None, min_length=1, max_length=150)
    work_mode: Optional[WorkModeType] = None
    location: Optional[str] = Field(None, max_length=150)
    starting_month_year: Optional[str] = Field(None, max_length=30)
    ending_month_year: Optional[str] = Field(None, max_length=30)
    currently_working: Optional[bool] = None
    ordering: Optional[int] = None
    start_month: Optional[int] = Field(None, ge=1, le=12)
    start_year: Optional[int] = Field(None, gt=0)
    end_month: Optional[int] = Field(None, ge=1, le=12)
    end_year: Optional[int] = Field(None, gt=0)
    display_order: Optional[int] = Field(None, ge=0)
    profile_id: Optional[int] = None


class ExperienceOut(ExperienceBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime
