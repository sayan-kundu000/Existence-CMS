from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship, validates, synonym
from app.core.database import Base
from app.utils.date_helpers import parse_month_year

VALID_WORK_MODES = ("On-site", "Remote", "Hybrid")


class Experience(Base):
    __tablename__ = "work_experiences"

    id = Column(Integer, primary_key=True, index=True)
    profile_id = Column(Integer, ForeignKey("profiles.id", ondelete="CASCADE"), nullable=True, index=True)
    role = Column(String(120), nullable=False)
    employer = Column(String(150), nullable=False)
    work_mode = Column(String(20), nullable=False)  # On-site, Remote, Hybrid
    location = Column(String(150), nullable=True)  # Required if On-site or Hybrid

    # Normalized numeric period fields
    start_month = Column(Integer, nullable=True)
    start_year = Column(Integer, nullable=True)
    end_month = Column(Integer, nullable=True)
    end_year = Column(Integer, nullable=True)

    # String representations preserved for API/frontend backwards compatibility
    starting_month_year = Column(String(30), nullable=True)
    ending_month_year = Column(String(30), nullable=True)

    currently_working = Column(Boolean, default=False, nullable=False)
    display_order = Column(Integer, default=0, nullable=False)

    # Alias ordering to display_order via synonym
    ordering = synonym("display_order")

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    __table_args__ = (
        CheckConstraint(
            f"work_mode IN {VALID_WORK_MODES}",
            name="check_work_mode"
        ),
        CheckConstraint(
            "(work_mode IN ('On-site', 'Hybrid') AND location IS NOT NULL AND length(trim(location)) > 0) OR (work_mode = 'Remote')",
            name="check_experience_location"
        ),
        CheckConstraint(
            "start_month IS NULL OR (start_month >= 1 AND start_month <= 12)",
            name="check_experience_start_month"
        ),
        CheckConstraint(
            "end_month IS NULL OR (end_month >= 1 AND end_month <= 12)",
            name="check_experience_end_month"
        ),
        CheckConstraint(
            "start_year IS NULL OR start_year > 0",
            name="check_experience_start_year"
        ),
        CheckConstraint(
            "end_year IS NULL OR end_year > 0",
            name="check_experience_end_year"
        ),
        CheckConstraint(
            "currently_working = 0 OR currently_working = FALSE OR (end_month IS NULL AND end_year IS NULL)",
            name="check_experience_working_no_end"
        ),
        CheckConstraint(
            "currently_working = 1 OR currently_working = TRUE OR start_year IS NULL OR end_year IS NULL OR ("
            "end_year > start_year OR (end_year = start_year AND (end_month IS NULL OR start_month IS NULL OR end_month >= start_month))"
            ")",
            name="check_experience_dates"
        ),
        CheckConstraint(
            "display_order >= 0",
            name="check_experience_display_order"
        ),
    )

    profile = relationship("Profile", back_populates="work_experiences")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.starting_month_year and (self.start_month is None or self.start_year is None):
            dt = parse_month_year(self.starting_month_year)
            if dt:
                self.start_month = dt.month
                self.start_year = dt.year
        if self.ending_month_year and (self.end_month is None or self.end_year is None):
            dt = parse_month_year(self.ending_month_year)
            if dt:
                self.end_month = dt.month
                self.end_year = dt.year
        if self.work_mode == "Remote" and (not self.location or self.location.strip() == ""):
            self.location = "Remote"

    @validates("starting_month_year")
    def _validate_starting_month_year(self, key, value):
        if value:
            dt = parse_month_year(value)
            if dt:
                self.start_month = dt.month
                self.start_year = dt.year
        else:
            self.start_month = None
            self.start_year = None
        return value

    @validates("ending_month_year")
    def _validate_ending_month_year(self, key, value):
        if value:
            dt = parse_month_year(value)
            if dt:
                self.end_month = dt.month
                self.end_year = dt.year
        else:
            self.end_month = None
            self.end_year = None
        return value

    @validates("work_mode")
    def _validate_work_mode(self, key, value):
        if value == "Remote" and (not self.location or self.location.strip() == ""):
            self.location = "Remote"
        return value


# Alias WorkExperience to Experience for full Prompt 03 and domain nomenclature compatibility
WorkExperience = Experience
