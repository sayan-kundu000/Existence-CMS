"""
Centralized Ownership Verification and IDOR (Insecure Direct Object Reference) Protection.
Guarantees that authenticated users can only view or modify resources they explicitly own,
or for which they have verified administrative authority.
"""
from typing import Any
from sqlalchemy.orm import Session
from app.core.exceptions import ResourceNotFoundError, PermissionDeniedError
from app.models.user import User
from app.models.profile import Profile
from app.models.project import Project, ProjectLink
from app.models.skill import Skill
from app.models.education import Education
from app.models.experience import Experience
from app.models.assessment import AssessmentSession, AssessmentResult


def verify_profile_ownership(user: User, profile: Profile) -> None:
    """
    Ensure the current user owns the specified profile.
    Admin users have access across the instance.
    """
    if user.role == "admin":
        return

    # Check explicit user_id foreign key if configured
    profile_user_id = getattr(profile, "user_id", None)
    if profile_user_id is not None and profile_user_id != user.id:
        raise PermissionDeniedError("You do not have permission to modify this profile.")


def verify_project_ownership(user: User, project: Project) -> None:
    """
    Ensure the project belongs to the user's profile.
    Prevents IDOR across differing portfolio accounts.
    """
    if user.role == "admin":
        return

    # If the project's profile has a user_id, ensure it matches
    if project.profile and getattr(project.profile, "user_id", None) is not None:
        if project.profile.user_id != user.id:
            # Raise 404 to avoid leaking existence of foreign projects
            raise ResourceNotFoundError("Project", project.id)


def verify_project_link_belongs_to_project(link: ProjectLink, project_id: int) -> None:
    """
    Ensure a project link explicitly belongs to the specified project.
    Prevents cross-project link modification or deletion.
    """
    if not link or link.project_id != project_id:
        raise ResourceNotFoundError(f"Project link with ID {getattr(link, 'id', None)} not found on project {project_id}.")


def verify_skill_ownership(user: User, skill: Skill) -> None:
    """Ensure skill belongs to user's profile."""
    if user.role == "admin":
        return
    if skill.profile and getattr(skill.profile, "user_id", None) is not None:
        if skill.profile.user_id != user.id:
            raise ResourceNotFoundError("Skill", skill.id)


def verify_education_ownership(user: User, education: Education) -> None:
    """Ensure education record belongs to user's profile."""
    if user.role == "admin":
        return
    if education.profile and getattr(education.profile, "user_id", None) is not None:
        if education.profile.user_id != user.id:
            raise ResourceNotFoundError("Education", education.id)


def verify_experience_ownership(user: User, experience: Experience) -> None:
    """Ensure work experience record belongs to user's profile."""
    if user.role == "admin":
        return
    if experience.profile and getattr(experience.profile, "user_id", None) is not None:
        if experience.profile.user_id != user.id:
            raise ResourceNotFoundError("Experience", experience.id)


def verify_assessment_session_access(user: User, session: AssessmentSession) -> None:
    """Ensure assessment session belongs to user or is authorized."""
    if user.role == "admin":
        return
    # If session is linked to a profile with user_id, verify match
    if session.profile and getattr(session.profile, "user_id", None) is not None:
        if session.profile.user_id != user.id:
            raise ResourceNotFoundError("Assessment session", session.id)
