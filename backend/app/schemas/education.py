from datetime import datetime
from typing import Optional, Literal
from pydantic import BaseModel, Field, ConfigDict, model_validator
from app.utils.date_helpers import validate_date_order, parse_month_year

EducationLevelType = Literal[
    "Doctorate",
    "Post Graduate",
    "Graduate",
    "Undergraduate",
    "High School",
    "Matriculation"
]


class EducationBase(BaseModel):
    level: EducationLevelType
    stream: str = Field(..., min_length=1, max_length=120)
    institution: Optional[str] = Field(None, max_length=150)
    starting_month_year: str = Field(..., min_length=1, max_length=30)
    ending_month_year: Optional[str] = Field(None, max_length=30)
    currently_studying: bool = Field(default=False)
    ordering: int = Field(default=0)
    start_month: Optional[int] = Field(None, ge=1, le=12)
    start_year: Optional[int] = Field(None, gt=0)
    end_month: Optional[int] = Field(None, ge=1, le=12)
    end_year: Optional[int] = Field(None, gt=0)
    display_order: Optional[int] = Field(None, ge=0)
    profile_id: Optional[int] = None

    @model_validator(mode="after")
    def validate_conditional_dates(self):
        # Sync display_order and ordering
        if self.display_order is not None and self.ordering == 0:
            self.ordering = self.display_order
        elif self.ordering != 0 and self.display_order is None:
            self.display_order = self.ordering

        # Sync start date
        if self.starting_month_year:
            dt = parse_month_year(self.starting_month_year)
            if dt:
                self.start_month = dt.month
                self.start_year = dt.year

        if self.currently_studying:
            # Rule: Currently Studying = TRUE -> ending date must be null
            self.ending_month_year = None
            self.end_month = None
            self.end_year = None
        else:
            # Rule: Currently Studying = FALSE -> ending date required
            if not self.ending_month_year or not self.ending_month_year.strip():
                raise ValueError("Ending Month & Year is required when not currently studying.")
            dt = parse_month_year(self.ending_month_year)
            if dt:
                self.end_month = dt.month
                self.end_year = dt.year

        # Rule: Ending date cannot precede starting date
        if self.ending_month_year:
            validate_date_order(self.starting_month_year, self.ending_month_year)

        return self


class EducationCreate(EducationBase):
    pass


class EducationUpdate(EducationBase):
    pass


class EducationPatch(BaseModel):
    level: Optional[EducationLevelType] = None
    stream: Optional[str] = Field(None, min_length=1, max_length=120)
    institution: Optional[str] = Field(None, max_length=150)
    starting_month_year: Optional[str] = Field(None, max_length=30)
    ending_month_year: Optional[str] = Field(None, max_length=30)
    currently_studying: Optional[bool] = None
    ordering: Optional[int] = None
    start_month: Optional[int] = Field(None, ge=1, le=12)
    start_year: Optional[int] = Field(None, gt=0)
    end_month: Optional[int] = Field(None, ge=1, le=12)
    end_year: Optional[int] = Field(None, gt=0)
    display_order: Optional[int] = Field(None, ge=0)
    profile_id: Optional[int] = None


class EducationOut(EducationBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime
