"""
Centralized Role-Based Access Control (RBAC) and Capability System.
Provides canonical roles, explicit permission capabilities, and deterministic capability evaluation
across all Existence domain modules.
"""
from typing import List, Set, Dict


class Roles:
    ADMIN = "admin"
    EDITOR = "editor"
    VIEWER = "viewer"
    PUBLIC = "public"

    ALL_ROLES = (ADMIN, EDITOR, VIEWER, PUBLIC)


class Permissions:
    # Profile Domain
    PROFILE_READ = "profile:read"
    PROFILE_WRITE = "profile:write"

    # Skills Domain
    SKILLS_READ = "skills:read"
    SKILLS_WRITE = "skills:write"

    # Projects Domain
    PROJECTS_READ = "projects:read"
    PROJECTS_WRITE = "projects:write"
    PROJECTS_DELETE = "projects:delete"

    # Personality & Psychometrics Domain
    PERSONALITY_READ = "personality:read"
    PERSONALITY_WRITE = "personality:write"

    # CMS & Administrative Management
    CMS_MANAGE = "cms:manage"
    ASSESSMENT_MANAGE = "assessment:manage"
    AUDIT_READ = "audit:read"
    SECURITY_MANAGE = "security:manage"

    ALL_PERMISSIONS = (
        PROFILE_READ,
        PROFILE_WRITE,
        SKILLS_READ,
        SKILLS_WRITE,
        PROJECTS_READ,
        PROJECTS_WRITE,
        PROJECTS_DELETE,
        PERSONALITY_READ,
        PERSONALITY_WRITE,
        CMS_MANAGE,
        ASSESSMENT_MANAGE,
        AUDIT_READ,
        SECURITY_MANAGE,
    )


# Role-to-Permissions Capability Mapping
ROLE_PERMISSIONS: Dict[str, Set[str]] = {
    Roles.ADMIN: {"*"},  # Superuser capability wildcard
    Roles.EDITOR: {
        Permissions.PROFILE_READ,
        Permissions.PROFILE_WRITE,
        Permissions.SKILLS_READ,
        Permissions.SKILLS_WRITE,
        Permissions.PROJECTS_READ,
        Permissions.PROJECTS_WRITE,
        Permissions.PROJECTS_DELETE,
        Permissions.PERSONALITY_READ,
        Permissions.PERSONALITY_WRITE,
        Permissions.CMS_MANAGE,
        Permissions.ASSESSMENT_MANAGE,
        Permissions.AUDIT_READ,
    },
    Roles.VIEWER: {
        Permissions.PROFILE_READ,
        Permissions.SKILLS_READ,
        Permissions.PROJECTS_READ,
        Permissions.PERSONALITY_READ,
        Permissions.AUDIT_READ,
    },
    Roles.PUBLIC: {
        Permissions.PROFILE_READ,
        Permissions.SKILLS_READ,
        Permissions.PROJECTS_READ,
        Permissions.PERSONALITY_READ,
    }
}


def has_permission(role: str, permission: str) -> bool:
    """
    Check if a given role possesses a requested capability.
    Wildcard '*' grants all capabilities.
    """
    if not role:
        return False
    normalized_role = role.lower().strip()
    allowed_perms = ROLE_PERMISSIONS.get(normalized_role, set())
    if "*" in allowed_perms:
        return True
    return permission in allowed_perms


def get_role_permissions(role: str) -> List[str]:
    """Retrieve the sorted list of explicit permissions granted to a role."""
    if not role:
        return []
    normalized_role = role.lower().strip()
    allowed = ROLE_PERMISSIONS.get(normalized_role, set())
    if "*" in allowed:
        return sorted(list(Permissions.ALL_PERMISSIONS))
    return sorted(list(allowed))
