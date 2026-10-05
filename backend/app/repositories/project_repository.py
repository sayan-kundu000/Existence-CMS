from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session, joinedload, selectinload
from sqlalchemy import func, or_
from app.models.project import (
    Project,
    ProjectLink,
    Technology,
    ProjectTechnology,
    ProjectSkill,
    GitHubAccountLink
)
from app.repositories.base import BaseRepository


class ProjectRepository(BaseRepository[Project]):
    def __init__(self, db: Session):
        super().__init__(Project, db)

    def get_by_id(self, project_id: int) -> Optional[Project]:
        """Fetch single project with full eager loading of links, technologies, and skills."""
        return (
            self.db.query(Project)
            .options(
                selectinload(Project.links),
                selectinload(Project.project_technologies).joinedload(ProjectTechnology.technology),
                selectinload(Project.project_skills).joinedload(ProjectSkill.skill)
            )
            .filter(Project.id == project_id)
            .first()
        )

    def get_by_profile_and_name(
        self,
        profile_id: Optional[int],
        name: str,
        exclude_id: Optional[int] = None
    ) -> Optional[Project]:
        """Check duplicate project name under profile (case-insensitive)."""
        clean = name.strip().lower()
        query = self.db.query(Project).filter(
            func.lower(Project.name) == clean
        )
        if profile_id is not None:
            query = query.filter(Project.profile_id == profile_id)
        if exclude_id is not None:
            query = query.filter(Project.id != exclude_id)
        return query.first()

    def list_projects(
        self,
        profile_id: Optional[int] = None,
        include_hidden: bool = False,
        search: Optional[str] = None,
        status: Optional[str] = None,
        technology: Optional[str] = None,
        is_featured: Optional[bool] = None,
        sort_by: str = "order"
    ) -> List[Project]:
        """
        Query projects deterministically with eager-loading to eliminate N+1 queries.
        Public queries (include_hidden=False) strictly exclude invisible projects.
        """
        query = self.db.query(Project).options(
            selectinload(Project.links),
            selectinload(Project.project_technologies).joinedload(ProjectTechnology.technology),
            selectinload(Project.project_skills).joinedload(ProjectSkill.skill)
        )

        if profile_id is not None:
            query = query.filter(Project.profile_id == profile_id)

        if not include_hidden:
            query = query.filter(Project.is_visible == True)

        if status:
            query = query.filter(Project.status == status)

        if is_featured is not None:
            query = query.filter(Project.is_featured == is_featured)

        if search:
            pattern = f"%{search.strip()}%"
            query = query.filter(
                or_(
                    Project.name.ilike(pattern),
                    Project.short_description.ilike(pattern),
                    Project.description.ilike(pattern)
                )
            )

        if technology:
            tech_clean = technology.strip().lower()
            query = query.join(Project.project_technologies).join(ProjectTechnology.technology).filter(
                func.lower(Technology.name) == tech_clean
            )

        # Ordering strategy
        if sort_by == "name":
            query = query.order_by(Project.name.asc(), Project.id.asc())
        elif sort_by == "updated":
            query = query.order_by(Project.updated_at.desc(), Project.id.asc())
        elif sort_by == "start_date":
            query = query.order_by(
                Project.start_year.desc().nullslast(),
                Project.start_month.desc().nullslast(),
                Project.display_order.asc(),
                Project.id.asc()
            )
        else:
            # Default: manual display order
            query = query.order_by(
                Project.display_order.asc(),
                Project.id.asc()
            )

        return query.all()

    def get_max_display_order(self, profile_id: Optional[int] = None) -> int:
        query = self.db.query(func.max(Project.display_order))
        if profile_id is not None:
            query = query.filter(Project.profile_id == profile_id)
        max_val = query.scalar()
        return max_val if max_val is not None else -1

    def reorder_projects(
        self,
        items: List[Dict[str, int]],
        profile_id: Optional[int] = None
    ) -> List[Project]:
        """Atomically update project display orders."""
        for item in items:
            proj_id = item["id"]
            new_order = item["display_order"]
            q = self.db.query(Project).filter(Project.id == proj_id)
            if profile_id is not None:
                q = q.filter(Project.profile_id == profile_id)
            proj = q.first()
            if proj:
                proj.display_order = new_order
        self.db.flush()
        return self.list_projects(profile_id=profile_id, include_hidden=True)

    # -------------------------------------------------------------------------
    # Technologies
    # -------------------------------------------------------------------------

    def get_or_create_technology(self, name: str, category: Optional[str] = "Other") -> Technology:
        """Find reusable Technology by case-insensitive name, or create one."""
        clean = name.strip()
        existing = (
            self.db.query(Technology)
            .filter(func.lower(Technology.name) == clean.lower())
            .first()
        )
        if existing:
            if category and category != "Other" and existing.category == "Other":
                existing.category = category
                self.db.flush()
            return existing

        new_tech = Technology(name=clean, category=category or "Other")
        self.db.add(new_tech)
        self.db.flush()
        self.db.refresh(new_tech)
        return new_tech

    def list_all_technologies(self) -> List[Technology]:
        return self.db.query(Technology).order_by(Technology.category.asc(), Technology.name.asc()).all()

    # -------------------------------------------------------------------------
    # Project Links
    # -------------------------------------------------------------------------

    def get_link_by_id(self, link_id: int) -> Optional[ProjectLink]:
        return self.db.query(ProjectLink).filter(ProjectLink.id == link_id).first()

    def get_project_link_by_url(self, project_id: int, url: str, exclude_link_id: Optional[int] = None) -> Optional[ProjectLink]:
        clean = url.strip().lower()
        query = self.db.query(ProjectLink).filter(
            ProjectLink.project_id == project_id,
            func.lower(ProjectLink.url) == clean
        )
        if exclude_link_id is not None:
            query = query.filter(ProjectLink.id != exclude_link_id)
        return query.first()

    def unset_primary_links(self, project_id: int, except_link_id: Optional[int] = None) -> None:
        """Ensure at most one primary link exists per project."""
        query = self.db.query(ProjectLink).filter(
            ProjectLink.project_id == project_id,
            ProjectLink.is_primary == True
        )
        if except_link_id is not None:
            query = query.filter(ProjectLink.id != except_link_id)
        for link in query.all():
            link.is_primary = False
        self.db.flush()

    def get_max_link_display_order(self, project_id: int) -> int:
        max_val = (
            self.db.query(func.max(ProjectLink.display_order))
            .filter(ProjectLink.project_id == project_id)
            .scalar()
        )
        return max_val if max_val is not None else -1

    def reorder_links(self, project_id: int, items: List[Dict[str, int]]) -> List[ProjectLink]:
        for item in items:
            link = self.db.query(ProjectLink).filter(
                ProjectLink.id == item["id"],
                ProjectLink.project_id == project_id
            ).first()
            if link:
                link.display_order = item["display_order"]
        self.db.flush()
        return (
            self.db.query(ProjectLink)
            .filter(ProjectLink.project_id == project_id)
            .order_by(ProjectLink.display_order.asc(), ProjectLink.id.asc())
            .all()
        )

    # -------------------------------------------------------------------------
    # GitHub Account Link & Repo Matching
    # -------------------------------------------------------------------------

    def get_github_link(self, profile_id: int) -> Optional[GitHubAccountLink]:
        """Fetch linked GitHub account configuration for a profile."""
        return self.db.query(GitHubAccountLink).filter(GitHubAccountLink.profile_id == profile_id).first()

    def get_github_link_by_username(self, username: str) -> Optional[GitHubAccountLink]:
        """Fetch linked GitHub account by username (case-insensitive)."""
        clean = username.strip().lower()
        return self.db.query(GitHubAccountLink).filter(func.lower(GitHubAccountLink.username) == clean).first()

    def save_github_link(
        self,
        profile_id: int,
        github_url: str,
        username: str,
        custom_token: Optional[str] = None,
        auto_sync: bool = True,
        webhook_secret: Optional[str] = None
    ) -> GitHubAccountLink:
        """Create or update linked GitHub account record."""
        existing = self.get_github_link(profile_id)
        if existing:
            existing.github_url = github_url.strip()
            existing.username = username.strip()
            if custom_token is not None:
                existing.custom_token = custom_token.strip() if custom_token.strip() else None
            existing.auto_sync = auto_sync
            if webhook_secret is not None:
                existing.webhook_secret = webhook_secret.strip() if webhook_secret.strip() else None
            self.db.flush()
            return existing

        new_link = GitHubAccountLink(
            profile_id=profile_id,
            github_url=github_url.strip(),
            username=username.strip(),
            custom_token=custom_token.strip() if (custom_token and custom_token.strip()) else None,
            auto_sync=auto_sync,
            webhook_secret=webhook_secret.strip() if (webhook_secret and webhook_secret.strip()) else None,
            last_sync_status="idle"
        )
        self.db.add(new_link)
        self.db.flush()
        self.db.refresh(new_link)
        return new_link

    def delete_github_link(self, profile_id: int) -> bool:
        """Remove linked GitHub account record."""
        record = self.get_github_link(profile_id)
        if record:
            self.db.delete(record)
            self.db.flush()
            return True
        return False

    def find_project_by_github_url(self, profile_id: int, github_url: str) -> Optional[Project]:
        """
        Find existing project in profile that has a matching GitHub repository URL.
        Normalizes trailing slashes and .git extensions.
        """
        clean_url = github_url.strip().lower()
        if clean_url.endswith(".git"):
            clean_url = clean_url[:-4]
        clean_url = clean_url.rstrip("/")

        # Query all projects with links in this profile
        projects = (
            self.db.query(Project)
            .options(
                selectinload(Project.links),
                selectinload(Project.project_technologies).joinedload(ProjectTechnology.technology),
                selectinload(Project.project_skills).joinedload(ProjectSkill.skill)
            )
            .filter(Project.profile_id == profile_id)
            .all()
        )

        for p in projects:
            for l in (p.links or []):
                link_url = (l.url or "").strip().lower()
                if link_url.endswith(".git"):
                    link_url = link_url[:-4]
                link_url = link_url.rstrip("/")
                if link_url == clean_url:
                    return p

        return None

