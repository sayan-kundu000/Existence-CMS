from datetime import datetime
from typing import Optional, Literal
from pydantic import BaseModel, Field, ConfigDict, model_validator
from app.utils.date_helpers import validate_date_order, parse_month_year

EducationLevelType = Literal[
    "Doctorate",
    "Post Graduate",
    "Graduate",
    "Diploma",
    "Undergraduate",
    "High School",
    "Matriculation"
]

ScoreCategoryType = Literal["Percentage", "CGPA 10", "CGPA 5"]


class EducationBase(BaseModel):
    level: EducationLevelType
    stream: Optional[str] = Field(None, max_length=120)
    institution: Optional[str] = Field(None, max_length=150)
    starting_month_year: str = Field(..., min_length=1, max_length=30)
    ending_month_year: Optional[str] = Field(None, max_length=30)
    currently_studying: bool = Field(default=False)
    score_type: Optional[ScoreCategoryType] = None
    score_value: Optional[float] = None
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

        # Stream/Field Locking Rule: High School or Matriculation cannot have stream/field
        if self.level in ("High School", "Matriculation"):
            self.stream = None
        else:
            if not self.stream or not self.stream.strip():
                raise ValueError(f"Stream / Field of study is required for {self.level}.")
            self.stream = self.stream.strip()

        # Sync start date
        if self.starting_month_year:
            dt = parse_month_year(self.starting_month_year)
            if dt:
                self.start_month = dt.month
                self.start_year = dt.year

        if self.currently_studying:
            # Rule: Currently Studying = TRUE -> ending date and score must be null
            self.ending_month_year = None
            self.end_month = None
            self.end_year = None
            self.score_type = None
            self.score_value = None
        else:
            # Rule: Currently Studying = FALSE -> ending date required
            if not self.ending_month_year or not self.ending_month_year.strip():
                raise ValueError("Ending Month & Year is required when not currently studying.")
            dt = parse_month_year(self.ending_month_year)
            if dt:
                self.end_month = dt.month
                self.end_year = dt.year

            # CGPA / Percentage Validation
            if self.score_type is not None or self.score_value is not None:
                if self.score_type is None and self.score_value is not None:
                    raise ValueError("Score category (Percentage, CGPA 10, or CGPA 5) is required when marks are provided.")
                if self.score_type is not None and self.score_value is None:
                    raise ValueError("Marks number is required when score category is selected.")

                # Decimal places check (up to 2 places)
                val_str = f"{self.score_value:.6f}".rstrip("0").rstrip(".")
                if "." in val_str:
                    dec_len = len(val_str.split(".")[1])
                    if dec_len > 2:
                        raise ValueError("Marks number can have at most 2 decimal places.")

                if self.score_type == "Percentage":
                    if not (0.0 <= self.score_value <= 100.0):
                        raise ValueError("Percentage must be between 0 and 100.")
                elif self.score_type == "CGPA 10":
                    if not (0.0 <= self.score_value <= 10.0):
                        raise ValueError("CGPA 10 marks must be between 0 and 10.")
                elif self.score_type == "CGPA 5":
                    if not (0.0 <= self.score_value <= 5.0):
                        raise ValueError("CGPA 5 marks must be between 0 and 5.")

                self.score_value = round(self.score_value, 2)

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
    stream: Optional[str] = Field(None, max_length=120)
    institution: Optional[str] = Field(None, max_length=150)
    starting_month_year: Optional[str] = Field(None, max_length=30)
    ending_month_year: Optional[str] = Field(None, max_length=30)
    currently_studying: Optional[bool] = None
    score_type: Optional[ScoreCategoryType] = None
    score_value: Optional[float] = None
    ordering: Optional[int] = None
    start_month: Optional[int] = Field(None, ge=1, le=12)
    start_year: Optional[int] = Field(None, gt=0)
    end_month: Optional[int] = Field(None, ge=1, le=12)
    end_year: Optional[int] = Field(None, gt=0)
    display_order: Optional[int] = Field(None, ge=0)
    profile_id: Optional[int] = None

    @model_validator(mode="after")
    def validate_patch(self):
        if self.level in ("High School", "Matriculation"):
            self.stream = None
        if self.currently_studying:
            self.score_type = None
            self.score_value = None
        elif self.score_type is not None and self.score_value is not None:
            val_str = f"{self.score_value:.6f}".rstrip("0").rstrip(".")
            if "." in val_str and len(val_str.split(".")[1]) > 2:
                raise ValueError("Marks number can have at most 2 decimal places.")
            if self.score_type == "Percentage" and not (0.0 <= self.score_value <= 100.0):
                raise ValueError("Percentage must be between 0 and 100.")
            elif self.score_type == "CGPA 10" and not (0.0 <= self.score_value <= 10.0):
                raise ValueError("CGPA 10 marks must be between 0 and 10.")
            elif self.score_type == "CGPA 5" and not (0.0 <= self.score_value <= 5.0):
                raise ValueError("CGPA 5 marks must be between 0 and 5.")
            self.score_value = round(self.score_value, 2)
        return self


class EducationOut(EducationBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime
