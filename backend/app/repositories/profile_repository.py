import json
from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from app.models.profile import Profile, ProfileEmail
from app.repositories.base import BaseRepository


class ProfileRepository(BaseRepository[Profile]):
    def __init__(self, db: Session):
        super().__init__(Profile, db)

    def get_or_create_profile(self) -> Profile:
        """Retrieves the authoritative profile or initializes a clean empty template."""
        profile = self.db.query(Profile).first()
        if not profile:
            profile = Profile(
                name=None,
                email_ids="[]",
                mobile_number=None,
                linkedin=None,
                about=None
            )
            self.db.add(profile)
            self.db.commit()
            self.db.refresh(profile)
        return profile

    def get_profile(self, profile_id: Optional[int] = None) -> Optional[Profile]:
        if profile_id:
            return self.db.query(Profile).filter(Profile.id == profile_id).first()
        return self.get_or_create_profile()

    def get_profile_with_relations(self, profile_id: Optional[int] = None) -> Profile:
        """
        Loads profile and eagerly joins child entities to eliminate N+1 database queries.
        """
        query = (
            self.db.query(Profile)
            .options(
                joinedload(Profile.emails),
                joinedload(Profile.educations),
                joinedload(Profile.work_experiences),
                joinedload(Profile.skills),
                joinedload(Profile.projects),
                joinedload(Profile.hobbies),
                joinedload(Profile.interests)
            )
        )
        if profile_id:
            profile = query.filter(Profile.id == profile_id).first()
        else:
            profile = query.first()

        if not profile:
            return self.get_or_create_profile()
        return profile

    def get_emails(self, profile_id: int) -> List[ProfileEmail]:
        return (
            self.db.query(ProfileEmail)
            .filter(ProfileEmail.profile_id == profile_id)
            .order_by(ProfileEmail.display_order.asc(), ProfileEmail.created_at.asc())
            .all()
        )

    def get_email_by_id(self, email_id: int, profile_id: int) -> Optional[ProfileEmail]:
        return (
            self.db.query(ProfileEmail)
            .filter(ProfileEmail.id == email_id, ProfileEmail.profile_id == profile_id)
            .first()
        )

    def get_email_by_address(self, email: str, profile_id: int) -> Optional[ProfileEmail]:
        clean_email = email.strip().lower()
        return (
            self.db.query(ProfileEmail)
            .filter(
                ProfileEmail.profile_id == profile_id,
                func.lower(func.trim(ProfileEmail.email)) == clean_email
            )
            .first()
        )

    def count_emails(self, profile_id: int) -> int:
        return self.db.query(ProfileEmail).filter(ProfileEmail.profile_id == profile_id).count()

    def add_email(
        self,
        profile_id: int,
        email: str,
        label: str = "Primary",
        is_primary: bool = False,
        display_order: int = 0,
        is_public: bool = True
    ) -> ProfileEmail:
        if is_primary:
            # Demote any existing primary email inside the transaction
            self.db.query(ProfileEmail).filter(
                ProfileEmail.profile_id == profile_id,
                ProfileEmail.is_primary == True
            ).update({"is_primary": False})

        new_email = ProfileEmail(
            profile_id=profile_id,
            email=email.strip(),
            label=label.strip() if label else "Primary",
            is_primary=is_primary,
            is_public=is_public,
            display_order=display_order
        )
        self.db.add(new_email)
        self.db.commit()
        self.db.refresh(new_email)
        return new_email

    def set_primary_email(self, profile_id: int, email_id: int) -> ProfileEmail:
        """
        Promotes target email and demotes old primary inside an atomic transaction.
        """
        # Demote current primary
        self.db.query(ProfileEmail).filter(
            ProfileEmail.profile_id == profile_id,
            ProfileEmail.id != email_id,
            ProfileEmail.is_primary == True
        ).update({"is_primary": False})

        # Promote target
        target = self.get_email_by_id(email_id, profile_id)
        if target:
            target.is_primary = True
            target.updated_at = datetime.now(timezone.utc)
            self.db.commit()
            self.db.refresh(target)
        return target

    def sync_email_ids(self, profile: Profile) -> None:
        """Synchronizes relational profile_emails to profile.email_ids JSON cache."""
        emails = self.get_emails(profile.id)
        profile.email_ids = json.dumps([e.email for e in emails])
        profile.updated_at = datetime.now(timezone.utc)
        self.db.commit()
        self.db.refresh(profile)
