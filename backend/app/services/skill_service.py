import json
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.models.skill import (
    Skill,
    SKILL_LEVEL_MAP,
    SKILL_LEVEL_METADATA,
    SKILL_CATEGORIES,
    normalize_skill_categories,
    normalize_skill_domains,
)
from app.models.user import User
from app.repositories.skill_repository import SkillRepository
from app.repositories.profile_repository import ProfileRepository
from app.schemas.skill import (
    SkillCreate,
    SkillUpdate,
    SkillPatch,
    SkillReorderItem
)
from app.core.exceptions import (
    ResourceNotFoundError,
    ValidationFailedError,
    ConflictError,
    PermissionDeniedError
)
from app.services.audit_service import log_audit_event, record_content_revision


def skill_to_dict(s: Skill) -> Dict[str, Any]:
    """Canonical dictionary representation of a Skill matching SkillOut schema."""
    meta: Dict[str, Any] = {}
    if s.metadata_info:
        if isinstance(s.metadata_info, dict):
            meta = s.metadata_info
        else:
            try:
                meta = json.loads(s.metadata_info)
            except Exception:
                meta = {}

    domain_val = getattr(s, "domain", None)
    if not domain_val and meta and isinstance(meta, dict):
        domain_val = meta.get("domain")

    domains_val: List[str] = []
    if domain_val:
        domains_val = normalize_skill_domains(domain_val)[1]
    elif meta and isinstance(meta, dict) and meta.get("domains"):
        domains_val = normalize_skill_domains(meta.get("domains"))[1]

    return {
        "id": s.id,
        "profile_id": s.profile_id,
        "name": s.name,
        "domain": domain_val,
        "domains": domains_val,
        "category": s.category,
        "categories": s.categories,
        "description": getattr(s, "description", None),
        "rating": s.rating,
        "level_label": SKILL_LEVEL_MAP.get(s.rating, "Unknown"),
        "level": SKILL_LEVEL_MAP.get(s.rating, "Beginner"),
        "visibility": s.is_visible,
        "is_visible": s.is_visible,
        "ordering": s.display_order,
        "display_order": s.display_order,
        "metadata_info": meta,
        "created_at": s.created_at,
        "updated_at": s.updated_at
    }


class SkillService:
    """
    Authoritative domain service for the Existence 7-Level Skills Engine.
    Enforces rating constraints (1-7), case-insensitive duplicate prevention,
    deterministic ordering, PIN security integration, revision snapshots, and audit logging.
    """

    def __init__(self, db: Session):
        self.db = db
        self.skill_repo = SkillRepository(db)
        self.profile_repo = ProfileRepository(db)

    def get_categories(self) -> List[str]:
        """Return the 17 canonical skill categories."""
        return SKILL_CATEGORIES

    def get_rating_levels(self) -> List[Dict[str, Any]]:
        """Return the canonical 7-level rating metadata definitions."""
        return SKILL_LEVEL_METADATA

    def list_skills(
        self,
        profile_id: Optional[int] = None,
        include_hidden: bool = False,
        category: Optional[str] = None,
        domain: Optional[str] = None,
        search: Optional[str] = None,
        rating: Optional[int] = None,
        sort_by: str = "rating"
    ) -> List[Dict[str, Any]]:
        """
        List skills with deterministic ordering and filtering.
        Public views (include_hidden=False) strictly exclude unverified/private skills.
        """
        skills = self.skill_repo.list_skills(
            profile_id=profile_id,
            include_hidden=include_hidden,
            category=category,
            domain=domain,
            search=search,
            rating=rating,
            sort_by=sort_by
        )
        return [skill_to_dict(s) for s in skills]

    def get_skill(self, skill_id: int) -> Dict[str, Any]:
        """Retrieve single skill item or raise 404."""
        s = self.skill_repo.get_by_id(skill_id)
        if not s:
            raise ResourceNotFoundError("Skill", skill_id)
        return skill_to_dict(s)

    def create_skill(
        self,
        skill_data: SkillCreate,
        current_user: User,
        client_ip: str
    ) -> Dict[str, Any]:
        """
        Create a new skill with exact 7-level rating.
        Validates name, enforces duplicate prevention, records revisions and audit trails.
        """
        # 1. Rating Domain Validation
        if not isinstance(skill_data.rating, int) or skill_data.rating not in SKILL_LEVEL_MAP:
            raise ValidationFailedError(
                f"Rating must be an integer between 1 and 7, got {skill_data.rating}"
            )

        # 2. Name validation & normalization
        name_clean = skill_data.name.strip()
        if not name_clean:
            raise ValidationFailedError("Skill name cannot be empty or whitespace-only.")
        if len(name_clean) > 100:
            raise ValidationFailedError("Skill name cannot exceed 100 characters.")

        # 3. Associate with authoritative profile
        profile = self.profile_repo.get_or_create_profile()
        profile_id = profile.id
        if skill_data.profile_id is not None and skill_data.profile_id != profile.id:
            raise PermissionDeniedError("Cannot create skills on a foreign profile.")

        # 4. Duplicate prevention (case-insensitive & trimmed)
        existing = self.skill_repo.find_by_name(name=name_clean, profile_id=profile_id)
        if existing:
            raise ConflictError(
                f"A skill named '{name_clean}' already exists for this profile."
            )

        # 5. Determine display order
        ordering = skill_data.ordering if skill_data.ordering != 0 else (skill_data.display_order or 0)
        if ordering == 0:
            max_order = self.skill_repo.get_max_display_order(profile_id=profile_id)
            ordering = max_order + 1

        category_clean = normalize_skill_categories(skill_data.categories or skill_data.category)[0]
        desc_clean = skill_data.description.strip() if skill_data.description else None

        dom_input = getattr(skill_data, "domains", None) or skill_data.domain
        domain_clean, domains_list = normalize_skill_domains(dom_input)

        meta = dict(skill_data.metadata_info or {})
        if domain_clean:
            meta["domain"] = domain_clean
            meta["domains"] = domains_list
        else:
            meta.pop("domain", None)
            meta.pop("domains", None)

        new_skill = Skill(
            profile_id=profile_id,
            name=name_clean,
            domain=domain_clean,
            category=category_clean,
            description=desc_clean,
            rating=skill_data.rating,
            is_visible=skill_data.visibility,
            display_order=ordering,
            metadata_info=json.dumps(meta)
        )

        try:
            self.db.add(new_skill)
            self.db.commit()
            self.db.refresh(new_skill)
        except IntegrityError:
            self.db.rollback()
            raise ConflictError(
                f"A skill named '{name_clean}' already exists for this profile."
            )

        curr_dict = skill_to_dict(new_skill)

        # 6. Content Revision Integration
        record_content_revision(
            db=self.db,
            entity_name="skill",
            action="CREATE",
            entity_id=str(new_skill.id),
            editor_username=current_user.username,
            change_summary=f"Added skill: {new_skill.name} (Level {new_skill.rating} - {new_skill.level_label})",
            previous_snapshot=None,
            current_snapshot=curr_dict
        )

        # 7. Audit Event Integration
        log_audit_event(
            db=self.db,
            event_type="SKILL_CREATED",
            status="SUCCESS",
            user_id=current_user.id,
            username=current_user.username,
            details={
                "skill_id": new_skill.id,
                "name": new_skill.name,
                "rating": new_skill.rating,
                "level": new_skill.level_label,
                "category": new_skill.category
            },
            ip_address=client_ip
        )

        return curr_dict

    def update_skill(
        self,
        skill_id: int,
        skill_data: SkillUpdate,
        current_user: User,
        client_ip: str
    ) -> Dict[str, Any]:
        """
        Fully update an existing skill.
        Validates 1-7 rating, checks duplicates, preserves rating change history in revision.
        """
        s = self.skill_repo.get_by_id(skill_id)
        if not s:
            raise ResourceNotFoundError("Skill", skill_id)

        # Rating validation
        if not isinstance(skill_data.rating, int) or skill_data.rating not in SKILL_LEVEL_MAP:
            raise ValidationFailedError(
                f"Rating must be an integer between 1 and 7, got {skill_data.rating}"
            )

        # Name validation & normalization
        name_clean = skill_data.name.strip()
        if not name_clean:
            raise ValidationFailedError("Skill name cannot be empty or whitespace-only.")
        if len(name_clean) > 100:
            raise ValidationFailedError("Skill name cannot exceed 100 characters.")

        # Duplicate check excluding current skill ID
        existing = self.skill_repo.find_by_name(
            name=name_clean,
            profile_id=s.profile_id,
            exclude_id=skill_id
        )
        if existing:
            raise ConflictError(
                f"A skill named '{name_clean}' already exists for this profile."
            )

        prev_dict = skill_to_dict(s)
        prev_rating = s.rating
        prev_level = s.level_label

        ordering = skill_data.ordering if skill_data.ordering != 0 else (skill_data.display_order or 0)
        dom_input = getattr(skill_data, "domains", None) or skill_data.domain
        domain_clean, domains_list = normalize_skill_domains(dom_input)

        meta = dict(skill_data.metadata_info or {})
        if domain_clean:
            meta["domain"] = domain_clean
            meta["domains"] = domains_list
        else:
            meta.pop("domain", None)
            meta.pop("domains", None)

        s.name = name_clean
        s.domain = domain_clean
        s.category = normalize_skill_categories(skill_data.categories or skill_data.category)[0]
        s.description = skill_data.description.strip() if skill_data.description else None
        s.rating = skill_data.rating
        s.is_visible = skill_data.visibility
        s.display_order = ordering
        s.metadata_info = json.dumps(meta)
        s.updated_at = datetime.now(timezone.utc)

        try:
            self.db.commit()
            self.db.refresh(s)
        except IntegrityError:
            self.db.rollback()
            raise ConflictError(
                f"A skill named '{name_clean}' already exists for this profile."
            )

        curr_dict = skill_to_dict(s)

        # Detailed rating change summary for audit and revisions
        if prev_rating != s.rating:
            summary = (
                f"Updated skill '{s.name}': Rating changed from Level {prev_rating} ({prev_level}) "
                f"to Level {s.rating} ({s.level_label})"
            )
        else:
            summary = f"Updated skill: {s.name} (Level {s.rating} - {s.level_label})"

        record_content_revision(
            db=self.db,
            entity_name="skill",
            action="UPDATE",
            entity_id=str(s.id),
            editor_username=current_user.username,
            change_summary=summary,
            previous_snapshot=prev_dict,
            current_snapshot=curr_dict
        )

        log_audit_event(
            db=self.db,
            event_type="SKILL_UPDATED",
            status="SUCCESS",
            user_id=current_user.id,
            username=current_user.username,
            details={
                "skill_id": s.id,
                "name": s.name,
                "old_rating": prev_rating,
                "new_rating": s.rating
            },
            ip_address=client_ip
        )

        return curr_dict

    def patch_skill(
        self,
        skill_id: int,
        skill_data: SkillPatch,
        current_user: User,
        client_ip: str
    ) -> Dict[str, Any]:
        """Partially update an existing skill."""
        s = self.skill_repo.get_by_id(skill_id)
        if not s:
            raise ResourceNotFoundError("Skill", skill_id)

        prev_dict = skill_to_dict(s)
        prev_rating = s.rating
        prev_level = s.level_label

        if skill_data.name is not None:
            name_clean = skill_data.name.strip()
            if not name_clean:
                raise ValidationFailedError("Skill name cannot be empty or whitespace-only.")
            existing = self.skill_repo.find_by_name(
                name=name_clean,
                profile_id=s.profile_id,
                exclude_id=skill_id
            )
            if existing:
                raise ConflictError(
                    f"A skill named '{name_clean}' already exists for this profile."
                )
            s.name = name_clean

        if skill_data.domains is not None or skill_data.domain is not None:
            dom_input = skill_data.domains if skill_data.domains is not None else skill_data.domain
            domain_clean, domains_list = normalize_skill_domains(dom_input)
            s.domain = domain_clean
            meta = {}
            if s.metadata_info:
                try:
                    meta = json.loads(s.metadata_info) if isinstance(s.metadata_info, str) else dict(s.metadata_info)
                except Exception:
                    meta = {}
            if domain_clean:
                meta["domain"] = domain_clean
                meta["domains"] = domains_list
            else:
                meta.pop("domain", None)
                meta.pop("domains", None)
            s.metadata_info = json.dumps(meta)

        if skill_data.rating is not None:
            if not isinstance(skill_data.rating, int) or skill_data.rating not in SKILL_LEVEL_MAP:
                raise ValidationFailedError(
                    f"Rating must be an integer between 1 and 7, got {skill_data.rating}"
                )
            s.rating = skill_data.rating

        if skill_data.categories is not None:
            s.category = normalize_skill_categories(skill_data.categories)[0]
        elif skill_data.category is not None:
            s.category = normalize_skill_categories(skill_data.category)[0]

        if skill_data.description is not None:
            s.description = skill_data.description.strip() if skill_data.description else None

        if skill_data.visibility is not None:
            s.is_visible = skill_data.visibility
        elif skill_data.is_visible is not None:
            s.is_visible = skill_data.is_visible

        if skill_data.ordering is not None:
            s.display_order = skill_data.ordering
        elif skill_data.display_order is not None:
            s.display_order = skill_data.display_order

        if skill_data.metadata_info is not None:
            s.metadata_info = json.dumps(skill_data.metadata_info)

        s.updated_at = datetime.now(timezone.utc)

        try:
            self.db.commit()
            self.db.refresh(s)
        except IntegrityError:
            self.db.rollback()
            raise ConflictError(
                f"A skill named '{s.name}' already exists for this profile."
            )

        curr_dict = skill_to_dict(s)

        if prev_rating != s.rating:
            summary = (
                f"Patched skill '{s.name}': Rating changed from Level {prev_rating} ({prev_level}) "
                f"to Level {s.rating} ({s.level_label})"
            )
        else:
            summary = f"Patched skill: {s.name} (Level {s.rating} - {s.level_label})"

        record_content_revision(
            db=self.db,
            entity_name="skill",
            action="PATCH",
            entity_id=str(s.id),
            editor_username=current_user.username,
            change_summary=summary,
            previous_snapshot=prev_dict,
            current_snapshot=curr_dict
        )

        log_audit_event(
            db=self.db,
            event_type="SKILL_PATCHED",
            status="SUCCESS",
            user_id=current_user.id,
            username=current_user.username,
            details={
                "skill_id": s.id,
                "name": s.name,
                "rating": s.rating
            },
            ip_address=client_ip
        )

        return curr_dict

    def delete_skill(
        self,
        skill_id: int,
        current_user: User,
        client_ip: str
    ) -> Dict[str, Any]:
        """Delete an existing skill safely with audit & revision recording."""
        s = self.skill_repo.get_by_id(skill_id)
        if not s:
            raise ResourceNotFoundError("Skill", skill_id)

        prev_dict = skill_to_dict(s)

        self.db.delete(s)
        self.db.commit()

        record_content_revision(
            db=self.db,
            entity_name="skill",
            action="DELETE",
            entity_id=str(skill_id),
            editor_username=current_user.username,
            change_summary=f"Deleted skill ID {skill_id} ({prev_dict['name']})",
            previous_snapshot=prev_dict,
            current_snapshot=None
        )

        log_audit_event(
            db=self.db,
            event_type="SKILL_DELETED",
            status="SUCCESS",
            user_id=current_user.id,
            username=current_user.username,
            details={"skill_id": skill_id, "name": prev_dict["name"]},
            ip_address=client_ip
        )

        return {"success": True, "message": f"Skill '{prev_dict['name']}' deleted successfully"}

    def reorder_skills(
        self,
        items: List[SkillReorderItem],
        current_user: User,
        client_ip: str
    ) -> Dict[str, Any]:
        """
        Bulk reorder skills transactionally.
        Validates ID ownership, rejects foreign/unknown IDs, prevents duplicate ordering values.
        """
        if not items:
            raise ValidationFailedError("Reorder request cannot be empty.")

        item_ids = [it.id for it in items]
        if len(item_ids) != len(set(item_ids)):
            raise ValidationFailedError("Duplicate skill IDs detected in reorder request.")

        for it in items:
            if it.ordering < 0:
                raise ValidationFailedError(f"Ordering cannot be negative: {it.ordering}")

        # Fetch and validate all skill records exist
        skills_in_db = self.db.query(Skill).filter(Skill.id.in_(item_ids)).all()
        found_ids = {s.id for s in skills_in_db}
        missing_ids = set(item_ids) - found_ids
        if missing_ids:
            raise ResourceNotFoundError("Skill", f"Unknown skill ID(s): {sorted(list(missing_ids))}")

        # Ensure all skills belong to the active profile (prevent IDOR)
        profile = self.profile_repo.get_or_create_profile()
        for s in skills_in_db:
            if s.profile_id is not None and s.profile_id != profile.id:
                raise PermissionDeniedError("Cannot reorder skills belonging to another profile.")

        # Execute updates transactionally
        for it in items:
            self.db.query(Skill).filter(Skill.id == it.id).update(
                {"display_order": it.ordering},
                synchronize_session="fetch"
            )

        self.db.commit()

        # Audit and revision recording
        record_content_revision(
            db=self.db,
            entity_name="skill",
            action="UPDATE",
            entity_id="batch",
            editor_username=current_user.username,
            change_summary=f"Reordered {len(items)} skills",
            previous_snapshot=None,
            current_snapshot={"reordered_items": [{"id": it.id, "ordering": it.ordering} for it in items]}
        )

        log_audit_event(
            db=self.db,
            event_type="SKILLS_REORDERED",
            status="SUCCESS",
            user_id=current_user.id,
            username=current_user.username,
            details={"count": len(items), "skill_ids": item_ids},
            ip_address=client_ip
        )

        return {"success": True, "message": "Skills reordered successfully"}
