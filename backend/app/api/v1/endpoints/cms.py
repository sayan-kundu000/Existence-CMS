from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.profile import Profile
from app.models.education import Education
from app.models.experience import Experience
from app.models.skill import Skill
from app.models.hobby import Hobby
from app.models.interest import Interest
from app.models.hobby_interest import HobbyInterest
from app.models.assessment import AssessmentResult
from app.models.audit import AuditEvent, ContentRevision
from app.models.user import User, PinSecurity
from app.api.deps import require_admin
from app.schemas.audit import DashboardStatsOut
from app.api.v1.endpoints.profile import profile_to_dict, get_or_create_profile

router = APIRouter()


@router.get("/dashboard", response_model=DashboardStatsOut)
def get_cms_dashboard_stats(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Retrieve comprehensive overview statistics for CMS administration dashboard."""
    profile = get_or_create_profile(db)
    profile_info = profile_to_dict(profile)

    edu_count = db.query(Education).count()
    exp_count = db.query(Experience).count()
    skills_count = db.query(Skill).count()

    hobbies_table_count = db.query(Hobby).count()
    interests_table_count = db.query(Interest).count()
    hi_hobby_count = db.query(HobbyInterest).filter(HobbyInterest.type == "hobby").count()
    hi_interest_count = db.query(HobbyInterest).filter(HobbyInterest.type == "interest").count()

    hobbies_count = max(hobbies_table_count, hi_hobby_count)
    interests_count = max(interests_table_count, hi_interest_count)
    hi_count = hobbies_count + interests_count

    assessments_count = db.query(AssessmentResult).count()
    revisions_count = db.query(ContentRevision).count()

    pin_record = db.query(PinSecurity).filter(PinSecurity.user_id == current_user.id).first()
    pin_configured = pin_record.is_configured if pin_record else False

    last_event = db.query(AuditEvent).order_by(AuditEvent.timestamp.desc()).first()

    return DashboardStatsOut(
        profile_configured=not profile_info["is_empty"],
        education_count=edu_count,
        experience_count=exp_count,
        work_experience_count=exp_count,
        skills_count=skills_count,
        hobbies_interests_count=hi_count,
        hobbies_count=hobbies_count,
        interests_count=interests_count,
        assessments_completed=assessments_count,
        personality_assessment_completed=(assessments_count > 0),
        pin_configured=pin_configured,
        revisions_count=revisions_count,
        last_audit_event=last_event.timestamp if last_event else None
    )
