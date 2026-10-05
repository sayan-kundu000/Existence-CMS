from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    Text,
    DateTime,
    ForeignKey,
    CheckConstraint,
    Index,
    func
)
from sqlalchemy.orm import relationship, synonym
from app.core.database import Base

SKILL_LEVEL_MAP: Dict[int, str] = {
    1: "Beginner",
    2: "Novice",
    3: "Intermediate",
    4: "Proficient",
    5: "Advanced",
    6: "Expert",
    7: "Master"
}

SKILL_LEVEL_METADATA: List[Dict[str, Any]] = [
    {
        "rating": 1,
        "level": "Beginner",
        "description": "Foundational understanding and basic operational capability.",
        "display_order": 1,
    },
    {
        "rating": 2,
        "level": "Novice",
        "description": "Practical application with structured guidance and established patterns.",
        "display_order": 2,
    },
    {
        "rating": 3,
        "level": "Intermediate",
        "description": "Competent independent execution of standard production workflows.",
        "display_order": 3,
    },
    {
        "rating": 4,
        "level": "Proficient",
        "description": "Strong practical competence, fluent problem-solving, and quality optimization.",
        "display_order": 4,
    },
    {
        "rating": 5,
        "level": "Advanced",
        "description": "Deep subject-matter mastery, architecting complex, resilient implementations.",
        "display_order": 5,
    },
    {
        "rating": 6,
        "level": "Expert",
        "description": "Authoritative domain authority, cross-paradigm insight, and technical leadership.",
        "display_order": 6,
    },
    {
        "rating": 7,
        "level": "Master",
        "description": "World-class synthesis, defining state-of-the-art standards and groundbreaking patterns.",
        "display_order": 7,
    },
]


SKILL_CATEGORIES: List[str] = [
    "Technical",
    "Financial",
    "Analytical",
    "Business",
    "Leadership",
    "Management",
    "Diplomatic",
    "Creative",
    "Research",
    "Medical",
    "Legal",
    "Psychological",
    "Scientific",
    "Educational",
    "Environmental",
    "Operational",
    "Ethical",
]

SKILL_CATEGORY_MAP: Dict[str, str] = {cat.lower(): cat for cat in SKILL_CATEGORIES}


def normalize_skill_categories(categories_input: Any) -> tuple[str, List[str]]:
    """
    Normalizes single or multiple skill categories against the canonical categories.
    Preserves case-normalization, trims whitespace, deduplicates while preserving order.
    Returns (comma_separated_str, list_of_categories).
    """
    if not categories_input:
        return ("Technical", ["Technical"])

    raw_list: List[str] = []
    if isinstance(categories_input, str):
        raw_list = [c.strip() for c in categories_input.split(",") if c.strip()]
    elif isinstance(categories_input, (list, tuple, set)):
        for item in categories_input:
            if isinstance(item, str):
                for part in item.split(","):
                    if part.strip():
                        raw_list.append(part.strip())
    else:
        raw_list = [str(categories_input).strip()]

    if not raw_list:
        return ("Technical", ["Technical"])

    canonical_list: List[str] = []
    seen: set[str] = set()

    for item in raw_list:
        clean = item.strip()
        if not clean:
            continue
        key = clean.lower()
        if key in seen:
            continue
        seen.add(key)
        if key in SKILL_CATEGORY_MAP:
            canonical_list.append(SKILL_CATEGORY_MAP[key])
        else:
            canonical_list.append(clean[:50])

    if not canonical_list:
        canonical_list = ["Technical"]

    return (", ".join(canonical_list), canonical_list)


def normalize_skill_domains(domains_input: Any) -> tuple[Optional[str], List[str]]:
    """
    Normalizes single or multiple skill domains.
    Accepts string, list, tuple, or set. Trims whitespace and deduplicates while preserving order.
    Returns (comma_separated_str, list_of_domains).
    """
    if not domains_input:
        return (None, [])

    raw_list: List[str] = []
    if isinstance(domains_input, str):
        raw_list = [d.strip() for d in domains_input.split(",") if d.strip()]
    elif isinstance(domains_input, (list, tuple, set)):
        for item in domains_input:
            if isinstance(item, str):
                for part in item.split(","):
                    if part.strip():
                        raw_list.append(part.strip())
            elif item is not None:
                raw_list.append(str(item).strip())
    else:
        raw_list = [str(domains_input).strip()]

    cleaned_list: List[str] = []
    seen: set[str] = set()

    for item in raw_list:
        clean = item.strip()
        if not clean:
            continue
        key = clean.lower()
        if key in seen:
            continue
        seen.add(key)
        cleaned_list.append(clean[:100])

    if not cleaned_list:
        return (None, [])

    return (", ".join(cleaned_list), cleaned_list)


class Skill(Base):
    __tablename__ = "skills"

    id = Column(Integer, primary_key=True, index=True)
    profile_id = Column(Integer, ForeignKey("profiles.id", ondelete="CASCADE"), nullable=True, index=True)
    name = Column(String(100), nullable=False)
    category = Column(String(255), nullable=False, default="Technical")
    description = Column(String(255), nullable=True)
    domain = Column(String(500), nullable=True)  # Comma-separated domains e.g. "AIML, Biotechnology"
    rating = Column(Integer, nullable=False)  # 1 to 7
    is_visible = Column(Boolean, default=True, nullable=False)
    display_order = Column(Integer, default=0, nullable=False)
    metadata_info = Column(Text, default="{}", nullable=False)  # Additional notes or tags
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    # Aliases via SQLAlchemy synonym
    visibility = synonym("is_visible")
    ordering = synonym("display_order")

    __table_args__ = (
        CheckConstraint("rating >= 1 AND rating <= 7", name="check_skill_rating"),
        CheckConstraint("display_order >= 0", name="check_skill_display_order"),
        CheckConstraint("length(trim(name)) > 0", name="check_skill_name_not_empty"),
        Index("ix_skills_profile_lower_name", "profile_id", func.lower(name), unique=True),
        Index("ix_skills_domain", "domain"),
        Index("ix_skills_category", "category"),
        Index("ix_skills_rating", "rating"),
        Index("ix_skills_visibility", "is_visible"),
    )

    profile = relationship("Profile", back_populates="skills")

    @property
    def level_label(self) -> str:
        return SKILL_LEVEL_MAP.get(self.rating, "Unknown")

    @property
    def level(self) -> str:
        return SKILL_LEVEL_MAP.get(self.rating, "Beginner")

    @property
    def categories(self) -> List[str]:
        return normalize_skill_categories(self.category)[1]

    @property
    def domains(self) -> List[str]:
        return normalize_skill_domains(self.domain)[1]

