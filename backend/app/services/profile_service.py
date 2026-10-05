import json
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from app.models.profile import Profile, ProfileEmail
from app.models.education import Education, VALID_EDUCATION_LEVELS
from app.models.experience import Experience, VALID_WORK_MODES
from app.models.hobby import Hobby
from app.models.interest import Interest
from app.models.skill import Skill
from app.repositories.profile_repository import ProfileRepository
from app.repositories.education_repository import EducationRepository
from app.repositories.experience_repository import ExperienceRepository
from app.repositories.hobby_repository import HobbyRepository
from app.repositories.interest_repository import InterestRepository
from app.repositories.skill_repository import SkillRepository
from app.schemas.profile import (
    ProfileUpdate,
    ProfileEmailCreate,
    ProfileEmailUpdate,
    ProfileEmailOut
)
from app.schemas.education import EducationCreate, EducationUpdate, EducationPatch
from app.schemas.experience import ExperienceCreate, ExperienceUpdate, ExperiencePatch
from app.schemas.hobby import HobbyCreate, HobbyUpdate, HobbyPatch
from app.schemas.interest import InterestCreate, InterestUpdate, InterestPatch
from app.core.exceptions import (
    ResourceNotFoundError,
    ValidationFailedError,
    BusinessRuleError,
    ConflictError
)
from app.services.audit_service import log_audit_event, record_content_revision
from app.utils.date_helpers import validate_date_order, parse_month_year


def reset_all_assessments(
    db: Session,
    reason: str = "Admin profile identifier updated",
    current_user: Any = None,
    client_ip: str = "unknown"
) -> None:
    """
    Purges all assessment results, normalized scores/records, responses, and sessions,
    and resets the personality synthesis layer to uncompleted state.
    This ensures that when an admin changes their email, mobile number, or LinkedIn,
    they must take all assessment tests again.
    """
    from app.models.assessment import (
        AssessmentResult,
        AssessmentSession,
        AssessmentResponse,
        PersonalitySynthesis,
        PersonalityTraitScore,
        SoftSkillRecord,
        StrengthRecord,
        WeaknessRecord
    )

    # 1. Delete normalized records
    db.query(PersonalityTraitScore).delete()
    db.query(SoftSkillRecord).filter(SoftSkillRecord.source.in_(["MBTI", "DISC", "BIG_FIVE", "ASSESSMENT"])).delete(synchronize_session=False)
    db.query(StrengthRecord).filter(StrengthRecord.source.in_(["MBTI", "DISC", "BIG_FIVE", "ASSESSMENT"])).delete(synchronize_session=False)
    db.query(WeaknessRecord).filter(WeaknessRecord.source.in_(["MBTI", "DISC", "BIG_FIVE", "ASSESSMENT"])).delete(synchronize_session=False)

    # 2. Delete all assessment results
    db.query(AssessmentResult).delete()

    # 3. Delete all assessment responses and sessions
    db.query(AssessmentResponse).delete()
    db.query(AssessmentSession).delete()

    # 4. Reset PersonalitySynthesis
    synthesis = db.query(PersonalitySynthesis).first()
    if synthesis:
        synthesis.key_soft_skills = "[]"
        synthesis.key_strengths = "[]"
        synthesis.key_weaknesses = "[]"
        synthesis.summary_notes = "Personality assessment not completed."
        synthesis.updated_at = datetime.now(timezone.utc)
    else:
        synthesis = PersonalitySynthesis(
            key_soft_skills="[]",
            key_strengths="[]",
            key_weaknesses="[]",
            summary_notes="Personality assessment not completed."
        )
        db.add(synthesis)

    db.commit()

    # 5. Log audit event
    user_id = getattr(current_user, "id", None) if current_user else None
    username = getattr(current_user, "username", "admin") if current_user else "admin"
    log_audit_event(
        db=db,
        event_type="ASSESSMENTS_RESET_ON_PROFILE_CHANGE",
        status="SUCCESS",
        user_id=user_id,
        username=username,
        details={"reason": reason},
        ip_address=client_ip
    )


class ProfileService:
    """
    Authoritative domain service for the Existence Profile Engine.
    Encapsulates personal identity, multi-email coordinates, education,
    work trajectory, hobbies, interests, and profile completeness calculation.
    """
    def __init__(self, db: Session):
        self.db = db
        self.profile_repo = ProfileRepository(db)
        self.edu_repo = EducationRepository(db)
        self.exp_repo = ExperienceRepository(db)
        self.hobby_repo = HobbyRepository(db)
        self.interest_repo = InterestRepository(db)
        self.skill_repo = SkillRepository(db)

    # -------------------------------------------------------------------------
    # Profile & Identity
    # -------------------------------------------------------------------------

    def get_or_create_profile(self) -> Profile:
        return self.profile_repo.get_or_create_profile()

    def profile_to_dict(self, profile: Profile, public: bool = False) -> Dict[str, Any]:
        """
        Converts Profile model to dictionary.
        Strictly enforces public/private data separation:
        When public=True, only public emails are exposed and private metadata is excluded.
        """
        emails = []
        try:
            emails = json.loads(profile.email_ids) if profile.email_ids else []
        except Exception:
            emails = []

        raw_email_records = profile.emails or []
        if public:
            # Expose only emails explicitly marked public (or primary)
            filtered_emails = [e for e in raw_email_records if getattr(e, "is_public", True)]
        else:
            filtered_emails = raw_email_records

        email_objs = [
            ProfileEmailOut(
                id=e.id,
                profile_id=e.profile_id,
                email=e.email,
                label=e.label,
                is_primary=e.is_primary,
                is_public=getattr(e, "is_public", True),
                display_order=e.display_order,
                created_at=e.created_at,
                updated_at=e.updated_at
            )
            for e in sorted(filtered_emails, key=lambda x: x.display_order)
        ]

        # Public email string list
        public_email_strings = [e.email for e in email_objs]

        is_empty = not any([
            profile.name,
            emails,
            profile.mobile_number,
            profile.linkedin,
            profile.about
        ])

        return {
            "id": profile.id,
            "name": profile.name,
            "email_ids": public_email_strings if public else emails,
            "emails": email_objs if email_objs else None,
            "mobile_number": profile.mobile_number,
            "linkedin": profile.linkedin,
            "about": profile.about,
            "is_empty": is_empty,
            "created_at": profile.created_at,
            "updated_at": profile.updated_at
        }

    def get_profile(self, public: bool = False) -> Dict[str, Any]:
        profile = self.get_or_create_profile()
        return self.profile_to_dict(profile, public=public)

    def calculate_completeness(self) -> Dict[str, Any]:
        """
        Calculates authoritative profile completeness across 9 distinct domain dimensions:
        1. personal_info: Name configured
        2. about: Executive bio narrative configured
        3. emails: At least one verified email registered
        4. contact: Mobile number or LinkedIn provided
        5. education: At least one academic record added
        6. experience: At least one work experience record added
        7. skills: At least one skill evaluated on 7-level scale
        8. hobbies: At least one hobby recorded
        9. interests: At least one intellectual interest recorded
        """
        profile = self.profile_repo.get_profile_with_relations()
        has_personal = bool(profile.name and profile.name.strip())
        has_about = bool(profile.about and profile.about.strip())
        has_emails = bool(profile.emails and len(profile.emails) > 0)
        has_education = bool(profile.educations and len(profile.educations) > 0)
        has_experience = bool(profile.work_experiences and len(profile.work_experiences) > 0)
        has_skills = bool(profile.skills and len(profile.skills) > 0)
        from app.models.hobby_interest import HobbyInterest
        hi_hobby_count = self.db.query(HobbyInterest).filter(HobbyInterest.type == "hobby").count()
        hi_interest_count = self.db.query(HobbyInterest).filter(HobbyInterest.type == "interest").count()
        has_hobbies = bool((profile.hobbies and len(profile.hobbies) > 0) or hi_hobby_count > 0)
        has_interests = bool((profile.interests and len(profile.interests) > 0) or hi_interest_count > 0)

        # Check personality assessment completion
        from app.models.assessment import AssessmentResult
        try:
            has_personality = self.db.query(AssessmentResult).count() > 0
        except Exception:
            has_personality = False

        canonical_dims = {
            "personal_info": has_personal,
            "email": has_emails,
            "about": has_about,
            "education": has_education,
            "experience": has_experience,
            "skills": has_skills,
            "hobbies": has_hobbies,
            "interests": has_interests,
            "personality": has_personality
        }

        completed_dims = [dim for dim, completed in canonical_dims.items() if completed]
        missing_dims = [dim for dim, completed in canonical_dims.items() if not completed]
        completed_count = len(completed_dims)
        total_dimensions = 9
        percentage = round((completed_count / total_dimensions) * 100.0, 1)

        dimension_status = {
            **canonical_dims,
            "name": has_personal,
            "emails": has_emails,
            "contact": bool((profile.mobile_number and profile.mobile_number.strip()) or (profile.linkedin and profile.linkedin.strip()))
        }

        return {
            "percentage": percentage,
            "score_percentage": percentage,
            "completed_count": completed_count,
            "dimensions_completed": completed_count,
            "total_dimensions": total_dimensions,
            "dimensions_total": total_dimensions,
            "dimension_status": dimension_status,
            "breakdown": dimension_status,
            "completed_dimensions": completed_dims,
            "missing_dimensions": missing_dims
        }

    def get_consolidated_public_profile(self) -> Dict[str, Any]:
        """
        Consolidated public portfolio query.
        Uses single eager-loaded SQL query to fetch Profile, Emails, Education,
        Experience, Skills, Hobbies, and Interests, strictly eliminating N+1 database queries.
        """
        profile = self.profile_repo.get_profile_with_relations()
        completeness = self.calculate_completeness()

        public_emails_records = [
            e for e in (profile.emails or [])
            if getattr(e, "is_public", True)
        ]
        primary_email_obj = next((e for e in public_emails_records if e.is_primary), None)
        if not primary_email_obj and public_emails_records:
            primary_email_obj = public_emails_records[0]

        # Active & visible education records sorted according to academic level hierarchy:
        # Doctorate -> Post Graduate -> Graduate -> Diploma -> High School -> Matriculation
        level_order_map = {
            "Doctorate": 1,
            "Post Graduate": 2,
            "Graduate": 3,
            "Diploma": 4,
            "Undergraduate": 4,
            "High School": 5,
            "Matriculation": 6
        }
        edu_list = sorted(
            [e for e in (profile.educations or [])],
            key=lambda x: (
                level_order_map.get(x.level, 99),
                x.ordering,
                not x.currently_studying,
                -(x.start_year or 0),
                -(x.start_month or 0)
            )
        )

        # Active & visible experience records sorted chronologically
        exp_list = sorted(
            [e for e in (profile.work_experiences or [])],
            key=lambda x: (x.ordering, not x.currently_working, -(x.start_year or 0), -(x.start_month or 0))
        )

        # Visible skills sorted by Mastery Rating descending (Level 7 down to Level 1), then ordering, then name
        skills_list = sorted(
            [s for s in (profile.skills or []) if getattr(s, "visibility", True)],
            key=lambda x: (-x.rating, x.ordering, (x.name or "").lower())
        )

        # Visible projects
        from app.services.project_service import project_to_dict
        from app.repositories.project_repository import ProjectRepository
        proj_repo = ProjectRepository(self.db)
        raw_projects = proj_repo.list_projects(profile_id=profile.id, include_hidden=False)
        projects_list = [project_to_dict(p, public=True) for p in raw_projects]

        # Visible hobbies (merges dedicated hobbies table and hobbies_interests table)
        hobbies_list = sorted(
            [h for h in (profile.hobbies or []) if getattr(h, "visibility", True)],
            key=lambda x: (x.ordering, x.name.lower())
        )
        from app.models.hobby_interest import HobbyInterest
        hi_hobbies = (
            self.db.query(HobbyInterest)
            .filter(HobbyInterest.type == "hobby")
            .order_by(HobbyInterest.ordering.asc(), HobbyInterest.name.asc())
            .all()
        )
        existing_hobby_names = {h.name.lower() for h in hobbies_list}
        for hi in hi_hobbies:
            if hi.name.lower() not in existing_hobby_names:
                hobbies_list.append(
                    Hobby(
                        id=hi.id,
                        profile_id=profile.id,
                        name=hi.name,
                        category=hi.category,
                        icon=hi.icon,
                        is_visible=True,
                        display_order=hi.ordering,
                        created_at=hi.created_at,
                        updated_at=hi.updated_at
                    )
                )
                existing_hobby_names.add(hi.name.lower())
        hobbies_list = sorted(hobbies_list, key=lambda x: (x.ordering, x.name.lower()))

        # Visible interests (merges dedicated interests table and hobbies_interests table)
        interests_list = sorted(
            [i for i in (profile.interests or []) if getattr(i, "visibility", True)],
            key=lambda x: (x.ordering, x.name.lower())
        )
        hi_interests = (
            self.db.query(HobbyInterest)
            .filter(HobbyInterest.type == "interest")
            .order_by(HobbyInterest.ordering.asc(), HobbyInterest.name.asc())
            .all()
        )
        existing_interest_names = {i.name.lower() for i in interests_list}
        for hi in hi_interests:
            if hi.name.lower() not in existing_interest_names:
                interests_list.append(
                    Interest(
                        id=hi.id,
                        profile_id=profile.id,
                        name=hi.name,
                        category=hi.category,
                        icon=hi.icon,
                        is_visible=True,
                        display_order=hi.ordering,
                        created_at=hi.created_at,
                        updated_at=hi.updated_at
                    )
                )
                existing_interest_names.add(hi.name.lower())
        interests_list = sorted(interests_list, key=lambda x: (x.ordering, x.name.lower()))

        is_empty = not any([
            profile.name,
            public_emails_records,
            profile.mobile_number,
            profile.linkedin,
            profile.about,
            edu_list,
            exp_list,
            skills_list
        ])

        # Public personality summary if any public results exist
        public_personality = None
        try:
            from app.models.assessment import AssessmentResult, PersonalitySynthesis
            from app.api.v1.endpoints.assessments import result_to_dict
            public_results = (
                self.db.query(AssessmentResult)
                .filter(AssessmentResult.is_public == True)
                .order_by(AssessmentResult.completed_at.desc())
                .all()
            )
            if public_results:
                latest_mbti = next((r for r in public_results if r.assessment_type == "MBTI"), None)
                latest_disc = next((r for r in public_results if r.assessment_type == "DISC"), None)
                latest_b5 = next((r for r in public_results if r.assessment_type == "BIG_FIVE"), None)

                synthesis = self.db.query(PersonalitySynthesis).first()
                soft_skills = json.loads(synthesis.key_soft_skills) if synthesis and synthesis.key_soft_skills else []
                strengths = json.loads(synthesis.key_strengths) if synthesis and synthesis.key_strengths else []
                weaknesses = json.loads(synthesis.key_weaknesses) if synthesis and synthesis.key_weaknesses else []

                completed_types = []
                if latest_mbti: completed_types.append("MBTI")
                if latest_disc: completed_types.append("DISC")
                if latest_b5: completed_types.append("BIG_FIVE")

                public_personality = {
                    "has_assessments": len(completed_types) > 0,
                    "assessments_completed": completed_types,
                    "key_soft_skills": soft_skills,
                    "key_strengths": strengths,
                    "key_weaknesses": weaknesses,
                    "summary_notes": synthesis.summary_notes if synthesis else None,
                    "latest_results": {
                        "MBTI": result_to_dict(latest_mbti) if latest_mbti else None,
                        "DISC": result_to_dict(latest_disc) if latest_disc else None,
                        "BIG_FIVE": result_to_dict(latest_b5) if latest_b5 else None,
                    }
                }
        except Exception:
            public_personality = None

        profile_dict = self.profile_to_dict(profile, public=True)

        return {
            "id": profile.id,
            "name": profile.name,
            "about": profile.about,
            "linkedin": profile.linkedin,
            "mobile_number": profile.mobile_number,
            "primary_email": primary_email_obj.email if primary_email_obj else None,
            "public_emails": [e.email for e in public_emails_records],
            "emails": public_emails_records,
            "education": edu_list,
            "experience": exp_list,
            "skills": skills_list,
            "projects": projects_list,
            "hobbies": hobbies_list,
            "interests": interests_list,
            "completeness": completeness,
            "is_empty": is_empty,
            "created_at": profile.created_at,
            "updated_at": profile.updated_at,
            "profile": profile_dict,
            "personality": public_personality
        }

    def update_profile(
        self,
        profile_data: ProfileUpdate,
        current_user: Any,
        client_ip: str
    ) -> Dict[str, Any]:
        """
        Updates core personal identity fields inside a transaction.
        Creates an immutable content revision and audit log.
        If email id, mobile number, or linkedin account is changed by admin,
        all assessment tests are reset so the admin must give all assessments again.
        """
        profile = self.get_or_create_profile()
        prev_snapshot = self.profile_to_dict(profile)

        prev_mobile = (profile.mobile_number or "").strip()
        new_mobile = (profile_data.mobile_number or "").strip() if profile_data.mobile_number is not None else prev_mobile

        prev_linkedin = (profile.linkedin or "").strip()
        new_linkedin = (profile_data.linkedin or "").strip() if profile_data.linkedin is not None else prev_linkedin

        try:
            prev_emails = json.loads(profile.email_ids) if profile.email_ids else []
        except Exception:
            prev_emails = []
        new_emails = profile_data.email_ids if profile_data.email_ids is not None else prev_emails

        mobile_changed = (prev_mobile != new_mobile)
        linkedin_changed = (prev_linkedin != new_linkedin)
        email_changed = (profile_data.email_ids is not None and sorted(prev_emails) != sorted(new_emails))
        identity_changed = mobile_changed or linkedin_changed or email_changed

        profile.name = profile_data.name.strip() if profile_data.name else None
        if profile_data.email_ids is not None:
            profile.email_ids = json.dumps(profile_data.email_ids)
        profile.mobile_number = profile_data.mobile_number.strip() if profile_data.mobile_number else None
        profile.linkedin = profile_data.linkedin.strip() if profile_data.linkedin else None
        profile.about = profile_data.about.strip() if profile_data.about else None
        profile.updated_at = datetime.now(timezone.utc)

        self.db.commit()
        self.db.refresh(profile)

        if identity_changed:
            reset_all_assessments(
                db=self.db,
                reason=f"Admin profile contact updated (email={email_changed}, mobile={mobile_changed}, linkedin={linkedin_changed})",
                current_user=current_user,
                client_ip=client_ip
            )

        curr_snapshot = self.profile_to_dict(profile)
        curr_snapshot["assessments_reset"] = identity_changed

        record_content_revision(
            db=self.db,
            entity_name="profile",
            action="UPDATE",
            entity_id=str(profile.id),
            editor_username=current_user.username,
            change_summary="Profile personal information updated via Profile Engine" + (" (assessments reset)" if identity_changed else ""),
            previous_snapshot=prev_snapshot,
            current_snapshot=curr_snapshot
        )

        log_audit_event(
            db=self.db,
            event_type="PROFILE_UPDATED",
            status="SUCCESS",
            user_id=current_user.id,
            username=current_user.username,
            details={"profile_id": profile.id, "assessments_reset": identity_changed},
            ip_address=client_ip
        )

        return curr_snapshot

    def patch_profile(
        self,
        profile_data: ProfileUpdate,
        current_user: Any,
        client_ip: str
    ) -> Dict[str, Any]:
        profile = self.get_or_create_profile()
        prev_snapshot = self.profile_to_dict(profile)

        prev_mobile = (profile.mobile_number or "").strip()
        new_mobile = (profile_data.mobile_number or "").strip() if profile_data.mobile_number is not None else prev_mobile

        prev_linkedin = (profile.linkedin or "").strip()
        new_linkedin = (profile_data.linkedin or "").strip() if profile_data.linkedin is not None else prev_linkedin

        try:
            prev_emails = json.loads(profile.email_ids) if profile.email_ids else []
        except Exception:
            prev_emails = []
        new_emails = profile_data.email_ids if profile_data.email_ids is not None else prev_emails

        mobile_changed = (profile_data.mobile_number is not None and prev_mobile != new_mobile)
        linkedin_changed = (profile_data.linkedin is not None and prev_linkedin != new_linkedin)
        email_changed = (profile_data.email_ids is not None and sorted(prev_emails) != sorted(new_emails))
        identity_changed = mobile_changed or linkedin_changed or email_changed

        if profile_data.name is not None:
            profile.name = profile_data.name.strip() if profile_data.name else None
        if profile_data.email_ids is not None:
            profile.email_ids = json.dumps(profile_data.email_ids)
        if profile_data.mobile_number is not None:
            profile.mobile_number = profile_data.mobile_number.strip() if profile_data.mobile_number else None
        if profile_data.linkedin is not None:
            profile.linkedin = profile_data.linkedin.strip() if profile_data.linkedin else None
        if profile_data.about is not None:
            profile.about = profile_data.about.strip() if profile_data.about else None

        profile.updated_at = datetime.now(timezone.utc)
        self.db.commit()
        self.db.refresh(profile)

        if identity_changed:
            reset_all_assessments(
                db=self.db,
                reason=f"Admin profile contact patched (email={email_changed}, mobile={mobile_changed}, linkedin={linkedin_changed})",
                current_user=current_user,
                client_ip=client_ip
            )

        curr_snapshot = self.profile_to_dict(profile)
        curr_snapshot["assessments_reset"] = identity_changed

        record_content_revision(
            db=self.db,
            entity_name="profile",
            action="PATCH",
            entity_id=str(profile.id),
            editor_username=current_user.username,
            change_summary="Profile personal information patched via Profile Engine" + (" (assessments reset)" if identity_changed else ""),
            previous_snapshot=prev_snapshot,
            current_snapshot=curr_snapshot
        )

        log_audit_event(
            db=self.db,
            event_type="PROFILE_PATCHED",
            status="SUCCESS",
            user_id=current_user.id,
            username=current_user.username,
            details={"profile_id": profile.id, "assessments_reset": identity_changed},
            ip_address=client_ip
        )

        return curr_snapshot

    # -------------------------------------------------------------------------
    # Email Engine
    # -------------------------------------------------------------------------

    def list_emails(self, public_only: bool = False) -> List[ProfileEmail]:
        profile = self.get_or_create_profile()
        emails = self.profile_repo.get_emails(profile.id)
        if public_only:
            return [e for e in emails if getattr(e, "is_public", True)]
        return emails

    def add_email(
        self,
        email_data: ProfileEmailCreate,
        current_user: Any,
        client_ip: str
    ) -> ProfileEmail:
        profile = self.get_or_create_profile()
        normalized_email = email_data.email.strip().lower()

        existing = self.profile_repo.get_email_by_address(normalized_email, profile.id)
        if existing:
            raise ConflictError("Email already registered in profile.")

        # If this is the very first email, force it to be primary
        total_emails = self.profile_repo.count_emails(profile.id)
        is_primary = email_data.is_primary or (total_emails == 0)

        new_email = self.profile_repo.add_email(
            profile_id=profile.id,
            email=normalized_email,
            label=email_data.label,
            is_primary=is_primary,
            display_order=email_data.display_order,
            is_public=email_data.is_public
        )

        self.profile_repo.sync_email_ids(profile)

        record_content_revision(
            db=self.db,
            entity_name="profile_email",
            action="CREATE",
            entity_id=str(new_email.id),
            editor_username=current_user.username,
            change_summary=f"Added profile email '{new_email.email}'",
            previous_snapshot=None,
            current_snapshot={
                "id": new_email.id,
                "email": new_email.email,
                "label": new_email.label,
                "is_primary": new_email.is_primary,
                "is_public": new_email.is_public
            }
        )

        log_audit_event(
            db=self.db,
            event_type="EMAIL_ADDED",
            status="SUCCESS",
            user_id=current_user.id,
            username=current_user.username,
            details={"email_id": new_email.id, "email": new_email.email},
            ip_address=client_ip
        )

        reset_all_assessments(
            db=self.db,
            reason=f"New profile email '{new_email.email}' added for admin",
            current_user=current_user,
            client_ip=client_ip
        )
        setattr(new_email, "assessments_reset", True)

        return new_email

    def update_email(
        self,
        email_id: int,
        email_data: ProfileEmailUpdate,
        current_user: Any,
        client_ip: str
    ) -> ProfileEmail:
        profile = self.get_or_create_profile()
        email_rec = self.profile_repo.get_email_by_id(email_id, profile.id)
        if not email_rec:
            raise ResourceNotFoundError("Profile email", email_id)

        prev_snapshot = {
            "id": email_rec.id,
            "email": email_rec.email,
            "label": email_rec.label,
            "is_primary": email_rec.is_primary,
            "is_public": email_rec.is_public
        }

        email_changed = False
        if email_data.email is not None:
            clean_email = email_data.email.strip().lower()
            if clean_email != email_rec.email.lower():
                dup = self.profile_repo.get_email_by_address(clean_email, profile.id)
                if dup and dup.id != email_id:
                    raise ConflictError("Email already registered in profile.")
                email_rec.email = clean_email
                email_changed = True

        if email_data.label is not None:
            email_rec.label = email_data.label.strip()
        if email_data.display_order is not None:
            email_rec.display_order = email_data.display_order
        if email_data.is_public is not None:
            email_rec.is_public = email_data.is_public

        if email_data.is_primary is True:
            self.profile_repo.set_primary_email(profile.id, email_id)
        elif email_data.is_primary is False and email_rec.is_primary:
            # Cannot simply un-primary the only primary without nominating another
            other_emails = [e for e in self.profile_repo.get_emails(profile.id) if e.id != email_id]
            if not other_emails:
                raise BusinessRuleError("A profile must have at least one primary email address.")
            # Auto-promote first alternate email
            other_emails[0].is_primary = True
            email_rec.is_primary = False

        email_rec.updated_at = datetime.now(timezone.utc)
        self.db.commit()
        self.db.refresh(email_rec)

        self.profile_repo.sync_email_ids(profile)

        if email_changed:
            reset_all_assessments(
                db=self.db,
                reason=f"Profile email updated to '{email_rec.email}' for admin",
                current_user=current_user,
                client_ip=client_ip
            )
            setattr(email_rec, "assessments_reset", True)

        curr_snapshot = {
            "id": email_rec.id,
            "email": email_rec.email,
            "label": email_rec.label,
            "is_primary": email_rec.is_primary,
            "is_public": email_rec.is_public
        }

        record_content_revision(
            db=self.db,
            entity_name="profile_email",
            action="UPDATE",
            entity_id=str(email_rec.id),
            editor_username=current_user.username,
            change_summary=f"Updated profile email '{email_rec.email}'",
            previous_snapshot=prev_snapshot,
            current_snapshot=curr_snapshot
        )

        log_audit_event(
            db=self.db,
            event_type="EMAIL_UPDATED",
            status="SUCCESS",
            user_id=current_user.id,
            username=current_user.username,
            details={"email_id": email_rec.id, "email": email_rec.email},
            ip_address=client_ip
        )

        return email_rec

    def delete_email(
        self,
        email_id: int,
        current_user: Any,
        client_ip: str
    ) -> Dict[str, Any]:
        profile = self.get_or_create_profile()
        email_rec = self.profile_repo.get_email_by_id(email_id, profile.id)
        if not email_rec:
            raise ResourceNotFoundError("Profile email", email_id)

        # Business Rule (Section 13): If this is the only registered email, prevent deletion
        total_emails = self.profile_repo.count_emails(profile.id)
        if total_emails <= 1:
            raise BusinessRuleError("Cannot delete the only email address registered in the profile.")

        deleted_addr = email_rec.email
        was_primary = email_rec.is_primary

        prev_snapshot = {
            "id": email_rec.id,
            "email": email_rec.email,
            "label": email_rec.label,
            "is_primary": email_rec.is_primary
        }

        self.db.delete(email_rec)
        self.db.commit()

        # If deleted email was primary, promote the next available email in display order
        if was_primary:
            remaining = self.profile_repo.get_emails(profile.id)
            if remaining:
                remaining[0].is_primary = True
                self.db.commit()

        self.profile_repo.sync_email_ids(profile)

        reset_all_assessments(
            db=self.db,
            reason=f"Profile email '{deleted_addr}' deleted for admin",
            current_user=current_user,
            client_ip=client_ip
        )

        record_content_revision(
            db=self.db,
            entity_name="profile_email",
            action="DELETE",
            entity_id=str(email_id),
            editor_username=current_user.username,
            change_summary=f"Deleted profile email '{deleted_addr}'",
            previous_snapshot=prev_snapshot,
            current_snapshot=None
        )

        log_audit_event(
            db=self.db,
            event_type="EMAIL_DELETED",
            status="SUCCESS",
            user_id=current_user.id,
            username=current_user.username,
            details={"email_id": email_id, "email": deleted_addr},
            ip_address=client_ip
        )

        return {"success": True, "message": f"Email {deleted_addr} deleted successfully.", "assessments_reset": True}

    def set_primary_email(
        self,
        email_id: int,
        current_user: Any,
        client_ip: str
    ) -> ProfileEmail:
        profile = self.get_or_create_profile()
        email_rec = self.profile_repo.get_email_by_id(email_id, profile.id)
        if not email_rec:
            raise ResourceNotFoundError("Profile email", email_id)

        prev_primary = next((e for e in self.profile_repo.get_emails(profile.id) if e.is_primary), None)
        target = self.profile_repo.set_primary_email(profile.id, email_id)
        self.profile_repo.sync_email_ids(profile)

        if prev_primary and prev_primary.id != email_id:
            reset_all_assessments(
                db=self.db,
                reason=f"Primary profile email changed to '{target.email}' for admin",
                current_user=current_user,
                client_ip=client_ip
            )
            setattr(target, "assessments_reset", True)

        record_content_revision(
            db=self.db,
            entity_name="profile_email",
            action="PRIMARY_CHANGED",
            entity_id=str(email_id),
            editor_username=current_user.username,
            change_summary=f"Set '{target.email}' as primary profile email",
            previous_snapshot={"primary_email": prev_primary.email if prev_primary else None},
            current_snapshot={"primary_email": target.email}
        )

        log_audit_event(
            db=self.db,
            event_type="EMAIL_PRIMARY_CHANGED",
            status="SUCCESS",
            user_id=current_user.id,
            username=current_user.username,
            details={"email_id": email_id, "email": target.email},
            ip_address=client_ip
        )

        return target

    # -------------------------------------------------------------------------
    # Education Engine
    # -------------------------------------------------------------------------

    def list_education(self) -> List[Education]:
        return self.edu_repo.list_ordered()

    def get_education(self, edu_id: int) -> Education:
        item = self.edu_repo.get_by_id(edu_id)
        if not item:
            raise ResourceNotFoundError("Education record", edu_id)
        return item

    def create_education(
        self,
        edu_data: EducationCreate,
        current_user: Any,
        client_ip: str
    ) -> Education:
        profile = self.get_or_create_profile()

        stream_val = edu_data.stream.strip() if edu_data.stream else None
        if edu_data.level in ("High School", "Matriculation"):
            stream_val = None

        # Check for duplicate
        dup = self.edu_repo.find_duplicate(
            level=edu_data.level,
            stream=stream_val,
            starting_month_year=edu_data.starting_month_year,
            institution=edu_data.institution
        )
        if dup:
            label = stream_val or edu_data.level
            raise ConflictError(f"Education entry for {label} ({edu_data.level}) already exists.")

        new_edu = Education(
            profile_id=profile.id,
            level=edu_data.level,
            stream=stream_val,
            institution=edu_data.institution.strip() if edu_data.institution else None,
            starting_month_year=edu_data.starting_month_year.strip(),
            ending_month_year=edu_data.ending_month_year.strip() if edu_data.ending_month_year else None,
            currently_studying=edu_data.currently_studying,
            score_type=edu_data.score_type,
            score_value=edu_data.score_value,
            display_order=edu_data.ordering if edu_data.ordering else (edu_data.display_order or 0),
            start_month=edu_data.start_month,
            start_year=edu_data.start_year,
            end_month=edu_data.end_month,
            end_year=edu_data.end_year
        )

        self.db.add(new_edu)
        self.db.commit()
        self.db.refresh(new_edu)

        record_content_revision(
            db=self.db,
            entity_name="education",
            action="CREATE",
            entity_id=str(new_edu.id),
            editor_username=current_user.username,
            change_summary=f"Created education record '{new_edu.stream or new_edu.level}' ({new_edu.level})",
            previous_snapshot=None,
            current_snapshot={
                "id": new_edu.id,
                "level": new_edu.level,
                "stream": new_edu.stream,
                "institution": new_edu.institution,
                "starting_month_year": new_edu.starting_month_year,
                "ending_month_year": new_edu.ending_month_year,
                "currently_studying": new_edu.currently_studying,
                "score_type": new_edu.score_type,
                "score_value": new_edu.score_value
            }
        )

        log_audit_event(
            db=self.db,
            event_type="EDUCATION_CREATED",
            status="SUCCESS",
            user_id=current_user.id,
            username=current_user.username,
            details={"education_id": new_edu.id, "stream": new_edu.stream or "", "level": new_edu.level},
            ip_address=client_ip
        )

        return new_edu

    def update_education(
        self,
        edu_id: int,
        edu_data: EducationUpdate,
        current_user: Any,
        client_ip: str
    ) -> Education:
        edu = self.get_education(edu_id)
        prev_snapshot = {
            "id": edu.id,
            "level": edu.level,
            "stream": edu.stream,
            "institution": edu.institution,
            "starting_month_year": edu.starting_month_year,
            "ending_month_year": edu.ending_month_year,
            "currently_studying": edu.currently_studying,
            "score_type": edu.score_type,
            "score_value": edu.score_value
        }

        edu.level = edu_data.level
        if edu.level in ("High School", "Matriculation"):
            edu.stream = None
        else:
            edu.stream = edu_data.stream.strip() if edu_data.stream else None
        edu.institution = edu_data.institution.strip() if edu_data.institution else None
        edu.starting_month_year = edu_data.starting_month_year.strip()
        edu.ending_month_year = edu_data.ending_month_year.strip() if edu_data.ending_month_year else None
        edu.currently_studying = edu_data.currently_studying
        if edu.currently_studying:
            edu.score_type = None
            edu.score_value = None
        else:
            edu.score_type = edu_data.score_type
            edu.score_value = edu_data.score_value
        edu.display_order = edu_data.ordering if edu_data.ordering else (edu_data.display_order or 0)
        edu.start_month = edu_data.start_month
        edu.start_year = edu_data.start_year
        edu.end_month = edu_data.end_month
        edu.end_year = edu_data.end_year
        edu.updated_at = datetime.now(timezone.utc)

        self.db.commit()
        self.db.refresh(edu)

        curr_snapshot = {
            "id": edu.id,
            "level": edu.level,
            "stream": edu.stream,
            "institution": edu.institution,
            "starting_month_year": edu.starting_month_year,
            "ending_month_year": edu.ending_month_year,
            "currently_studying": edu.currently_studying,
            "score_type": edu.score_type,
            "score_value": edu.score_value
        }

        record_content_revision(
            db=self.db,
            entity_name="education",
            action="UPDATE",
            entity_id=str(edu.id),
            editor_username=current_user.username,
            change_summary=f"Updated education record '{edu.stream or edu.level}' ({edu.level})",
            previous_snapshot=prev_snapshot,
            current_snapshot=curr_snapshot
        )

        log_audit_event(
            db=self.db,
            event_type="EDUCATION_UPDATED",
            status="SUCCESS",
            user_id=current_user.id,
            username=current_user.username,
            details={"education_id": edu.id, "stream": edu.stream or ""},
            ip_address=client_ip
        )

        return edu

    def patch_education(
        self,
        edu_id: int,
        edu_data: EducationPatch,
        current_user: Any,
        client_ip: str
    ) -> Education:
        edu = self.get_education(edu_id)
        prev_snapshot = {
            "id": edu.id,
            "level": edu.level,
            "stream": edu.stream,
            "institution": edu.institution,
            "starting_month_year": edu.starting_month_year,
            "ending_month_year": edu.ending_month_year,
            "currently_studying": edu.currently_studying,
            "score_type": edu.score_type,
            "score_value": edu.score_value
        }

        if edu_data.level is not None:
            edu.level = edu_data.level
            if edu.level in ("High School", "Matriculation"):
                edu.stream = None
        if edu_data.stream is not None and edu.level not in ("High School", "Matriculation"):
            edu.stream = edu_data.stream.strip() if edu_data.stream else None
        if edu_data.institution is not None:
            edu.institution = edu_data.institution.strip() if edu_data.institution else None
        if edu_data.starting_month_year is not None:
            edu.starting_month_year = edu_data.starting_month_year.strip()
            dt = parse_month_year(edu.starting_month_year)
            if dt:
                edu.start_month = dt.month
                edu.start_year = dt.year

        if edu_data.currently_studying is not None:
            edu.currently_studying = edu_data.currently_studying

        if edu.currently_studying:
            edu.ending_month_year = None
            edu.end_month = None
            edu.end_year = None
            edu.score_type = None
            edu.score_value = None
        else:
            if edu_data.ending_month_year is not None:
                edu.ending_month_year = edu_data.ending_month_year.strip() if edu_data.ending_month_year else None
                if edu.ending_month_year:
                    dt = parse_month_year(edu.ending_month_year)
                    if dt:
                        edu.end_month = dt.month
                        edu.end_year = dt.year
            if edu_data.score_type is not None:
                edu.score_type = edu_data.score_type
            if edu_data.score_value is not None:
                edu.score_value = edu_data.score_value

        if edu.ending_month_year:
            validate_date_order(edu.starting_month_year, edu.ending_month_year)

        if edu_data.ordering is not None:
            edu.display_order = edu_data.ordering
        elif edu_data.display_order is not None:
            edu.display_order = edu_data.display_order

        edu.updated_at = datetime.now(timezone.utc)
        self.db.commit()
        self.db.refresh(edu)

        curr_snapshot = {
            "id": edu.id,
            "level": edu.level,
            "stream": edu.stream,
            "institution": edu.institution,
            "starting_month_year": edu.starting_month_year,
            "ending_month_year": edu.ending_month_year,
            "currently_studying": edu.currently_studying,
            "score_type": edu.score_type,
            "score_value": edu.score_value
        }

        record_content_revision(
            db=self.db,
            entity_name="education",
            action="PATCH",
            entity_id=str(edu.id),
            editor_username=current_user.username,
            change_summary=f"Patched education record '{edu.stream or edu.level}'",
            previous_snapshot=prev_snapshot,
            current_snapshot=curr_snapshot
        )

        log_audit_event(
            db=self.db,
            event_type="EDUCATION_PATCHED",
            status="SUCCESS",
            user_id=current_user.id,
            username=current_user.username,
            details={"education_id": edu.id, "stream": edu.stream or ""},
            ip_address=client_ip
        )

        return edu

    def delete_education(
        self,
        edu_id: int,
        current_user: Any,
        client_ip: str
    ) -> Dict[str, Any]:
        edu = self.get_education(edu_id)
        stream_name = edu.stream or edu.level
        prev_snapshot = {
            "id": edu.id,
            "level": edu.level,
            "stream": edu.stream,
            "institution": edu.institution
        }

        self.db.delete(edu)
        self.db.commit()

        record_content_revision(
            db=self.db,
            entity_name="education",
            action="DELETE",
            entity_id=str(edu_id),
            editor_username=current_user.username,
            change_summary=f"Deleted education record '{stream_name}'",
            previous_snapshot=prev_snapshot,
            current_snapshot=None
        )

        log_audit_event(
            db=self.db,
            event_type="EDUCATION_DELETED",
            status="SUCCESS",
            user_id=current_user.id,
            username=current_user.username,
            details={"education_id": edu_id, "stream": stream_name},
            ip_address=client_ip
        )

        return {"success": True, "message": f"Education record '{stream_name}' deleted successfully."}

    # -------------------------------------------------------------------------
    # Work Experience Engine
    # -------------------------------------------------------------------------

    def list_experience(self) -> List[Experience]:
        return self.exp_repo.list_ordered()

    def get_experience(self, exp_id: int) -> Experience:
        item = self.exp_repo.get_by_id(exp_id)
        if not item:
            raise ResourceNotFoundError("Work experience record", exp_id)
        return item

    def create_experience(
        self,
        exp_data: ExperienceCreate,
        current_user: Any,
        client_ip: str
    ) -> Experience:
        profile = self.get_or_create_profile()

        # Check duplicate
        dup = self.exp_repo.find_duplicate(
            role=exp_data.role,
            employer=exp_data.employer,
            starting_month_year=exp_data.starting_month_year
        )
        if dup:
            raise ConflictError(f"Experience entry for '{exp_data.role}' at '{exp_data.employer}' already exists.")

        loc = exp_data.location.strip() if exp_data.location else None
        if exp_data.work_mode == "Remote" and (not loc or loc == ""):
            loc = "Remote"

        new_exp = Experience(
            profile_id=profile.id,
            role=exp_data.role.strip(),
            employer=exp_data.employer.strip(),
            work_mode=exp_data.work_mode,
            location=loc,
            starting_month_year=exp_data.starting_month_year.strip(),
            ending_month_year=exp_data.ending_month_year.strip() if exp_data.ending_month_year else None,
            currently_working=exp_data.currently_working,
            display_order=exp_data.ordering if exp_data.ordering else (exp_data.display_order or 0),
            start_month=exp_data.start_month,
            start_year=exp_data.start_year,
            end_month=exp_data.end_month,
            end_year=exp_data.end_year
        )

        self.db.add(new_exp)
        self.db.commit()
        self.db.refresh(new_exp)

        record_content_revision(
            db=self.db,
            entity_name="experience",
            action="CREATE",
            entity_id=str(new_exp.id),
            editor_username=current_user.username,
            change_summary=f"Created work experience '{new_exp.role}' at '{new_exp.employer}'",
            previous_snapshot=None,
            current_snapshot={
                "id": new_exp.id,
                "role": new_exp.role,
                "employer": new_exp.employer,
                "work_mode": new_exp.work_mode,
                "location": new_exp.location,
                "starting_month_year": new_exp.starting_month_year,
                "ending_month_year": new_exp.ending_month_year,
                "currently_working": new_exp.currently_working
            }
        )

        log_audit_event(
            db=self.db,
            event_type="EXPERIENCE_CREATED",
            status="SUCCESS",
            user_id=current_user.id,
            username=current_user.username,
            details={"experience_id": new_exp.id, "role": new_exp.role, "employer": new_exp.employer},
            ip_address=client_ip
        )

        return new_exp

    def update_experience(
        self,
        exp_id: int,
        exp_data: ExperienceUpdate,
        current_user: Any,
        client_ip: str
    ) -> Experience:
        exp = self.get_experience(exp_id)
        prev_snapshot = {
            "id": exp.id,
            "role": exp.role,
            "employer": exp.employer,
            "work_mode": exp.work_mode,
            "location": exp.location,
            "starting_month_year": exp.starting_month_year,
            "ending_month_year": exp.ending_month_year,
            "currently_working": exp.currently_working
        }

        loc = exp_data.location.strip() if exp_data.location else None
        if exp_data.work_mode == "Remote":
            loc = "Remote"

        exp.role = exp_data.role.strip()
        exp.employer = exp_data.employer.strip()
        exp.work_mode = exp_data.work_mode
        exp.location = loc
        exp.starting_month_year = exp_data.starting_month_year.strip()
        exp.ending_month_year = exp_data.ending_month_year.strip() if exp_data.ending_month_year else None
        exp.currently_working = exp_data.currently_working
        exp.display_order = exp_data.ordering if exp_data.ordering else (exp_data.display_order or 0)
        exp.start_month = exp_data.start_month
        exp.start_year = exp_data.start_year
        exp.end_month = exp_data.end_month
        exp.end_year = exp_data.end_year
        exp.updated_at = datetime.now(timezone.utc)

        self.db.commit()
        self.db.refresh(exp)

        curr_snapshot = {
            "id": exp.id,
            "role": exp.role,
            "employer": exp.employer,
            "work_mode": exp.work_mode,
            "location": exp.location,
            "starting_month_year": exp.starting_month_year,
            "ending_month_year": exp.ending_month_year,
            "currently_working": exp.currently_working
        }

        record_content_revision(
            db=self.db,
            entity_name="experience",
            action="UPDATE",
            entity_id=str(exp.id),
            editor_username=current_user.username,
            change_summary=f"Updated work experience '{exp.role}' at '{exp.employer}'",
            previous_snapshot=prev_snapshot,
            current_snapshot=curr_snapshot
        )

        log_audit_event(
            db=self.db,
            event_type="EXPERIENCE_UPDATED",
            status="SUCCESS",
            user_id=current_user.id,
            username=current_user.username,
            details={"experience_id": exp.id, "role": exp.role},
            ip_address=client_ip
        )

        return exp

    def patch_experience(
        self,
        exp_id: int,
        exp_data: ExperiencePatch,
        current_user: Any,
        client_ip: str
    ) -> Experience:
        exp = self.get_experience(exp_id)
        prev_snapshot = {
            "id": exp.id,
            "role": exp.role,
            "employer": exp.employer,
            "work_mode": exp.work_mode,
            "location": exp.location,
            "starting_month_year": exp.starting_month_year,
            "ending_month_year": exp.ending_month_year,
            "currently_working": exp.currently_working
        }

        if exp_data.role is not None:
            exp.role = exp_data.role.strip()
        if exp_data.employer is not None:
            exp.employer = exp_data.employer.strip()
        if exp_data.work_mode is not None:
            exp.work_mode = exp_data.work_mode

        if exp_data.location is not None:
            exp.location = exp_data.location.strip() if exp_data.location else None

        # Clean stale location if Remote
        if exp.work_mode == "Remote":
            exp.location = "Remote"
        elif exp.work_mode in ["On-site", "Hybrid"] and (not exp.location or not exp.location.strip()):
            raise ValidationFailedError(f"Location is required when work mode is {exp.work_mode}.")

        if exp_data.starting_month_year is not None:
            exp.starting_month_year = exp_data.starting_month_year.strip()
            dt = parse_month_year(exp.starting_month_year)
            if dt:
                exp.start_month = dt.month
                exp.start_year = dt.year

        if exp_data.currently_working is not None:
            exp.currently_working = exp_data.currently_working

        if exp.currently_working:
            exp.ending_month_year = None
            exp.end_month = None
            exp.end_year = None
        elif exp_data.ending_month_year is not None:
            exp.ending_month_year = exp_data.ending_month_year.strip() if exp_data.ending_month_year else None
            if exp.ending_month_year:
                dt = parse_month_year(exp.ending_month_year)
                if dt:
                    exp.end_month = dt.month
                    exp.end_year = dt.year

        if exp.ending_month_year:
            validate_date_order(exp.starting_month_year, exp.ending_month_year)

        if exp_data.ordering is not None:
            exp.display_order = exp_data.ordering
        elif exp_data.display_order is not None:
            exp.display_order = exp_data.display_order

        exp.updated_at = datetime.now(timezone.utc)
        self.db.commit()
        self.db.refresh(exp)

        curr_snapshot = {
            "id": exp.id,
            "role": exp.role,
            "employer": exp.employer,
            "work_mode": exp.work_mode,
            "location": exp.location,
            "starting_month_year": exp.starting_month_year,
            "ending_month_year": exp.ending_month_year,
            "currently_working": exp.currently_working
        }

        record_content_revision(
            db=self.db,
            entity_name="experience",
            action="PATCH",
            entity_id=str(exp.id),
            editor_username=current_user.username,
            change_summary=f"Patched work experience '{exp.role}'",
            previous_snapshot=prev_snapshot,
            current_snapshot=curr_snapshot
        )

        log_audit_event(
            db=self.db,
            event_type="EXPERIENCE_PATCHED",
            status="SUCCESS",
            user_id=current_user.id,
            username=current_user.username,
            details={"experience_id": exp.id, "role": exp.role},
            ip_address=client_ip
        )

        return exp

    def delete_experience(
        self,
        exp_id: int,
        current_user: Any,
        client_ip: str
    ) -> Dict[str, Any]:
        exp = self.get_experience(exp_id)
        role_name = exp.role
        employer_name = exp.employer
        prev_snapshot = {
            "id": exp.id,
            "role": exp.role,
            "employer": exp.employer
        }

        self.db.delete(exp)
        self.db.commit()

        record_content_revision(
            db=self.db,
            entity_name="experience",
            action="DELETE",
            entity_id=str(exp_id),
            editor_username=current_user.username,
            change_summary=f"Deleted work experience '{role_name}' at '{employer_name}'",
            previous_snapshot=prev_snapshot,
            current_snapshot=None
        )

        log_audit_event(
            db=self.db,
            event_type="EXPERIENCE_DELETED",
            status="SUCCESS",
            user_id=current_user.id,
            username=current_user.username,
            details={"experience_id": exp_id, "role": role_name},
            ip_address=client_ip
        )

        return {"success": True, "message": f"Work experience '{role_name}' deleted successfully."}

    # -------------------------------------------------------------------------
    # Hobbies Engine
    # -------------------------------------------------------------------------

    def list_hobbies(self, include_hidden: bool = False) -> List[Hobby]:
        hobbies = self.hobby_repo.list_hobbies(include_hidden=include_hidden)
        if not hobbies:
            from app.models.hobby_interest import HobbyInterest
            hi_hobbies = (
                self.db.query(HobbyInterest)
                .filter(HobbyInterest.type == "hobby")
                .order_by(HobbyInterest.ordering.asc(), HobbyInterest.name.asc())
                .all()
            )
            return [
                Hobby(
                    id=hi.id,
                    name=hi.name,
                    category=hi.category,
                    icon=hi.icon,
                    is_visible=True,
                    display_order=hi.ordering,
                    created_at=hi.created_at,
                    updated_at=hi.updated_at
                )
                for hi in hi_hobbies
            ]
        return hobbies

    def get_hobby(self, hobby_id: int) -> Hobby:
        item = self.hobby_repo.get_by_id(hobby_id)
        if not item:
            raise ResourceNotFoundError("Hobby", hobby_id)
        return item

    def create_hobby(
        self,
        data: HobbyCreate,
        current_user: Any,
        client_ip: str
    ) -> Hobby:
        profile = self.get_or_create_profile()
        trimmed_name = data.name.strip()

        # Duplicate detection (case-insensitive & trimmed)
        dup = self.hobby_repo.find_by_normalized_name(trimmed_name)
        if dup:
            raise ConflictError(f"Hobby '{trimmed_name}' already exists.")

        new_hobby = Hobby(
            profile_id=profile.id,
            name=trimmed_name,
            category=data.category.strip() if data.category else None,
            icon=data.icon.strip() if data.icon else None,
            is_visible=data.visibility if data.is_visible is None else data.is_visible,
            display_order=data.ordering if data.display_order is None else data.display_order
        )

        self.db.add(new_hobby)
        self.db.commit()
        self.db.refresh(new_hobby)

        record_content_revision(
            db=self.db,
            entity_name="hobby",
            action="CREATE",
            entity_id=str(new_hobby.id),
            editor_username=current_user.username,
            change_summary=f"Created hobby '{new_hobby.name}'",
            previous_snapshot=None,
            current_snapshot={"id": new_hobby.id, "name": new_hobby.name, "category": new_hobby.category}
        )

        log_audit_event(
            db=self.db,
            event_type="HOBBY_CREATED",
            status="SUCCESS",
            user_id=current_user.id,
            username=current_user.username,
            details={"hobby_id": new_hobby.id, "name": new_hobby.name},
            ip_address=client_ip
        )

        return new_hobby

    def update_hobby(
        self,
        hobby_id: int,
        data: HobbyUpdate,
        current_user: Any,
        client_ip: str
    ) -> Hobby:
        hobby = self.get_hobby(hobby_id)
        trimmed_name = data.name.strip()

        dup = self.hobby_repo.find_by_normalized_name(trimmed_name, exclude_id=hobby_id)
        if dup:
            raise ConflictError(f"Hobby '{trimmed_name}' already exists.")

        prev_snapshot = {"id": hobby.id, "name": hobby.name, "category": hobby.category}

        hobby.name = trimmed_name
        hobby.category = data.category.strip() if data.category else None
        hobby.icon = data.icon.strip() if data.icon else None
        hobby.is_visible = data.visibility if data.is_visible is None else data.is_visible
        hobby.display_order = data.ordering if data.display_order is None else data.display_order
        hobby.updated_at = datetime.now(timezone.utc)

        self.db.commit()
        self.db.refresh(hobby)

        curr_snapshot = {"id": hobby.id, "name": hobby.name, "category": hobby.category}

        record_content_revision(
            db=self.db,
            entity_name="hobby",
            action="UPDATE",
            entity_id=str(hobby.id),
            editor_username=current_user.username,
            change_summary=f"Updated hobby '{hobby.name}'",
            previous_snapshot=prev_snapshot,
            current_snapshot=curr_snapshot
        )

        log_audit_event(
            db=self.db,
            event_type="HOBBY_UPDATED",
            status="SUCCESS",
            user_id=current_user.id,
            username=current_user.username,
            details={"hobby_id": hobby.id, "name": hobby.name},
            ip_address=client_ip
        )

        return hobby

    def patch_hobby(
        self,
        hobby_id: int,
        data: HobbyPatch,
        current_user: Any,
        client_ip: str
    ) -> Hobby:
        hobby = self.get_hobby(hobby_id)
        prev_snapshot = {"id": hobby.id, "name": hobby.name}

        if data.name is not None:
            trimmed = data.name.strip()
            dup = self.hobby_repo.find_by_normalized_name(trimmed, exclude_id=hobby_id)
            if dup:
                raise ConflictError(f"Hobby '{trimmed}' already exists.")
            hobby.name = trimmed

        if data.category is not None:
            hobby.category = data.category.strip() if data.category else None
        if data.icon is not None:
            hobby.icon = data.icon.strip() if data.icon else None
        if data.visibility is not None:
            hobby.is_visible = data.visibility
        elif data.is_visible is not None:
            hobby.is_visible = data.is_visible
        if data.ordering is not None:
            hobby.display_order = data.ordering
        elif data.display_order is not None:
            hobby.display_order = data.display_order

        hobby.updated_at = datetime.now(timezone.utc)
        self.db.commit()
        self.db.refresh(hobby)

        curr_snapshot = {"id": hobby.id, "name": hobby.name}

        record_content_revision(
            db=self.db,
            entity_name="hobby",
            action="PATCH",
            entity_id=str(hobby.id),
            editor_username=current_user.username,
            change_summary=f"Patched hobby '{hobby.name}'",
            previous_snapshot=prev_snapshot,
            current_snapshot=curr_snapshot
        )

        log_audit_event(
            db=self.db,
            event_type="HOBBY_PATCHED",
            status="SUCCESS",
            user_id=current_user.id,
            username=current_user.username,
            details={"hobby_id": hobby.id, "name": hobby.name},
            ip_address=client_ip
        )

        return hobby

    def delete_hobby(
        self,
        hobby_id: int,
        current_user: Any,
        client_ip: str
    ) -> Dict[str, Any]:
        hobby = self.get_hobby(hobby_id)
        name = hobby.name
        prev_snapshot = {"id": hobby.id, "name": hobby.name}

        self.db.delete(hobby)
        self.db.commit()

        record_content_revision(
            db=self.db,
            entity_name="hobby",
            action="DELETE",
            entity_id=str(hobby_id),
            editor_username=current_user.username,
            change_summary=f"Deleted hobby '{name}'",
            previous_snapshot=prev_snapshot,
            current_snapshot=None
        )

        log_audit_event(
            db=self.db,
            event_type="HOBBY_DELETED",
            status="SUCCESS",
            user_id=current_user.id,
            username=current_user.username,
            details={"hobby_id": hobby_id, "name": name},
            ip_address=client_ip
        )

        return {"success": True, "message": f"Hobby '{name}' deleted successfully."}

    # -------------------------------------------------------------------------
    # Interests Engine
    # -------------------------------------------------------------------------

    def list_interests(self, include_hidden: bool = False) -> List[Interest]:
        interests = self.interest_repo.list_interests(include_hidden=include_hidden)
        if not interests:
            from app.models.hobby_interest import HobbyInterest
            hi_interests = (
                self.db.query(HobbyInterest)
                .filter(HobbyInterest.type == "interest")
                .order_by(HobbyInterest.ordering.asc(), HobbyInterest.name.asc())
                .all()
            )
            return [
                Interest(
                    id=hi.id,
                    name=hi.name,
                    category=hi.category,
                    icon=hi.icon,
                    is_visible=True,
                    display_order=hi.ordering,
                    created_at=hi.created_at,
                    updated_at=hi.updated_at
                )
                for hi in hi_interests
            ]
        return interests

    def get_interest(self, interest_id: int) -> Interest:
        item = self.interest_repo.get_by_id(interest_id)
        if not item:
            raise ResourceNotFoundError("Interest", interest_id)
        return item

    def create_interest(
        self,
        data: InterestCreate,
        current_user: Any,
        client_ip: str
    ) -> Interest:
        profile = self.get_or_create_profile()
        trimmed_name = data.name.strip()

        dup = self.interest_repo.find_by_normalized_name(trimmed_name)
        if dup:
            raise ConflictError(f"Interest '{trimmed_name}' already exists.")

        new_interest = Interest(
            profile_id=profile.id,
            name=trimmed_name,
            category=data.category.strip() if data.category else None,
            icon=data.icon.strip() if data.icon else None,
            is_visible=data.visibility if data.is_visible is None else data.is_visible,
            display_order=data.ordering if data.display_order is None else data.display_order
        )

        self.db.add(new_interest)
        self.db.commit()
        self.db.refresh(new_interest)

        record_content_revision(
            db=self.db,
            entity_name="interest",
            action="CREATE",
            entity_id=str(new_interest.id),
            editor_username=current_user.username,
            change_summary=f"Created interest '{new_interest.name}'",
            previous_snapshot=None,
            current_snapshot={"id": new_interest.id, "name": new_interest.name, "category": new_interest.category}
        )

        log_audit_event(
            db=self.db,
            event_type="INTEREST_CREATED",
            status="SUCCESS",
            user_id=current_user.id,
            username=current_user.username,
            details={"interest_id": new_interest.id, "name": new_interest.name},
            ip_address=client_ip
        )

        return new_interest

    def update_interest(
        self,
        interest_id: int,
        data: InterestUpdate,
        current_user: Any,
        client_ip: str
    ) -> Interest:
        interest = self.get_interest(interest_id)
        trimmed_name = data.name.strip()

        dup = self.interest_repo.find_by_normalized_name(trimmed_name, exclude_id=interest_id)
        if dup:
            raise ConflictError(f"Interest '{trimmed_name}' already exists.")

        prev_snapshot = {"id": interest.id, "name": interest.name, "category": interest.category}

        interest.name = trimmed_name
        interest.category = data.category.strip() if data.category else None
        interest.icon = data.icon.strip() if data.icon else None
        interest.is_visible = data.visibility if data.is_visible is None else data.is_visible
        interest.display_order = data.ordering if data.display_order is None else data.display_order
        interest.updated_at = datetime.now(timezone.utc)

        self.db.commit()
        self.db.refresh(interest)

        curr_snapshot = {"id": interest.id, "name": interest.name, "category": interest.category}

        record_content_revision(
            db=self.db,
            entity_name="interest",
            action="UPDATE",
            entity_id=str(interest.id),
            editor_username=current_user.username,
            change_summary=f"Updated interest '{interest.name}'",
            previous_snapshot=prev_snapshot,
            current_snapshot=curr_snapshot
        )

        log_audit_event(
            db=self.db,
            event_type="INTEREST_UPDATED",
            status="SUCCESS",
            user_id=current_user.id,
            username=current_user.username,
            details={"interest_id": interest.id, "name": interest.name},
            ip_address=client_ip
        )

        return interest

    def patch_interest(
        self,
        interest_id: int,
        data: InterestPatch,
        current_user: Any,
        client_ip: str
    ) -> Interest:
        interest = self.get_interest(interest_id)
        prev_snapshot = {"id": interest.id, "name": interest.name}

        if data.name is not None:
            trimmed = data.name.strip()
            dup = self.interest_repo.find_by_normalized_name(trimmed, exclude_id=interest_id)
            if dup:
                raise ConflictError(f"Interest '{trimmed}' already exists.")
            interest.name = trimmed

        if data.category is not None:
            interest.category = data.category.strip() if data.category else None
        if data.icon is not None:
            interest.icon = data.icon.strip() if data.icon else None
        if data.visibility is not None:
            interest.is_visible = data.visibility
        elif data.is_visible is not None:
            interest.is_visible = data.is_visible
        if data.ordering is not None:
            interest.display_order = data.ordering
        elif data.display_order is not None:
            interest.display_order = data.display_order

        interest.updated_at = datetime.now(timezone.utc)
        self.db.commit()
        self.db.refresh(interest)

        curr_snapshot = {"id": interest.id, "name": interest.name}

        record_content_revision(
            db=self.db,
            entity_name="interest",
            action="PATCH",
            entity_id=str(interest.id),
            editor_username=current_user.username,
            change_summary=f"Patched interest '{interest.name}'",
            previous_snapshot=prev_snapshot,
            current_snapshot=curr_snapshot
        )

        log_audit_event(
            db=self.db,
            event_type="INTEREST_PATCHED",
            status="SUCCESS",
            user_id=current_user.id,
            username=current_user.username,
            details={"interest_id": interest.id, "name": interest.name},
            ip_address=client_ip
        )

        return interest

    def delete_interest(
        self,
        interest_id: int,
        current_user: Any,
        client_ip: str
    ) -> Dict[str, Any]:
        interest = self.get_interest(interest_id)
        name = interest.name
        prev_snapshot = {"id": interest.id, "name": interest.name}

        self.db.delete(interest)
        self.db.commit()

        record_content_revision(
            db=self.db,
            entity_name="interest",
            action="DELETE",
            entity_id=str(interest_id),
            editor_username=current_user.username,
            change_summary=f"Deleted interest '{name}'",
            previous_snapshot=prev_snapshot,
            current_snapshot=None
        )

        log_audit_event(
            db=self.db,
            event_type="INTEREST_DELETED",
            status="SUCCESS",
            user_id=current_user.id,
            username=current_user.username,
            details={"interest_id": interest_id, "name": name},
            ip_address=client_ip
        )

        return {"success": True, "message": f"Interest '{name}' deleted successfully."}
