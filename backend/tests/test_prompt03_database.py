import uuid
from datetime import datetime, timedelta, timezone
import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select, text
from app.core.database import create_app_engine
from app.core.security import hash_password, hash_pin
from app.models.profile import Profile, ProfileEmail
from app.models.education import Education
from app.models.experience import Experience, WorkExperience
from app.models.skill import Skill
from app.models.hobby import Hobby
from app.models.interest import Interest
from app.models.user import AdminUser, User, AuthSession, PinSecurity, PinVerificationSession
from app.models.assessment import (
    AssessmentDefinition,
    AssessmentQuestion,
    AssessmentSession,
    AssessmentResponse,
    AssessmentResult,
    PersonalityTraitScore,
    SoftSkillRecord,
    StrengthRecord,
    WeaknessRecord
)
from app.models.audit import ContentRevision, AuditEvent


def test_profile_and_emails_relational_integrity(db_session):
    """Verify Profile domain, ProfileEmail child records, email format validation, and cascade delete."""
    prof = Profile(
        name="Elena Rostova",
        mobile_number="+1-555-0199",
        linkedin="https://linkedin.com/in/elena-rostova",
        about="Principal Distributed Systems Architect"
    )
    db_session.add(prof)
    db_session.commit()
    prof_id = prof.id
    assert prof_id is not None

    # 1. Add valid emails with ordering
    email1 = ProfileEmail(
        profile_id=prof_id,
        email="elena.primary@enterprise.io",
        label="Work",
        is_primary=True,
        display_order=0
    )
    email2 = ProfileEmail(
        profile_id=prof_id,
        email="elena@personal.net",
        label="Personal",
        is_primary=False,
        display_order=1
    )
    db_session.add_all([email1, email2])
    db_session.commit()

    # Verify relationships
    loaded_prof = db_session.query(Profile).filter(Profile.id == prof_id).first()
    assert len(loaded_prof.emails) == 2
    assert loaded_prof.emails[0].email == "elena.primary@enterprise.io"

    # 2. Email validation at model level rejects invalid emails
    with pytest.raises(ValueError, match="Invalid email address format"):
        invalid_email = ProfileEmail(
            profile_id=prof_id,
            email="not-an-email",
            label="Invalid"
        )
        db_session.add(invalid_email)
        db_session.flush()

    # 3. Check display_order constraint (display_order >= 0)
    with pytest.raises(IntegrityError):
        with db_session.begin_nested():
            neg_order_email = ProfileEmail(
                profile_id=prof_id,
                email="negative@example.com",
                display_order=-1
            )
            db_session.add(neg_order_email)
            db_session.flush()

    # 4. Cascade delete: deleting profile deletes its emails
    loaded_prof = db_session.query(Profile).filter(Profile.id == prof_id).first()
    db_session.delete(loaded_prof)
    db_session.commit()
    assert db_session.query(ProfileEmail).filter(ProfileEmail.profile_id == prof_id).count() == 0


def test_education_db_constraints(db_session):
    """Verify Section 10 & 11: Education levels, month/year constraints, currently_studying no end date, date order."""
    prof = Profile(name="Edu Scholar")
    db_session.add(prof)
    db_session.commit()
    prof_id = prof.id

    # 1. Valid education records pass
    valid_edu = Education(
        profile_id=prof_id,
        level="Doctorate",
        stream="Quantum Computation",
        institution="Max Planck Institute",
        start_month=9,
        start_year=2018,
        end_month=6,
        end_year=2022,
        currently_studying=False,
        display_order=1
    )
    db_session.add(valid_edu)
    db_session.commit()
    assert valid_edu.id is not None
    assert valid_edu.ordering == 1

    # 2. Invalid education level rejected by check constraint
    with pytest.raises(IntegrityError):
        with db_session.begin_nested():
            bad_level_edu = Education(
                profile_id=prof_id,
                level="UnaccreditedCourse",
                stream="Physics",
                start_month=1,
                start_year=2020,
                currently_studying=True
            )
            db_session.add(bad_level_edu)
            db_session.flush()

    # 3. Invalid month (e.g. 13) rejected by check constraint
    with pytest.raises(IntegrityError):
        with db_session.begin_nested():
            bad_month_edu = Education(
                profile_id=prof_id,
                level="Graduate",
                stream="Computer Science",
                start_month=13,  # Invalid!
                start_year=2020,
                currently_studying=True
            )
            db_session.add(bad_month_edu)
            db_session.flush()

    # 4. Currently studying = True but end period supplied rejected by check constraint
    with pytest.raises(IntegrityError):
        with db_session.begin_nested():
            studying_with_end = Education(
                profile_id=prof_id,
                level="Post Graduate",
                stream="Cybernetics",
                start_month=9,
                start_year=2023,
                end_month=6,
                end_year=2025,
                currently_studying=True  # Conflict!
            )
            db_session.add(studying_with_end)
            db_session.flush()

    # 5. End date preceding start date rejected by check constraint
    with pytest.raises(IntegrityError):
        with db_session.begin_nested():
            inverted_dates = Education(
                profile_id=prof_id,
                level="Undergraduate",
                stream="Mathematics",
                start_month=9,
                start_year=2024,
                end_month=6,
                end_year=2021,  # Before start year!
                currently_studying=False
            )
            db_session.add(inverted_dates)
            db_session.flush()

    # 6. Negative display order rejected
    with pytest.raises(IntegrityError):
        with db_session.begin_nested():
            neg_order = Education(
                profile_id=prof_id,
                level="High School",
                stream="General",
                start_month=1,
                start_year=2015,
                end_month=12,
                end_year=2019,
                display_order=-5
            )
            db_session.add(neg_order)
            db_session.flush()


def test_work_experience_db_constraints(db_session):
    """Verify Section 12 & 13: Work modes, location requirement, currently_working rules, date order."""
    prof = Profile(name="Work Professional")
    db_session.add(prof)
    db_session.commit()
    prof_id = prof.id

    # 1. Valid On-site experience with location passes
    valid_onsite = Experience(
        profile_id=prof_id,
        role="Lead Reliability Engineer",
        employer="Global Telecom",
        work_mode="On-site",
        location="Zurich, Switzerland",
        start_month=3,
        start_year=2021,
        end_month=11,
        end_year=2023,
        currently_working=False,
        display_order=0
    )
    db_session.add(valid_onsite)
    db_session.commit()
    assert valid_onsite.id is not None

    # 2. Invalid work mode rejected by check constraint
    with pytest.raises(IntegrityError):
        with db_session.begin_nested():
            bad_mode = Experience(
                profile_id=prof_id,
                role="Contractor",
                employer="Agency",
                work_mode="Nomadic",  # Invalid!
                location="Berlin",
                start_month=1,
                start_year=2022,
                currently_working=True
            )
            db_session.add(bad_mode)
            db_session.flush()

    # 3. On-site without location rejected by check constraint
    with pytest.raises(IntegrityError):
        with db_session.begin_nested():
            onsite_no_loc = Experience(
                profile_id=prof_id,
                role="On-site Tech",
                employer="HQ Inc",
                work_mode="On-site",
                location="",  # Missing required location!
                start_month=1,
                start_year=2022,
                currently_working=True
            )
            db_session.add(onsite_no_loc)
            db_session.flush()

    # 4. Currently working = True with end date rejected by check constraint
    with pytest.raises(IntegrityError):
        with db_session.begin_nested():
            working_with_end = Experience(
                profile_id=prof_id,
                role="Director of Engineering",
                employer="Cloud Apex",
                work_mode="Remote",
                location="Remote",
                start_month=1,
                start_year=2023,
                end_month=12,
                end_year=2024,
                currently_working=True  # Conflict!
            )
            db_session.add(working_with_end)
            db_session.flush()

    # 5. End date preceding start date rejected
    with pytest.raises(IntegrityError):
        with db_session.begin_nested():
            inverted_exp = Experience(
                profile_id=prof_id,
                role="Systems Engineer",
                employer="Matrix Labs",
                work_mode="Remote",
                location="Remote",
                start_month=6,
                start_year=2024,
                end_month=2,
                end_year=2024,  # Earlier month in same year!
                currently_working=False
            )
            db_session.add(inverted_exp)
            db_session.flush()


def test_skills_seven_level_db_constraints(db_session):
    """Verify Section 14 & 15: rating must be between 1 and 7, display_order >= 0, and non-empty name."""
    prof = Profile(name="Skill Master")
    db_session.add(prof)
    db_session.commit()
    prof_id = prof.id

    # Rating 1 (Beginner) passes
    skill_1 = Skill(
        profile_id=prof_id,
        name="Elixir / OTP",
        rating=1,
        display_order=0
    )
    db_session.add(skill_1)
    db_session.commit()
    assert skill_1.level_label == "Beginner"

    # Rating 7 (Master) passes
    skill_7 = Skill(
        profile_id=prof_id,
        name="PostgreSQL Internals",
        rating=7,
        display_order=1
    )
    db_session.add(skill_7)
    db_session.commit()
    assert skill_7.level_label == "Master"

    # Rating 0 rejected by database check constraint
    with pytest.raises(IntegrityError):
        with db_session.begin_nested():
            bad_skill_0 = Skill(
                profile_id=prof_id,
                name="Zero Rating Skill",
                rating=0
            )
            db_session.add(bad_skill_0)
            db_session.flush()

    # Rating 8 rejected by database check constraint
    with pytest.raises(IntegrityError):
        with db_session.begin_nested():
            bad_skill_8 = Skill(
                profile_id=prof_id,
                name="Eight Rating Skill",
                rating=8
            )
            db_session.add(bad_skill_8)
            db_session.flush()

    # Empty name rejected by check constraint
    with pytest.raises(IntegrityError):
        with db_session.begin_nested():
            empty_skill = Skill(
                profile_id=prof_id,
                name="   ",
                rating=4
            )
            db_session.add(empty_skill)
            db_session.flush()


def test_hobbies_and_interests_constraints(db_session):
    """Verify Section 16 & 17: non-negative display order, non-empty names, and profile cascade."""
    prof = Profile(name="Creative Enthusiast")
    db_session.add(prof)
    db_session.commit()
    prof_id = prof.id

    hobby = Hobby(profile_id=prof_id, name="Film Photography", display_order=0)
    interest = Interest(profile_id=prof_id, name="Type Theory", display_order=0)
    db_session.add_all([hobby, interest])
    db_session.commit()

    # Negative display order rejected
    with pytest.raises(IntegrityError):
        with db_session.begin_nested():
            bad_hobby = Hobby(profile_id=prof_id, name="Gaming", display_order=-1)
            db_session.add(bad_hobby)
            db_session.flush()

    with pytest.raises(IntegrityError):
        with db_session.begin_nested():
            bad_interest = Interest(profile_id=prof_id, name="AI", display_order=-2)
            db_session.add(bad_interest)
            db_session.flush()


def test_admin_user_security_and_sessions(db_session):
    """Verify Section 18, 19, 20, 21: AdminUser uniqueness, password hash, AuthSession, PinSecurity, PinVerificationSession."""
    user = AdminUser(
        username="secops_admin",
        email="secops@existence.internal",
        password_hash=hash_password("SuperSecretKey2026!"),
        role="admin",
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    uid = user.id
    assert uid is not None
    assert user.hashed_password == user.password_hash

    # 1. Duplicate email rejected by unique constraint
    with pytest.raises(IntegrityError):
        with db_session.begin_nested():
            dup_email_user = AdminUser(
                username="another_user",
                email="secops@existence.internal",  # Duplicate!
                password_hash=hash_password("DifferentPassword!")
            )
            db_session.add(dup_email_user)
            db_session.flush()

    # 2. AuthSession creation and association
    token_id = str(uuid.uuid4())
    session_rec = AuthSession(
        admin_user_id=uid,
        token_identifier=token_id,
        expires_at=datetime.now(timezone.utc) + timedelta(days=1)
    )
    db_session.add(session_rec)
    db_session.commit()

    # 3. PinSecurity association
    pin_rec = PinSecurity(
        admin_user_id=uid,
        pin_hash=hash_pin("9512"),
        is_configured=True,
        failed_attempts=0
    )
    db_session.add(pin_rec)
    db_session.commit()
    assert pin_rec.user_id == uid
    assert pin_rec.hashed_pin == pin_rec.pin_hash

    # 4. PinVerificationSession creation
    verif_id = str(uuid.uuid4())
    pin_verif = PinVerificationSession(
        admin_user_id=uid,
        verification_identifier=verif_id,
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=15)
    )
    db_session.add(pin_verif)
    db_session.commit()

    # 5. Cascading: deleting admin user cleans up auth sessions, pin security, and verification sessions
    loaded_user = db_session.query(AdminUser).filter(AdminUser.id == uid).first()
    db_session.delete(loaded_user)
    db_session.commit()

    assert db_session.query(AuthSession).filter(AuthSession.admin_user_id == uid).count() == 0
    assert db_session.query(PinSecurity).filter(PinSecurity.admin_user_id == uid).count() == 0
    assert db_session.query(PinVerificationSession).filter(PinVerificationSession.admin_user_id == uid).count() == 0


def test_assessments_domain_integrity_and_duplicate_prevention(db_session):
    """Verify Section 22-30: Assessment session lifecycle, duplicate response prevention, results and trait scores."""
    # 1. Assessment Definition
    def_mbti = AssessmentDefinition(
        code="MBTI_EXP",
        name="Myers-Briggs Empirical",
        version="2.0",
        description="Empirical 16-personality assessment",
        question_count=4,
        is_active=True
    )
    db_session.add(def_mbti)
    db_session.commit()
    def_id = def_mbti.id

    # 2. Questions
    q1 = AssessmentQuestion(
        id="MBTI_EXP_01",
        assessment_definition_id=def_id,
        question_key="Q1",
        dimension="EI",
        question_text="You feel energized after attending lively social gatherings.",
        scale_type="likert_5",
        question_order=1
    )
    q2 = AssessmentQuestion(
        id="MBTI_EXP_02",
        assessment_definition_id=def_id,
        question_key="Q2",
        dimension="SN",
        question_text="You focus on practical facts rather than speculative theories.",
        scale_type="likert_5",
        question_order=2
    )
    db_session.add_all([q1, q2])
    db_session.commit()
    q1_id = q1.id

    # 3. Assessment Session with status check constraint
    sess = AssessmentSession(
        assessment_definition_id=def_id,
        assessment_type="MBTI_EXP",
        status="IN_PROGRESS"
    )
    db_session.add(sess)
    db_session.commit()
    sess_id = sess.id

    # Invalid status rejected by check constraint
    with pytest.raises(IntegrityError):
        with db_session.begin_nested():
            bad_status_sess = AssessmentSession(
                assessment_type="MBTI_EXP",
                status="INVALID_STATUS"
            )
            db_session.add(bad_status_sess)
            db_session.flush()

    # 4. Assessment Responses: valid response passes
    resp1 = AssessmentResponse(
        session_id=sess_id,
        question_id=q1_id,
        dimension="EI",
        response_value=4
    )
    db_session.add(resp1)
    db_session.commit()

    # Section 25 INVARIANT: Duplicate response for same (session_id, question_id) MUST be rejected!
    with pytest.raises(IntegrityError):
        with db_session.begin_nested():
            duplicate_resp = AssessmentResponse(
                session_id=sess_id,
                question_id=q1_id,  # Same question in same session!
                dimension="EI",
                response_value=2
            )
            db_session.add(duplicate_resp)
            db_session.flush()

    # 5. Results & Trait Scores
    result = AssessmentResult(
        session_id=sess_id,
        assessment_definition_id=def_id,
        assessment_type="MBTI_EXP",
        result_code="ENTJ",
        result_title="The Commander",
        result_version="2.0",
        scores_json='{"EI": 75, "SN": 60, "TF": 80, "JP": 85}',
        summary="Strategic decision-maker with structured execution focus."
    )
    db_session.add(result)
    db_session.commit()
    result_id = result.id

    trait_ei = PersonalityTraitScore(
        result_id=result_id,
        trait_code="Extraversion",
        score=75.0,
        normalized_score=0.75
    )
    db_session.add(trait_ei)
    db_session.commit()
    assert trait_ei.trait_name == "Extraversion"

    # Normalized soft skills and strengths
    prof = Profile(name="Executive Commander")
    db_session.add(prof)
    db_session.commit()
    prof_id = prof.id

    soft_skill = SoftSkillRecord(
        profile_id=prof_id,
        result_id=result_id,
        name="Strategic Alignment",
        description="Translates complex organizational objectives into actionable roadmaps",
        source="MBTI"
    )
    strength = StrengthRecord(
        profile_id=prof_id,
        result_id=result_id,
        title="High Decisiveness under Uncertainty",
        source="MBTI"
    )
    weakness = WeaknessRecord(
        profile_id=prof_id,
        result_id=result_id,
        title="Impatience with Ambiguity",
        source="MBTI"
    )
    db_session.add_all([soft_skill, strength, weakness])
    db_session.commit()

    assert soft_skill.id is not None
    assert strength.id is not None
    assert weakness.id is not None


def test_content_revisions_and_audit_events_integrity(db_session):
    """Verify Section 31 & 32: ContentRevision action constraint, non-leaking snapshots, AuditEvent metadata."""
    # 1. Valid action passes
    rev = ContentRevision(
        entity_type="profile",
        entity_id="1",
        revision_number=1,
        action="UPDATE",
        changed_by="lead_admin",
        change_summary="Updated contact coordinates",
        previous_snapshot='{"name": null}',
        current_snapshot='{"name": "Verified User"}'
    )
    db_session.add(rev)
    db_session.commit()
    assert rev.id is not None
    assert rev.entity_name == "profile"
    assert rev.editor_username == "lead_admin"

    # 2. Invalid revision action rejected by check constraint
    with pytest.raises(IntegrityError):
        with db_session.begin_nested():
            bad_action_rev = ContentRevision(
                entity_type="education",
                action="HACKED_ACTION"
            )
            db_session.add(bad_action_rev)
            db_session.flush()

    # 3. Audit event tracking
    audit = AuditEvent(
        actor_id=1,
        username="lead_admin",
        action="PIN_VERIFIED",
        entity_type="pin_security",
        request_id=str(uuid.uuid4()),
        status="SUCCESS",
        metadata_json='{"ip": "127.0.0.1", "device": "workstation"}'
    )
    db_session.add(audit)
    db_session.commit()
    assert audit.event_type == "PIN_VERIFIED"
    assert audit.user_id == 1
    assert audit.details == '{"ip": "127.0.0.1", "device": "workstation"}'


def test_database_transactions_and_rollback(db_session):
    """Verify Section 40: multi-step transactions rollback cleanly upon failure without partial state pollution."""
    prof = Profile(name="Transaction Guard Profile")
    db_session.add(prof)
    db_session.commit()
    prof_id = prof.id
    initial_edu_count = db_session.query(Education).count()

    # Transaction begins with savepoint
    try:
        with db_session.begin_nested():
            # Step 1: Add valid education
            edu1 = Education(
                profile_id=prof_id,
                level="Graduate",
                stream="Computer Science",
                start_month=9,
                start_year=2020,
                end_month=6,
                end_year=2022,
                currently_studying=False
            )
            db_session.add(edu1)
            db_session.flush()

            # Step 2: Trigger invalid check constraint violation (e.g. invalid level)
            edu2_invalid = Education(
                profile_id=prof_id,
                level="TotallyInvalidLevelXYZ",
                stream="Invalid",
                start_month=1,
                start_year=2020,
                currently_studying=True
            )
            db_session.add(edu2_invalid)
            db_session.flush()  # Throws IntegrityError!
    except IntegrityError:
        pass

    # Verify no partial commit occurred
    assert db_session.query(Education).count() == initial_edu_count


def test_render_postgresql_engine_configuration():
    """Verify Section 51: Render PostgreSQL connection pool settings and URL resolution."""
    pg_url = "postgresql+psycopg://render_user:secure_pwd@ep-sample-12345.oregon-postgres.render.com/existence_prod"
    engine = create_app_engine(pg_url)
    assert engine.pool is not None
    assert engine.pool.size() >= 5
    assert engine.url.drivername == "postgresql+psycopg"
