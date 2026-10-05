from app.repositories.base import BaseRepository
from app.repositories.profile_repository import ProfileRepository
from app.repositories.education_repository import EducationRepository
from app.repositories.experience_repository import ExperienceRepository
from app.repositories.skill_repository import SkillRepository
from app.repositories.hobby_repository import HobbyRepository
from app.repositories.interest_repository import InterestRepository
from app.repositories.assessment_repository import AssessmentRepository
from app.repositories.project_repository import ProjectRepository

__all__ = [
    "BaseRepository",
    "ProfileRepository",
    "EducationRepository",
    "ExperienceRepository",
    "SkillRepository",
    "HobbyRepository",
    "InterestRepository",
    "AssessmentRepository",
    "ProjectRepository"
]

