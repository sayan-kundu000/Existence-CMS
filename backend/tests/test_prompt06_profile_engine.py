import pytest
from datetime import datetime, timezone
from app.models.profile import Profile, ProfileEmail
from app.models.education import Education
from app.models.experience import Experience
from app.models.hobby import Hobby
from app.models.interest import Interest
from app.models.audit import ContentRevision, AuditEvent


def test_01_personal_info_empty_state_and_retrieval(client, admin_headers):
    """
    Prompt 06 Sections 4, 5, 83:
    Profile must start empty without fictitious or fabricated personal data.
    The identifier remains stable and is_empty is True until real data is supplied.
    """
    res = client.get("/api/v1/profile")
    assert res.status_code == 200
    data = res.json()
    assert data["name"] is None
    assert data["about"] is None
    assert data["mobile_number"] is None
    assert data["linkedin"] is None
    assert data["is_empty"] is True
    assert isinstance(data["email_ids"], list)
    assert len(data["email_ids"]) == 0


def test_02_personal_info_validations_and_sanitization(client, admin_headers):
    """
    Prompt 06 Sections 6-10:
    Personal Information validation rules:
    - Name: whitespace trimmed
    - About: script tags rejected
    - Mobile: international phone format validation
    - LinkedIn: valid URL format validation
    """
    # 1. Invalid Mobile format rejected (422)
    bad_phone_res = client.put("/api/v1/profile", headers=admin_headers, json={
        "name": "Jane Doe",
        "mobile_number": "invalid-letters-1234"
    })
    assert bad_phone_res.status_code == 422

    # 2. Invalid LinkedIn format rejected (422)
    bad_li_res = client.put("/api/v1/profile", headers=admin_headers, json={
        "name": "Jane Doe",
        "linkedin": "https://facebook.com/fakeuser"
    })
    assert bad_li_res.status_code == 422

    # 3. HTML script tag in about rejected (422)
    xss_res = client.put("/api/v1/profile", headers=admin_headers, json={
        "name": "Jane Doe",
        "about": "Hello <script>alert('xss')</script> world"
    })
    assert xss_res.status_code == 422

    # 4. Valid update succeeds with trimmed whitespace and valid coordinates
    good_res = client.put("/api/v1/profile", headers=admin_headers, json={
        "name": "  Alex Morgan  ",
        "mobile_number": "+1 (555) 234-5678",
        "linkedin": "https://linkedin.com/in/alex-morgan-lead",
        "about": "Senior Systems Architect specializing in distributed workflows."
    })
    assert good_res.status_code == 200
    data = good_res.json()
    assert data["name"] == "Alex Morgan"
    assert data["mobile_number"] == "+1 (555) 234-5678"
    assert data["linkedin"] == "https://linkedin.com/in/alex-morgan-lead"
    assert "Senior Systems Architect" in data["about"]
    assert data["is_empty"] is False


def test_03_email_engine_atomic_primary_and_deletion_protection(client, admin_headers):
    """
    Prompt 06 Sections 11-14:
    Multi-email management:
    - Case-insensitive duplicate detection
    - Atomic primary email switch inside transaction
    - Business rule: Cannot delete the only registered email address
    - Public / Private email visibility flag
    """
    # 1. Add primary email
    e1 = client.post("/api/v1/profile/emails", headers=admin_headers, json={
        "email": "primary@existence.org",
        "label": "Work",
        "is_primary": True,
        "is_public": True,
        "display_order": 0
    })
    assert e1.status_code == 201
    e1_id = e1.json()["id"]

    # 2. Add duplicate email (case-insensitive) -> 409 Conflict
    dup_res = client.post("/api/v1/profile/emails", headers=admin_headers, json={
        "email": "PRIMARY@existence.org",
        "label": "Duplicate"
    })
    assert dup_res.status_code == 409

    # 3. Attempt to delete the ONLY email -> 400 BusinessRuleError
    del_only_res = client.delete(f"/api/v1/profile/emails/{e1_id}", headers=admin_headers)
    assert del_only_res.status_code == 400
    assert "only email address" in del_only_res.json()["error"]["message"]

    # 4. Add secondary private email
    e2 = client.post("/api/v1/profile/emails", headers=admin_headers, json={
        "email": "personal@private.net",
        "label": "Personal",
        "is_primary": False,
        "is_public": False,
        "display_order": 1
    })
    assert e2.status_code == 201
    e2_id = e2.json()["id"]

    # 5. Atomically promote e2 to primary via dedicated endpoint
    prom_res = client.post(f"/api/v1/profile/emails/{e2_id}/primary", headers=admin_headers)
    assert prom_res.status_code == 200
    assert prom_res.json()["is_primary"] is True

    # Verify e1 was demoted in the same transaction
    list_res = client.get("/api/v1/profile/emails", headers=admin_headers)
    emails = list_res.json()
    e1_fetched = next(e for e in emails if e["id"] == e1_id)
    e2_fetched = next(e for e in emails if e["id"] == e2_id)
    assert e1_fetched["is_primary"] is False
    assert e2_fetched["is_primary"] is True

    # 6. Now that there are 2 emails, deleting e1 is allowed
    del_res = client.delete(f"/api/v1/profile/emails/{e1_id}", headers=admin_headers)
    assert del_res.status_code == 200


def test_04_education_engine_rules_and_ordering(client, admin_headers):
    """
    Prompt 06 Sections 15-20:
    Education domain rules:
    - Exactly 6 allowed levels
    - Currently studying = True clears ending dates
    - Ending date before start date rejected (422)
    - Chronological sorting: current / most recent first
    - Duplicate detection
    """
    # 1. Invalid Education Level rejected (422)
    bad_level_res = client.post("/api/v1/education", headers=admin_headers, json={
        "level": "Associate Degree",  # Not in whitelisted 6
        "stream": "Information Systems",
        "starting_month_year": "Sep 2020",
        "ending_month_year": "Jun 2024"
    })
    assert bad_level_res.status_code == 422

    # 2. Invalid date order rejected: Start: Sep 2024, End: Mar 2024 (422)
    bad_dates_res = client.post("/api/v1/education", headers=admin_headers, json={
        "level": "Post Graduate",
        "stream": "Computer Science",
        "starting_month_year": "Sep 2024",
        "ending_month_year": "Mar 2024"
    })
    assert bad_dates_res.status_code == 422

    # 3. Create completed education: High School (2016-2020)
    hs_res = client.post("/api/v1/education", headers=admin_headers, json={
        "level": "High School",
        "stream": "Sciences",
        "institution": "Central Academy",
        "starting_month_year": "Aug 2016",
        "ending_month_year": "May 2020",
        "currently_studying": False
    })
    assert hs_res.status_code == 201
    hs_id = hs_res.json()["id"]

    # 4. Create currently studying education: Doctorate (started Sep 2024, currently studying)
    # Even if client accidentally sends ending dates, backend MUST enforce null
    doc_res = client.post("/api/v1/education", headers=admin_headers, json={
        "level": "Doctorate",
        "stream": "Applied Mathematics",
        "institution": "Institute of Technology",
        "starting_month_year": "Sep 2024",
        "ending_month_year": "Jun 2028",  # Should be cleared by backend rule
        "currently_studying": True
    })
    assert doc_res.status_code == 201
    doc_data = doc_res.json()
    assert doc_data["currently_studying"] is True
    assert doc_data["ending_month_year"] is None
    doc_id = doc_data["id"]

    # 5. Verify Chronological Ordering: Doctorate (current, 2024) appears BEFORE High School (2016)
    list_res = client.get("/api/v1/education")
    assert list_res.status_code == 200
    edu_list = list_res.json()
    assert len(edu_list) >= 2
    assert edu_list[0]["id"] == doc_id
    assert edu_list[1]["id"] == hs_id

    # 6. Duplicate prevention: Re-creating identical record fails (409)
    dup_res = client.post("/api/v1/education", headers=admin_headers, json={
        "level": "Doctorate",
        "stream": "Applied Mathematics",
        "institution": "Institute of Technology",
        "starting_month_year": "Sep 2024",
        "currently_studying": True
    })
    assert dup_res.status_code == 409


def test_05_work_experience_engine_rules_and_ordering(client, admin_headers):
    """
    Prompt 06 Sections 22-28:
    Work experience domain rules:
    - 3 work modes: On-site, Remote, Hybrid
    - Remote allows optional location (defaults to Remote)
    - On-site / Hybrid REQUIRES location
    - Currently working = True clears ending dates
    - Ending date before start date rejected
    - Chronological sorting: current / most recent first
    """
    # 1. Invalid work mode rejected (422)
    bad_mode_res = client.post("/api/v1/experience", headers=admin_headers, json={
        "role": "Consultant",
        "employer": "Self-employed",
        "work_mode": "Freelance",  # Invalid
        "starting_month_year": "Jan 2022"
    })
    assert bad_mode_res.status_code == 422

    # 2. On-site missing location rejected (422)
    bad_loc_res = client.post("/api/v1/experience", headers=admin_headers, json={
        "role": "Lab Engineer",
        "employer": "Hardware Corp",
        "work_mode": "On-site",
        "location": "",  # Required for On-site
        "starting_month_year": "Jan 2022"
    })
    assert bad_loc_res.status_code == 422

    # 3. Remote with omitted location succeeds and defaults location
    rem_res = client.post("/api/v1/experience", headers=admin_headers, json={
        "role": "Backend Engineer",
        "employer": "Distributed Labs",
        "work_mode": "Remote",
        "starting_month_year": "Mar 2021",
        "ending_month_year": "Dec 2023",
        "currently_working": False
    })
    assert rem_res.status_code == 201
    assert rem_res.json()["location"] == "Remote"
    past_exp_id = rem_res.json()["id"]

    # 4. Currently working experience clears ending date
    curr_res = client.post("/api/v1/experience", headers=admin_headers, json={
        "role": "Principal Architect",
        "employer": "Existence Global",
        "work_mode": "Hybrid",
        "location": "Boston, MA",
        "starting_month_year": "Jan 2024",
        "ending_month_year": "Dec 2025",  # Must be cleared
        "currently_working": True
    })
    assert curr_res.status_code == 201
    curr_data = curr_res.json()
    assert curr_data["currently_working"] is True
    assert curr_data["ending_month_year"] is None
    curr_exp_id = curr_data["id"]

    # 5. Chronological Ordering: Current position (Jan 2024) precedes past position (Mar 2021)
    list_res = client.get("/api/v1/experience")
    assert list_res.status_code == 200
    exps = list_res.json()
    assert len(exps) >= 2
    assert exps[0]["id"] == curr_exp_id
    assert exps[1]["id"] == past_exp_id


def test_06_hobbies_and_interests_segregation_and_deduplication(client, admin_headers):
    """
    Prompt 06 Sections 29-32:
    Hobbies and Interests must be strictly segregated conceptually:
    - Hobbies = activities enjoyed doing
    - Interests = domains, fields, or subjects interested in
    - Case-insensitive & trimmed duplicate detection
    """
    # 1. Create Hobby
    h1 = client.post("/api/v1/hobbies", headers=admin_headers, json={
        "name": "  Astrophotography  ",
        "category": "Astronomy"
    })
    assert h1.status_code == 201
    assert h1.json()["name"] == "Astrophotography"

    # Duplicate hobby (case-insensitive) rejected -> 409
    h_dup = client.post("/api/v1/hobbies", headers=admin_headers, json={
        "name": "astrophotography",
        "category": "Photography"
    })
    assert h_dup.status_code == 409

    # 2. Create Interest with same name as Hobby is allowed because they are separate domains
    i1 = client.post("/api/v1/interests", headers=admin_headers, json={
        "name": "Astrophotography",
        "category": "Optics"
    })
    assert i1.status_code == 201
    assert i1.json()["name"] == "Astrophotography"

    # Duplicate interest (case-insensitive) rejected -> 409
    i_dup = client.post("/api/v1/interests", headers=admin_headers, json={
        "name": "ASTROPHOTOGRAPHY"
    })
    assert i_dup.status_code == 409


def test_07_profile_completeness_calculation(client, admin_headers):
    """
    Prompt 06 Section 33:
    Deterministic 9-dimension Profile Completeness Calculation:
    1. Personal Information (name, mobile, linkedin)
    2. Email
    3. About
    4. Education
    5. Experience
    6. Skills
    7. Hobbies
    8. Interests
    9. Personality
    """
    res = client.get("/api/v1/profile/completeness")
    assert res.status_code == 200
    comp = res.json()
    assert comp["dimensions_total"] == 9
    assert isinstance(comp["score_percentage"], float)
    assert 0 <= comp["score_percentage"] <= 100
    assert isinstance(comp["breakdown"], dict)
    assert "personal_info" in comp["breakdown"]
    assert "education" in comp["breakdown"]
    assert "experience" in comp["breakdown"]
    assert "hobbies" in comp["breakdown"]
    assert "interests" in comp["breakdown"]


def test_08_consolidated_public_profile_and_boundary_protection(client, admin_headers):
    """
    Prompt 06 Sections 37, 59, 74:
    Consolidated Public Profile endpoint (/api/v1/profile/public):
    - Unauthenticated access permitted
    - Single-query consolidation eliminating N+1 requests
    - Private emails excluded (only is_public=True visible)
    - Zero secrets, hashes, PIN data, revisions, or audits leaked
    """
    # 1. Fetch public consolidated profile without headers
    pub_res = client.get("/api/v1/profile/public")
    assert pub_res.status_code == 200
    pub_data = pub_res.json()

    assert "profile" in pub_data
    assert "education" in pub_data
    assert "experience" in pub_data
    assert "hobbies" in pub_data
    assert "interests" in pub_data
    assert "skills" in pub_data
    assert "personality" in pub_data

    # Check that private emails are NOT exposed in public emails list
    if pub_data["profile"].get("emails"):
        for em in pub_data["profile"]["emails"]:
            assert em["is_public"] is True

    # Security check: verify sensitive keys are nowhere in the public response
    pub_text = pub_res.text.lower()
    assert "hashed_password" not in pub_text
    assert "hashed_pin" not in pub_text
    assert "access_token" not in pub_text
    assert "audit_events" not in pub_text
    assert "personal@private.net" not in pub_text  # Private email must not leak


def test_09_security_and_pin_enforcement(client):
    """
    Prompt 06 Sections 43, 48, 73:
    Security enforcement:
    - Unauthenticated mutations rejected (401)
    - Sensitive operations require valid PIN header (403 without PIN)
    """
    # 1. Unauthenticated education creation -> 401
    unauth_res = client.post("/api/v1/education", json={
        "level": "Graduate",
        "stream": "Economics",
        "starting_month_year": "Sep 2021"
    })
    assert unauth_res.status_code == 401

    # 2. Authenticated but missing PIN header for mutation -> 403
    login_res = client.post("/api/v1/auth/login", json={"username": "admin", "password": "Admin@Existence2026!"})
    token = login_res.json()["access_token"]
    no_pin_headers = {"Authorization": f"Bearer {token}"}

    no_pin_res = client.post("/api/v1/education", headers=no_pin_headers, json={
        "level": "Graduate",
        "stream": "Economics",
        "starting_month_year": "Sep 2021"
    })
    assert no_pin_res.status_code == 403
    assert "PIN" in no_pin_res.json()["error"]["message"]


def test_10_revisions_and_audit_integration(client, admin_headers, db_session):
    """
    Prompt 06 Sections 46, 47:
    Mutations in the Profile Engine must create revisions and audit log records.
    """
    # 1. Perform a mutation via the Profile Engine
    res = client.post("/api/v1/education", headers=admin_headers, json={
        "level": "Graduate",
        "stream": "Cybernetics",
        "institution": "Polytechnic",
        "starting_month_year": "Sep 2020",
        "ending_month_year": "Jun 2024",
        "currently_studying": False
    })
    assert res.status_code == 201

    # 2. Verify that content revisions exist in database
    revs = db_session.query(ContentRevision).filter(ContentRevision.entity_name == "education").all()
    assert len(revs) > 0
    assert any("Cybernetics" in (r.change_summary or "") for r in revs)

    # 3. Verify that audit events exist in database
    events = db_session.query(AuditEvent).filter(AuditEvent.event_type == "EDUCATION_CREATED").all()
    assert len(events) > 0

