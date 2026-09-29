from app.repositories.base import BaseRepository
from app.repositories.education_repository import EducationRepository
from app.repositories.experience_repository import ExperienceRepository
from app.repositories.skill_repository import SkillRepository
from app.repositories.hobby_repository import HobbyRepository
from app.repositories.interest_repository import InterestRepository
from app.repositories.assessment_repository import AssessmentRepository

__all__ = [
    "BaseRepository",
    "EducationRepository",
    "ExperienceRepository",
    "SkillRepository",
    "HobbyRepository",
    "InterestRepository",
    "AssessmentRepository"
]
