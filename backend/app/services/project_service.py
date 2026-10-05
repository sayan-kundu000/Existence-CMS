import json
import hmac
import hashlib
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any, Union
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.models.project import (
    Project,
    ProjectLink,
    Technology,
    ProjectTechnology,
    ProjectSkill,
    GitHubAccountLink,
    PROJECT_STATUSES,
    LINK_TYPES,
    TECH_CATEGORIES
)
from app.models.skill import Skill, SKILL_LEVEL_MAP
from app.models.user import User
from app.repositories.project_repository import ProjectRepository
from app.repositories.profile_repository import ProfileRepository
from app.schemas.project import (
    ProjectCreate,
    ProjectUpdate,
    ProjectPatch,
    ProjectLinkCreate,
    ProjectLinkUpdate,
    ProjectLinkPatch,
    ProjectTechnologyInput,
    ProjectReorderItem,
    ProjectLinkReorderItem,
    GitHubAccountLinkCreate,
    GitHubAccountLinkUpdate,
    GitHubAccountLinkOut,
    GitHubSyncResultOut,
    ProjectAiDossierGenerateRequest,
    ProjectAiDossierGenerateResponse
)
from app.core.exceptions import (
    ResourceNotFoundError,
    ValidationFailedError,
    ConflictError,
    BusinessRuleError
)
from app.services.audit_service import log_audit_event, record_content_revision
from app.services.github_extractor import (
    extract_github_projects,
    parse_github_target,
    generate_simple_ai_dossier,
    categorize_technology
)


def project_to_dict(p: Project, public: bool = False) -> Dict[str, Any]:
    """Convert Project ORM instance to a dictionary matching ProjectOut schema."""
    # Filter links for public view
    raw_links = sorted(p.links or [], key=lambda l: (l.display_order, l.id))
    if public:
        links_data = [l for l in raw_links if getattr(l, "is_visible", True)]
    else:
        links_data = raw_links

    serialized_links = [
        {
            "id": l.id,
            "project_id": l.project_id,
            "label": l.label,
            "url": l.url,
            "link_type": l.link_type,
            "is_primary": l.is_primary,
            "is_visible": l.is_visible,
            "display_order": l.display_order,
            "created_at": l.created_at,
            "updated_at": l.updated_at,
        }
        for l in links_data
    ]

    # Primary link resolution
    primary_link = None
    for l in serialized_links:
        if l["is_primary"]:
            primary_link = l
            break

    # Technologies
    raw_proj_techs = sorted(p.project_technologies or [], key=lambda pt: (pt.display_order, pt.id))
    serialized_techs = [
        {
            "id": pt.id,
            "technology_id": pt.technology_id,
            "name": pt.technology.name if pt.technology else "Unknown",
            "category": pt.technology.category if pt.technology else "Other",
            "display_order": pt.display_order,
        }
        for pt in raw_proj_techs
    ]

    # Associated Skills sorted by Mastery Rating descending
    serialized_skills = sorted(
        [
            {
                "id": ps.skill.id,
                "name": ps.skill.name,
                "category": ps.skill.category,
                "rating": ps.skill.rating,
                "level_label": SKILL_LEVEL_MAP.get(ps.skill.rating, "Unknown"),
            }
            for ps in (p.project_skills or [])
            if ps.skill is not None
        ],
        key=lambda s: (-s["rating"], (s["name"] or "").lower())
    )

    return {
        "id": p.id,
        "profile_id": p.profile_id,
        "name": p.name,
        "short_description": p.short_description,
        "description": p.description,
        "status": p.status,
        "start_month": p.start_month,
        "start_year": p.start_year,
        "end_month": p.end_month,
        "end_year": p.end_year,
        "is_current": p.is_current,
        "is_featured": p.is_featured,
        "is_visible": p.is_visible,
        "visibility": p.is_visible,
        "display_order": p.display_order,
        "ordering": p.display_order,
        "technologies": serialized_techs,
        "links": serialized_links,
        "skills": serialized_skills,
        "primary_link": primary_link,
        "created_at": p.created_at,
        "updated_at": p.updated_at,
    }


class ProjectService:
    """
    Authoritative domain service for Existence Projects Engine.
    Coordinates project CRUD, multiple deployment links, primary link integrity,
    reusable technology stack deduplication, deterministic ordering, PIN security,
    revision snapshots, and audit logging.
    """

    def __init__(self, db: Session):
        self.db = db
        self.repo = ProjectRepository(db)
        self.profile_repo = ProfileRepository(db)

    def _get_active_profile_id(self) -> int:
        profile = self.profile_repo.get_or_create_profile()
        return profile.id

    def list_projects(
        self,
        profile_id: Optional[int] = None,
        include_hidden: bool = False,
        search: Optional[str] = None,
        status: Optional[str] = None,
        technology: Optional[str] = None,
        is_featured: Optional[bool] = None,
        sort_by: str = "order"
    ) -> List[Dict[str, Any]]:
        """List projects with eager loading and public/private visibility filtration."""
        if profile_id is None:
            profile_id = self._get_active_profile_id()

        projects = self.repo.list_projects(
            profile_id=profile_id,
            include_hidden=include_hidden,
            search=search,
            status=status,
            technology=technology,
            is_featured=is_featured,
            sort_by=sort_by
        )
        return [project_to_dict(p, public=not include_hidden) for p in projects]

    def get_project(self, project_id: int, include_hidden: bool = False) -> Dict[str, Any]:
        """Retrieve single project by ID."""
        p = self.repo.get_by_id(project_id)
        if not p:
            raise ResourceNotFoundError(f"Project with ID {project_id} not found.")
        if not include_hidden and not p.is_visible:
            raise ResourceNotFoundError(f"Project with ID {project_id} not found.")
        return project_to_dict(p, public=not include_hidden)

    def get_categories(self) -> Dict[str, List[str]]:
        """Return canonical status values, link types, and technology categories."""
        return {
            "statuses": list(PROJECT_STATUSES),
            "link_types": list(LINK_TYPES),
            "tech_categories": list(TECH_CATEGORIES)
        }

    # -------------------------------------------------------------------------
    # Project Mutations
    # -------------------------------------------------------------------------

    def create_project(
        self,
        data: ProjectCreate,
        current_user: User,
        client_ip: str = "unknown"
    ) -> Dict[str, Any]:
        """Create a new project with optional technologies, deployment links, and skills."""
        profile_id = self._get_active_profile_id()

        # 1. Validate Project Name Duplicate
        existing = self.repo.get_by_profile_and_name(profile_id, data.name)
        if existing:
            raise ConflictError(f"A project named '{data.name.strip()}' already exists.")

        # 2. Assign Display Order if default
        display_order = data.display_order
        if display_order <= 0:
            display_order = self.repo.get_max_display_order(profile_id) + 1

        # 3. Create Project Instance
        new_project = Project(
            profile_id=profile_id,
            name=data.name.strip(),
            short_description=data.short_description,
            description=data.description,
            status=data.status or "Completed",
            start_month=data.start_month,
            start_year=data.start_year,
            end_month=data.end_month if not data.is_current else None,
            end_year=data.end_year if not data.is_current else None,
            is_current=data.is_current,
            is_featured=data.is_featured,
            is_visible=data.is_visible,
            display_order=display_order
        )
        self.db.add(new_project)
        self.db.flush()

        # 4. Attach Technologies
        if data.technologies:
            self._sync_project_technologies(new_project, data.technologies)

        # 5. Attach Multiple Links
        if data.links:
            self._sync_project_links(new_project, data.links)

        # 6. Attach Skills
        if data.skill_ids:
            self._sync_project_skills(new_project, data.skill_ids)

        self.db.commit()
        refreshed = self.repo.get_by_id(new_project.id)
        snapshot = project_to_dict(refreshed, public=False)

        # 7. Audit & Content Revision
        record_content_revision(
            db=self.db,
            entity_name="project",
            action="CREATE",
            entity_id=str(refreshed.id),
            editor_username=current_user.username,
            change_summary=f"Created project '{refreshed.name}'",
            previous_snapshot=None,
            current_snapshot=snapshot
        )
        log_audit_event(
            db=self.db,
            event_type="PROJECT_CREATED",
            status="SUCCESS",
            user_id=current_user.id,
            username=current_user.username,
            details={"project_id": refreshed.id, "name": refreshed.name},
            ip_address=client_ip
        )

        return snapshot

    def update_project(
        self,
        project_id: int,
        data: ProjectUpdate,
        current_user: User,
        client_ip: str = "unknown"
    ) -> Dict[str, Any]:
        """Full update of an existing project."""
        project = self.repo.get_by_id(project_id)
        if not project:
            raise ResourceNotFoundError(f"Project with ID {project_id} not found.")

        # Duplicate name check
        if data.name.strip().lower() != project.name.lower():
            dup = self.repo.get_by_profile_and_name(project.profile_id, data.name, exclude_id=project_id)
            if dup:
                raise ConflictError(f"A project named '{data.name.strip()}' already exists.")

        prev_snapshot = project_to_dict(project, public=False)

        # Update core fields
        project.name = data.name.strip()
        project.short_description = data.short_description
        project.description = data.description
        project.status = data.status or "Completed"
        project.start_month = data.start_month
        project.start_year = data.start_year
        project.end_month = data.end_month if not data.is_current else None
        project.end_year = data.end_year if not data.is_current else None
        project.is_current = data.is_current
        project.is_featured = data.is_featured
        project.is_visible = data.is_visible
        project.display_order = data.display_order
        project.updated_at = datetime.now(timezone.utc)

        # Synchronize child entities if passed
        if data.technologies is not None:
            self._sync_project_technologies(project, data.technologies)

        if data.links is not None:
            self._sync_project_links(project, data.links)

        if data.skill_ids is not None:
            self._sync_project_skills(project, data.skill_ids)

        self.db.commit()
        refreshed = self.repo.get_by_id(project.id)
        current_snapshot = project_to_dict(refreshed, public=False)

        # Audit & Revision
        record_content_revision(
            db=self.db,
            entity_name="project",
            action="UPDATE",
            entity_id=str(refreshed.id),
            editor_username=current_user.username,
            change_summary=f"Updated project '{refreshed.name}'",
            previous_snapshot=prev_snapshot,
            current_snapshot=current_snapshot
        )
        log_audit_event(
            db=self.db,
            event_type="PROJECT_UPDATED",
            status="SUCCESS",
            user_id=current_user.id,
            username=current_user.username,
            details={"project_id": refreshed.id, "name": refreshed.name},
            ip_address=client_ip
        )

        return current_snapshot

    def patch_project(
        self,
        project_id: int,
        data: ProjectPatch,
        current_user: User,
        client_ip: str = "unknown"
    ) -> Dict[str, Any]:
        """Partial update of an existing project."""
        project = self.repo.get_by_id(project_id)
        if not project:
            raise ResourceNotFoundError(f"Project with ID {project_id} not found.")

        prev_snapshot = project_to_dict(project, public=False)

        # Validate name if changed
        if data.name is not None and data.name.strip().lower() != project.name.lower():
            dup = self.repo.get_by_profile_and_name(project.profile_id, data.name, exclude_id=project_id)
            if dup:
                raise ConflictError(f"A project named '{data.name.strip()}' already exists.")
            project.name = data.name.strip()

        if data.short_description is not None:
            project.short_description = data.short_description
        if data.description is not None:
            project.description = data.description
        if data.status is not None:
            project.status = data.status
        if data.start_month is not None:
            project.start_month = data.start_month
        if data.start_year is not None:
            project.start_year = data.start_year
        if data.end_month is not None:
            project.end_month = data.end_month
        if data.end_year is not None:
            project.end_year = data.end_year
        if data.is_current is not None:
            project.is_current = data.is_current
            if project.is_current:
                project.end_month = None
                project.end_year = None
        if data.is_featured is not None:
            project.is_featured = data.is_featured
        if data.is_visible is not None:
            project.is_visible = data.is_visible
        if data.display_order is not None:
            project.display_order = data.display_order

        # Date consistency validation
        if not project.is_current and project.start_year and project.end_year:
            if project.end_year < project.start_year or (
                project.end_year == project.start_year
                and project.start_month
                and project.end_month
                and project.end_month < project.start_month
            ):
                raise ValidationFailedError("End date cannot precede start date.")

        project.updated_at = datetime.now(timezone.utc)

        if data.technologies is not None:
            self._sync_project_technologies(project, data.technologies)

        if data.links is not None:
            self._sync_project_links(project, data.links)

        if data.skill_ids is not None:
            self._sync_project_skills(project, data.skill_ids)

        self.db.commit()
        refreshed = self.repo.get_by_id(project.id)
        current_snapshot = project_to_dict(refreshed, public=False)

        record_content_revision(
            db=self.db,
            entity_name="project",
            action="PATCH",
            entity_id=str(refreshed.id),
            editor_username=current_user.username,
            change_summary=f"Patched project '{refreshed.name}'",
            previous_snapshot=prev_snapshot,
            current_snapshot=current_snapshot
        )
        log_audit_event(
            db=self.db,
            event_type="PROJECT_PATCHED",
            status="SUCCESS",
            user_id=current_user.id,
            username=current_user.username,
            details={"project_id": refreshed.id, "name": refreshed.name},
            ip_address=client_ip
        )

        return current_snapshot

    def delete_project(
        self,
        project_id: int,
        current_user: User,
        client_ip: str = "unknown"
    ) -> Dict[str, Any]:
        """Delete project safely with cascade removal of link/tech associations."""
        project = self.repo.get_by_id(project_id)
        if not project:
            raise ResourceNotFoundError(f"Project with ID {project_id} not found.")

        prev_snapshot = project_to_dict(project, public=False)
        project_name = project.name

        self.db.delete(project)
        self.db.commit()

        # Audit & Revision
        record_content_revision(
            db=self.db,
            entity_name="project",
            action="DELETE",
            entity_id=str(project_id),
            editor_username=current_user.username,
            change_summary=f"Deleted project '{project_name}'",
            previous_snapshot=prev_snapshot,
            current_snapshot=None
        )
        log_audit_event(
            db=self.db,
            event_type="PROJECT_DELETED",
            status="SUCCESS",
            user_id=current_user.id,
            username=current_user.username,
            details={"project_id": project_id, "name": project_name},
            ip_address=client_ip
        )

        return {"success": True, "message": f"Project '{project_name}' deleted successfully."}

    def reorder_projects(
        self,
        items: List[ProjectReorderItem],
        current_user: User,
        client_ip: str = "unknown"
    ) -> List[Dict[str, Any]]:
        """Bulk reorder projects transactionally."""
        profile_id = self._get_active_profile_id()
        all_projects = self.repo.list_projects(profile_id=profile_id, include_hidden=True)
        valid_ids = {p.id for p in all_projects}

        for item in items:
            if item.id not in valid_ids:
                raise ResourceNotFoundError(f"Project with ID {item.id} does not exist.")

        reorder_dicts = [{"id": it.id, "display_order": it.display_order} for it in items]
        reordered = self.repo.reorder_projects(reorder_dicts, profile_id=profile_id)
        self.db.commit()

        log_audit_event(
            db=self.db,
            event_type="PROJECTS_REORDERED",
            status="SUCCESS",
            user_id=current_user.id,
            username=current_user.username,
            details={"item_count": len(items)},
            ip_address=client_ip
        )

        return [project_to_dict(p, public=False) for p in reordered]

    # -------------------------------------------------------------------------
    # GitHub Extraction & Bulk Import
    # -------------------------------------------------------------------------

    def extract_from_github(
        self,
        github_url: str,
        custom_token: Optional[str] = None
    ) -> Dict[str, Any]:
        """Extract repositories, tech stacks, links, and synthesized AI dossiers from GitHub."""
        try:
            return extract_github_projects(github_url, custom_token)
        except ValueError as e:
            raise ValidationFailedError(str(e))
        except Exception as e:
            raise ValidationFailedError(f"GitHub extraction failed: {str(e)}")

    def generate_project_ai_dossier(
        self,
        data: ProjectAiDossierGenerateRequest
    ) -> Dict[str, str]:
        """
        Synthesizes a massively big, advancedly detailed, super-simple project dossier on demand.
        Uses everyday physical analogies and zero condescending references.
        """
        tech_items = []
        for t in data.technologies:
            if isinstance(t, str):
                t_str = t.strip()
                if t_str:
                    norm_name, cat, rat = categorize_technology(t_str)
                    tech_items.append({"name": norm_name, "category": cat, "rationale": rat})
            elif isinstance(t, dict):
                t_name = (t.get("name") or "").strip()
                if t_name:
                    t_cat = t.get("category") or "Other"
                    norm_name, cat, rat = categorize_technology(t_name)
                    tech_items.append({"name": norm_name, "category": t_cat or cat, "rationale": rat})

        clean_links = []
        for idx, l in enumerate(data.links or []):
            if isinstance(l, dict) and l.get("url"):
                clean_links.append({
                    "label": l.get("label") or "Project Link",
                    "url": l.get("url"),
                    "link_type": l.get("link_type") or "Other",
                    "is_primary": bool(l.get("is_primary", idx == 0))
                })

        short_desc, full_dossier = generate_simple_ai_dossier(
            project_name=data.name.strip(),
            raw_desc=data.raw_description or "",
            language=data.language,
            topics=data.topics or [],
            tech_items=tech_items,
            links=clean_links,
            stars=data.stars,
            forks=data.forks,
            readme_snippet=""
        )
        return {
            "short_description": short_desc,
            "description": full_dossier
        }

    def bulk_import_projects(
        self,
        projects_data: List[ProjectCreate],
        current_user: User,
        client_ip: str = "unknown"
    ) -> List[Dict[str, Any]]:
        """
        Bulk import extracted or custom projects into portfolio transactionally.
        Gracefully updates existing projects or creates new ones.
        """
        profile_id = self._get_active_profile_id()
        results: List[Project] = []
        max_order = self.repo.get_max_display_order(profile_id)

        for idx, data in enumerate(projects_data):
            clean_name = data.name.strip()
            if not clean_name:
                continue

            existing = self.repo.get_by_profile_and_name(profile_id, clean_name)
            display_order = data.display_order if data.display_order > 0 else (max_order + idx + 1)

            if existing:
                # Update existing project with latest details
                if data.short_description:
                    existing.short_description = data.short_description
                if data.description:
                    existing.description = data.description
                if data.status:
                    existing.status = data.status
                if data.start_month is not None:
                    existing.start_month = data.start_month
                if data.start_year is not None:
                    existing.start_year = data.start_year
                if data.end_month is not None and not data.is_current:
                    existing.end_month = data.end_month
                if data.end_year is not None and not data.is_current:
                    existing.end_year = data.end_year
                existing.is_current = data.is_current
                if data.is_featured is not None:
                    existing.is_featured = data.is_featured
                if data.is_visible is not None:
                    existing.is_visible = data.is_visible

                if data.technologies:
                    self._sync_project_technologies(existing, data.technologies)
                if data.links:
                    self._sync_project_links(existing, data.links)
                if data.skill_ids:
                    self._sync_project_skills(existing, data.skill_ids)

                target_proj = existing
            else:
                # Create new project
                new_project = Project(
                    profile_id=profile_id,
                    name=clean_name,
                    short_description=data.short_description,
                    description=data.description,
                    status=data.status or "Completed",
                    start_month=data.start_month,
                    start_year=data.start_year,
                    end_month=data.end_month if not data.is_current else None,
                    end_year=data.end_year if not data.is_current else None,
                    is_current=data.is_current,
                    is_featured=data.is_featured,
                    is_visible=data.is_visible,
                    display_order=display_order
                )
                self.db.add(new_project)
                self.db.flush()

                if data.technologies:
                    self._sync_project_technologies(new_project, data.technologies)
                if data.links:
                    self._sync_project_links(new_project, data.links)
                if data.skill_ids:
                    self._sync_project_skills(new_project, data.skill_ids)

                target_proj = new_project

            results.append(target_proj)

        self.db.commit()

        # Build output models
        output_list = []
        for p in results:
            refreshed = self.repo.get_by_id(p.id)
            if refreshed:
                output_list.append(project_to_dict(refreshed, public=False))

        # Log content revision & audit
        record_content_revision(
            db=self.db,
            entity_name="project",
            action="BULK_IMPORT",
            entity_id="bulk",
            editor_username=current_user.username,
            change_summary=f"Bulk imported {len(output_list)} projects",
            previous_snapshot=None,
            current_snapshot={"imported_count": len(output_list)}
        )
        self.db.commit()

        log_audit_event(
            db=self.db,
            event_type="PROJECTS_BULK_IMPORTED",
            status="SUCCESS",
            user_id=current_user.id,
            username=current_user.username,
            details={"imported_count": len(output_list)},
            ip_address=client_ip
        )
        self.db.commit()

        return output_list

    # -------------------------------------------------------------------------
    # GitHub Account Link & Automatic Synchronization
    # -------------------------------------------------------------------------

    def get_github_link(self) -> Optional[Dict[str, Any]]:
        """Fetch linked GitHub account configuration for the active profile."""
        profile_id = self._get_active_profile_id()
        link = self.repo.get_github_link(profile_id)
        if not link:
            return None
        return {
            "id": link.id,
            "profile_id": link.profile_id,
            "github_url": link.github_url,
            "username": link.username,
            "auto_sync": link.auto_sync,
            "webhook_secret": link.webhook_secret,
            "last_synced_at": link.last_synced_at,
            "last_sync_status": link.last_sync_status,
            "last_sync_summary": link.last_sync_summary,
            "created_at": link.created_at,
            "updated_at": link.updated_at
        }

    def save_github_link(
        self,
        data: GitHubAccountLinkCreate,
        current_user: User,
        client_ip: str = "unknown"
    ) -> Dict[str, Any]:
        """Link or update a GitHub account for the portfolio and run initial sync."""
        profile_id = self._get_active_profile_id()
        try:
            owner, _ = parse_github_target(data.github_url)
        except ValueError as e:
            raise ValidationFailedError(str(e))

        link_record = self.repo.save_github_link(
            profile_id=profile_id,
            github_url=data.github_url,
            username=owner,
            custom_token=data.custom_token,
            auto_sync=data.auto_sync,
            webhook_secret=data.webhook_secret
        )
        self.db.commit()
        self.db.refresh(link_record)

        log_audit_event(
            db=self.db,
            event_type="GITHUB_ACCOUNT_LINKED",
            status="SUCCESS",
            user_id=current_user.id,
            username=current_user.username,
            details={"github_url": link_record.github_url, "username": link_record.username, "auto_sync": link_record.auto_sync},
            ip_address=client_ip
        )
        self.db.commit()

        # Run initial sync if auto_sync enabled
        if data.auto_sync:
            try:
                self.sync_github_account(current_user=current_user, client_ip=client_ip)
                self.db.refresh(link_record)
            except Exception as exc:
                link_record.last_sync_status = "error"
                link_record.last_sync_summary = f"Initial sync issue: {str(exc)}"
                self.db.commit()
                self.db.refresh(link_record)

        return {
            "id": link_record.id,
            "profile_id": link_record.profile_id,
            "github_url": link_record.github_url,
            "username": link_record.username,
            "auto_sync": link_record.auto_sync,
            "webhook_secret": link_record.webhook_secret,
            "last_synced_at": link_record.last_synced_at,
            "last_sync_status": link_record.last_sync_status,
            "last_sync_summary": link_record.last_sync_summary,
            "created_at": link_record.created_at,
            "updated_at": link_record.updated_at
        }

    def unlink_github_account(
        self,
        current_user: User,
        client_ip: str = "unknown"
    ) -> Dict[str, Any]:
        """Remove linked GitHub account."""
        profile_id = self._get_active_profile_id()
        deleted = self.repo.delete_github_link(profile_id)
        if not deleted:
            raise ResourceNotFoundError("No linked GitHub account found.")
        self.db.commit()

        log_audit_event(
            db=self.db,
            event_type="GITHUB_ACCOUNT_UNLINKED",
            status="SUCCESS",
            user_id=current_user.id,
            username=current_user.username,
            details={"profile_id": profile_id},
            ip_address=client_ip
        )
        self.db.commit()
        return {"success": True, "message": "GitHub account unlinked successfully."}

    def sync_github_account(
        self,
        custom_url: Optional[str] = None,
        force: bool = False,
        current_user: Optional[User] = None,
        client_ip: str = "unknown"
    ) -> Dict[str, Any]:
        """
        Synchronize repositories from GitHub:
        - Extracts new repositories and creates portfolio projects with mandatory GitHub links, optional deployments, and AI dossiers.
        - Detects modifications in existing repositories: clears removed technologies, adds new technologies, and re-synthesizes AI descriptions and architecture.
        """
        profile_id = self._get_active_profile_id()
        link_record = self.repo.get_github_link(profile_id)

        target_url = custom_url or (link_record.github_url if link_record else None)
        if not target_url:
            raise ResourceNotFoundError("No GitHub account is currently linked. Please link your GitHub account first.")

        custom_token = link_record.custom_token if link_record else None

        if link_record:
            link_record.last_sync_status = "syncing"
            self.db.commit()

        try:
            extracted = extract_github_projects(target_url, custom_token)
        except Exception as e:
            if link_record:
                link_record.last_sync_status = "error"
                link_record.last_sync_summary = str(e)
                self.db.commit()
            raise ValidationFailedError(f"GitHub synchronization failed: {str(e)}")

        created_projects: List[str] = []
        updated_projects: List[str] = []
        max_order = self.repo.get_max_display_order(profile_id)

        for p_data in extracted.get("projects", []):
            repo_url = p_data.get("repo_url", "")
            clean_name = p_data.get("name", "").strip()

            # 1. Match by repository URL first
            existing = self.repo.find_project_by_github_url(profile_id, repo_url) if repo_url else None
            
            # 2. Fallback match by name
            if not existing and clean_name:
                existing = self.repo.get_by_profile_and_name(profile_id, clean_name)

            if existing:
                # Update existing repository project
                # Re-synthesized AI description & short description reflecting current stack
                existing.description = p_data.get("description")
                existing.short_description = p_data.get("short_description")
                if p_data.get("status"):
                    existing.status = p_data["status"]
                if p_data.get("start_year") is not None:
                    existing.start_year = p_data["start_year"]
                if p_data.get("start_month") is not None:
                    existing.start_month = p_data["start_month"]
                if p_data.get("end_year") is not None and not existing.is_current:
                    existing.end_year = p_data["end_year"]
                if p_data.get("end_month") is not None and not existing.is_current:
                    existing.end_month = p_data["end_month"]

                # Automatically update tech stack: clears deleted technologies, adds new ones!
                self._sync_project_technologies(existing, p_data.get("technologies", []))

                # Automatically update links: updates mandatory GitHub link and detected deployments
                self._sync_project_links(existing, p_data.get("links", []))

                existing.updated_at = datetime.now(timezone.utc)
                updated_projects.append(existing.name)
            else:
                # Create brand new project
                max_order += 1
                new_project = Project(
                    profile_id=profile_id,
                    name=clean_name,
                    short_description=p_data.get("short_description"),
                    description=p_data.get("description"),
                    status=p_data.get("status", "Completed"),
                    start_month=p_data.get("start_month"),
                    start_year=p_data.get("start_year"),
                    end_month=p_data.get("end_month"),
                    end_year=p_data.get("end_year"),
                    is_current=False,
                    is_featured=p_data.get("is_featured", False),
                    is_visible=True,
                    display_order=max_order
                )
                self.db.add(new_project)
                self.db.flush()

                self._sync_project_technologies(new_project, p_data.get("technologies", []))
                self._sync_project_links(new_project, p_data.get("links", []))

                created_projects.append(new_project.name)

        # Update link_record status
        if link_record:
            link_record.last_synced_at = datetime.now(timezone.utc)
            link_record.last_sync_status = "success"
            link_record.last_sync_summary = f"Synced {len(created_projects)} new, {len(updated_projects)} updated."
            self.db.commit()
            self.db.refresh(link_record)
        else:
            self.db.commit()

        # Audit revision logging
        user_name = current_user.username if current_user else "System/GitHub-Sync"
        user_id = current_user.id if current_user else None

        record_content_revision(
            db=self.db,
            entity_name="project",
            action="GITHUB_SYNC",
            entity_id="bulk_sync",
            editor_username=user_name,
            change_summary=f"GitHub sync: {len(created_projects)} created, {len(updated_projects)} updated",
            previous_snapshot=None,
            current_snapshot={"created": created_projects, "updated": updated_projects}
        )
        self.db.commit()

        log_audit_event(
            db=self.db,
            event_type="GITHUB_SYNC_COMPLETED",
            status="SUCCESS",
            user_id=user_id,
            username=user_name,
            details={
                "target_url": target_url,
                "created_count": len(created_projects),
                "updated_count": len(updated_projects)
            },
            ip_address=client_ip
        )
        self.db.commit()

        return {
            "status": "success",
            "message": f"Successfully synchronized GitHub projects: {len(created_projects)} added, {len(updated_projects)} updated.",
            "username": extracted.get("username", "github"),
            "total_found": extracted.get("projects_count", 0),
            "created_count": len(created_projects),
            "updated_count": len(updated_projects),
            "created_projects": created_projects,
            "updated_projects": updated_projects,
            "synced_at": datetime.now(timezone.utc)
        }

    def handle_github_webhook(
        self,
        payload: Dict[str, Any],
        event_type: str = "push",
        signature: Optional[str] = None,
        raw_body: Optional[bytes] = None
    ) -> Dict[str, Any]:
        """
        Handle incoming GitHub webhooks for real-time automatic synchronization.
        Supports 'ping', 'push', and 'repository' events.
        """
        if event_type == "ping":
            return {"status": "success", "message": "Pong! Existence CMS Webhook listener is active."}

        repo_info = payload.get("repository") or {}
        repo_html_url = repo_info.get("html_url")
        owner_info = repo_info.get("owner") or {}
        owner_login = owner_info.get("login")

        if not repo_html_url or not owner_login:
            return {"status": "ignored", "message": "Webhook payload does not contain repository details."}

        # Check linked account
        linked_account = self.repo.get_github_link_by_username(owner_login)
        if linked_account and linked_account.webhook_secret and signature and raw_body:
            # Verify HMAC signature
            secret_bytes = linked_account.webhook_secret.encode("utf-8")
            expected_sig = "sha256=" + hmac.new(secret_bytes, raw_body, hashlib.sha256).hexdigest()
            if not hmac.compare_digest(expected_sig, signature):
                raise ValidationFailedError("Invalid webhook signature.")

        # Sync this repository
        try:
            sync_res = self.sync_github_account(custom_url=repo_html_url, client_ip="github-webhook")
            return {
                "status": "success",
                "event": event_type,
                "repository": repo_html_url,
                "result": sync_res
            }
        except Exception as e:
            return {
                "status": "error",
                "event": event_type,
                "repository": repo_html_url,
                "error": str(e)
            }


    # -------------------------------------------------------------------------
    # Dedicated Project Link Operations
    # -------------------------------------------------------------------------

    def add_project_link(
        self,
        project_id: int,
        link_data: ProjectLinkCreate,
        current_user: User,
        client_ip: str = "unknown"
    ) -> Dict[str, Any]:
        """Add a deployment/demo link to an existing project."""
        project = self.repo.get_by_id(project_id)
        if not project:
            raise ResourceNotFoundError(f"Project with ID {project_id} not found.")

        # Check duplicate URL within same project
        dup = self.repo.get_project_link_by_url(project_id, link_data.url)
        if dup:
            raise ConflictError(f"Link with URL '{link_data.url}' already exists on this project.")

        # Primary link integrity: if marked primary, unset other primary links
        if link_data.is_primary:
            self.repo.unset_primary_links(project_id)

        display_order = link_data.display_order
        if display_order <= 0:
            display_order = self.repo.get_max_link_display_order(project_id) + 1

        new_link = ProjectLink(
            project_id=project_id,
            label=link_data.label.strip(),
            url=link_data.url.strip(),
            link_type=link_data.link_type,
            is_primary=link_data.is_primary,
            is_visible=link_data.is_visible,
            display_order=display_order
        )
        self.db.add(new_link)
        self.db.commit()
        self.db.refresh(new_link)

        # Audit
        log_audit_event(
            db=self.db,
            event_type="PROJECT_LINK_ADDED",
            status="SUCCESS",
            user_id=current_user.id,
            username=current_user.username,
            details={"project_id": project_id, "link_id": new_link.id, "label": new_link.label, "url": new_link.url},
            ip_address=client_ip
        )

        return {
            "id": new_link.id,
            "project_id": new_link.project_id,
            "label": new_link.label,
            "url": new_link.url,
            "link_type": new_link.link_type,
            "is_primary": new_link.is_primary,
            "is_visible": new_link.is_visible,
            "display_order": new_link.display_order,
            "created_at": new_link.created_at,
            "updated_at": new_link.updated_at
        }

    def update_project_link(
        self,
        project_id: int,
        link_id: int,
        link_data: ProjectLinkUpdate,
        current_user: User,
        client_ip: str = "unknown"
    ) -> Dict[str, Any]:
        """Update an existing project link."""
        link = self.repo.get_link_by_id(link_id)
        if not link or link.project_id != project_id:
            raise ResourceNotFoundError(f"Project link with ID {link_id} not found on project {project_id}.")

        # Check duplicate URL
        dup = self.repo.get_project_link_by_url(project_id, link_data.url, exclude_link_id=link_id)
        if dup:
            raise ConflictError(f"Another link with URL '{link_data.url}' already exists on this project.")

        if link_data.is_primary and not link.is_primary:
            self.repo.unset_primary_links(project_id, except_link_id=link_id)

        link.label = link_data.label.strip()
        link.url = link_data.url.strip()
        link.link_type = link_data.link_type
        link.is_primary = link_data.is_primary
        link.is_visible = link_data.is_visible
        link.display_order = link_data.display_order
        link.updated_at = datetime.now(timezone.utc)

        self.db.commit()
        self.db.refresh(link)

        log_audit_event(
            db=self.db,
            event_type="PROJECT_LINK_UPDATED",
            status="SUCCESS",
            user_id=current_user.id,
            username=current_user.username,
            details={"project_id": project_id, "link_id": link.id, "label": link.label},
            ip_address=client_ip
        )

        return {
            "id": link.id,
            "project_id": link.project_id,
            "label": link.label,
            "url": link.url,
            "link_type": link.link_type,
            "is_primary": link.is_primary,
            "is_visible": link.is_visible,
            "display_order": link.display_order,
            "created_at": link.created_at,
            "updated_at": link.updated_at
        }

    def patch_project_link(
        self,
        project_id: int,
        link_id: int,
        link_data: ProjectLinkPatch,
        current_user: User,
        client_ip: str = "unknown"
    ) -> Dict[str, Any]:
        """Partial update of an existing project link."""
        link = self.repo.get_link_by_id(link_id)
        if not link or link.project_id != project_id:
            raise ResourceNotFoundError(f"Project link with ID {link_id} not found on project {project_id}.")

        if link_data.url is not None:
            dup = self.repo.get_project_link_by_url(project_id, link_data.url, exclude_link_id=link_id)
            if dup:
                raise ConflictError(f"Another link with URL '{link_data.url}' already exists on this project.")
            link.url = link_data.url.strip()

        if link_data.label is not None:
            link.label = link_data.label.strip()
        if link_data.link_type is not None:
            link.link_type = link_data.link_type
        if link_data.is_primary is not None:
            if link_data.is_primary and not link.is_primary:
                self.repo.unset_primary_links(project_id, except_link_id=link_id)
            link.is_primary = link_data.is_primary
        if link_data.is_visible is not None:
            link.is_visible = link_data.is_visible
        if link_data.display_order is not None:
            link.display_order = link_data.display_order

        link.updated_at = datetime.now(timezone.utc)
        self.db.commit()
        self.db.refresh(link)

        return {
            "id": link.id,
            "project_id": link.project_id,
            "label": link.label,
            "url": link.url,
            "link_type": link.link_type,
            "is_primary": link.is_primary,
            "is_visible": link.is_visible,
            "display_order": link.display_order,
            "created_at": link.created_at,
            "updated_at": link.updated_at
        }

    def delete_project_link(
        self,
        project_id: int,
        link_id: int,
        current_user: User,
        client_ip: str = "unknown"
    ) -> Dict[str, Any]:
        """Delete a project link safely."""
        link = self.repo.get_link_by_id(link_id)
        if not link or link.project_id != project_id:
            raise ResourceNotFoundError(f"Project link with ID {link_id} not found on project {project_id}.")

        label = link.label
        self.db.delete(link)
        self.db.commit()

        log_audit_event(
            db=self.db,
            event_type="PROJECT_LINK_DELETED",
            status="SUCCESS",
            user_id=current_user.id,
            username=current_user.username,
            details={"project_id": project_id, "link_id": link_id, "label": label},
            ip_address=client_ip
        )

        return {"success": True, "message": f"Project link '{label}' deleted successfully."}

    def reorder_project_links(
        self,
        project_id: int,
        items: List[ProjectLinkReorderItem],
        current_user: User,
        client_ip: str = "unknown"
    ) -> List[Dict[str, Any]]:
        """Reorder project links deterministically."""
        project = self.repo.get_by_id(project_id)
        if not project:
            raise ResourceNotFoundError(f"Project with ID {project_id} not found.")

        existing_link_ids = {l.id for l in project.links}
        for item in items:
            if item.id not in existing_link_ids:
                raise ResourceNotFoundError(f"Link with ID {item.id} does not belong to project {project_id}.")

        reorder_dicts = [{"id": it.id, "display_order": it.display_order} for it in items]
        reordered = self.repo.reorder_links(project_id, reorder_dicts)
        self.db.commit()

        log_audit_event(
            db=self.db,
            event_type="PROJECT_LINKS_REORDERED",
            status="SUCCESS",
            user_id=current_user.id,
            username=current_user.username,
            details={"project_id": project_id, "item_count": len(items)},
            ip_address=client_ip
        )

        return [
            {
                "id": l.id,
                "project_id": l.project_id,
                "label": l.label,
                "url": l.url,
                "link_type": l.link_type,
                "is_primary": l.is_primary,
                "is_visible": l.is_visible,
                "display_order": l.display_order,
                "created_at": l.created_at,
                "updated_at": l.updated_at
            }
            for l in reordered
        ]

    # -------------------------------------------------------------------------
    # Internal Child Synchronization Helpers
    # -------------------------------------------------------------------------

    def _sync_project_technologies(
        self,
        project: Project,
        tech_inputs: List[Union[str, ProjectTechnologyInput]]
    ) -> None:
        """
        Synchronize technologies on a project without duplicate relationships.
        Reuses existing canonical Technology entities.
        """
        # Clear existing associations
        self.db.query(ProjectTechnology).filter(ProjectTechnology.project_id == project.id).delete()
        self.db.flush()

        seen_names = set()
        order = 0
        for item in tech_inputs:
            if isinstance(item, str):
                name = item.strip()
                cat = "Other"
            elif isinstance(item, ProjectTechnologyInput):
                name = item.name.strip()
                cat = item.category or "Other"
            elif isinstance(item, dict):
                name = item.get("name", "").strip()
                cat = item.get("category", "Other")
            else:
                continue

            if not name:
                continue

            norm_name = name.lower()
            if norm_name in seen_names:
                continue  # Prevent duplicates within same project
            seen_names.add(norm_name)

            tech_entity = self.repo.get_or_create_technology(name, category=cat)
            proj_tech = ProjectTechnology(
                project_id=project.id,
                technology_id=tech_entity.id,
                display_order=order
            )
            self.db.add(proj_tech)
            order += 1
        self.db.flush()

    def _sync_project_links(
        self,
        project: Project,
        link_inputs: List[ProjectLinkCreate]
    ) -> None:
        """Synchronize links on a project, ensuring URL uniqueness and at most 1 primary link."""
        self.db.query(ProjectLink).filter(ProjectLink.project_id == project.id).delete()
        self.db.flush()

        seen_urls = set()
        primary_assigned = False
        order = 0

        for l_in in link_inputs:
            if isinstance(l_in, dict):
                l_obj = ProjectLinkCreate(**l_in)
            else:
                l_obj = l_in

            url_key = l_obj.url.strip().lower()
            if url_key in seen_urls:
                continue
            seen_urls.add(url_key)

            # At most one primary link
            is_pri = l_obj.is_primary
            if is_pri and not primary_assigned:
                primary_assigned = True
            elif is_pri and primary_assigned:
                is_pri = False

            link_rec = ProjectLink(
                project_id=project.id,
                label=l_obj.label.strip(),
                url=l_obj.url.strip(),
                link_type=l_obj.link_type,
                is_primary=is_pri,
                is_visible=l_obj.is_visible,
                display_order=l_obj.display_order if l_obj.display_order > 0 else order
            )
            self.db.add(link_rec)
            order += 1
        self.db.flush()

    def _sync_project_skills(
        self,
        project: Project,
        skill_ids: List[int]
    ) -> None:
        """Associate existing verified skills with the project."""
        self.db.query(ProjectSkill).filter(ProjectSkill.project_id == project.id).delete()
        self.db.flush()

        valid_skills = self.db.query(Skill).filter(Skill.id.in_(skill_ids)).all()
        for sk in valid_skills:
            ps = ProjectSkill(project_id=project.id, skill_id=sk.id)
            self.db.add(ps)
        self.db.flush()
