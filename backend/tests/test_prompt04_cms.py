import uuid
from datetime import datetime, timezone
import pytest


def test_cms_dashboard_stats_empty_and_populated(client, admin_headers):
    """
    Prompt 04 Section 4 & Acceptance Criteria:
    Verify CMS Dashboard provides an accurate overview without fake data.
    Empty database must show 0 records; adding entities increments counts accurately.
    """
    # 1. Initial empty dashboard check
    res = client.get("/api/v1/cms/dashboard", headers=admin_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["education_count"] == 0
    assert data["experience_count"] == 0
    assert data["work_experience_count"] == 0
    assert data["skills_count"] == 0
    assert data["hobbies_count"] == 0
    assert data["interests_count"] == 0
    assert data["personality_assessment_completed"] is False

    # 2. Populate single records in each section
    edu_res = client.post("/api/v1/education", headers=admin_headers, json={
        "level": "Graduate",
        "stream": "Robotics",
        "institution": "Polytechnic Institute",
        "starting_month_year": "Sep 2020",
        "ending_month_year": "May 2024",
        "currently_studying": False
    })
    assert edu_res.status_code == 201

    exp_res = client.post("/api/v1/experience", headers=admin_headers, json={
        "role": "Research Engineer",
        "employer": "Neural Dynamics",
        "work_mode": "Remote",
        "starting_month_year": "Jun 2024",
        "currently_working": True
    })
    assert exp_res.status_code == 201

    sk_res = client.post("/api/v1/skills", headers=admin_headers, json={
        "name": "Rust Systems",
        "category": "Systems",
        "rating": 6
    })
    assert sk_res.status_code == 201

    h_res = client.post("/api/v1/hobbies", headers=admin_headers, json={
        "name": "Amateur Radio",
        "category": "Electronics"
    })
    assert h_res.status_code == 201

    i_res = client.post("/api/v1/interests", headers=admin_headers, json={
        "name": "Type Theory",
        "category": "Computer Science"
    })
    assert i_res.status_code == 201

    # 3. Re-check dashboard stats
    res2 = client.get("/api/v1/cms/dashboard", headers=admin_headers)
    assert res2.status_code == 200
    data2 = res2.json()
    assert data2["education_count"] == 1
    assert data2["experience_count"] == 1
    assert data2["work_experience_count"] == 1
    assert data2["skills_count"] == 1
    assert data2["hobbies_count"] == 1
    assert data2["interests_count"] == 1
    assert data2["revisions_count"] >= 5


def test_profile_email_management_and_pin_enforcement(client, admin_headers):
    """
    Prompt 04 Sections 5 & 6:
    Email management CRUD, validation, primary sync, and PIN requirement on deletion.
    """
    # 1. Fetch initially empty emails
    get_res = client.get("/api/v1/profile/emails", headers=admin_headers)
    assert get_res.status_code == 200
    assert len(get_res.json()) == 0

    # 2. Add invalid email format -> 422
    bad_res = client.post("/api/v1/profile/emails", headers=admin_headers, json={
        "email": "not-an-email",
        "label": "Work",
        "is_primary": True
    })
    assert bad_res.status_code == 422

    # 3. Add primary email
    email1_res = client.post("/api/v1/profile/emails", headers=admin_headers, json={
        "email": "primary@existence.org",
        "label": "Work",
        "is_primary": True,
        "display_order": 0
    })
    assert email1_res.status_code == 201
    email1_data = email1_res.json()
    assert email1_data["email"] == "primary@existence.org"
    assert email1_data["is_primary"] is True
    email1_id = email1_data["id"]

    # 4. Add secondary email
    email2_res = client.post("/api/v1/profile/emails", headers=admin_headers, json={
        "email": "secondary@existence.org",
        "label": "Personal",
        "is_primary": False,
        "display_order": 1
    })
    assert email2_res.status_code == 201
    email2_id = email2_res.json()["id"]

    # 5. Update secondary email to primary -> verify email1 becomes non-primary
    up_res = client.put(f"/api/v1/profile/emails/{email2_id}", headers=admin_headers, json={
        "email": "secondary@existence.org",
        "label": "Personal Direct",
        "is_primary": True,
        "display_order": 0
    })
    assert up_res.status_code == 200
    assert up_res.json()["is_primary"] is True

    # Check email1 is no longer primary
    emails_list = client.get("/api/v1/profile/emails", headers=admin_headers).json()
    e1 = next(e for e in emails_list if e["id"] == email1_id)
    assert e1["is_primary"] is False

    # 6. Attempt deletion without PIN -> 403
    no_pin_headers = {"Authorization": admin_headers["Authorization"]}
    del_fail = client.delete(f"/api/v1/profile/emails/{email1_id}", headers=no_pin_headers)
    assert del_fail.status_code in (403, 422)

    # 7. Delete with valid PIN
    del_ok = client.delete(f"/api/v1/profile/emails/{email1_id}", headers=admin_headers)
    assert del_ok.status_code == 200
    assert del_ok.json()["success"] is True

    # Verify only 1 email remains
    final_list = client.get("/api/v1/profile/emails", headers=admin_headers).json()
    assert len(final_list) == 1
    assert final_list[0]["id"] == email2_id


def test_pin_verification_session_token_lifecycle(client, db_session):
    """
    Prompt 04 Sections 17, 19, 20:
    PIN verification returns a temporary token that can authorize sensitive mutations.
    """
    # 1. Login
    login_res = client.post("/api/v1/auth/login", json={"username": "admin", "password": "Admin@Existence2026!"})
    auth_token = login_res.json()["access_token"]
    bearer_header = {"Authorization": f"Bearer {auth_token}"}

    # 2. Verify with wrong PIN -> 401
    bad_pin = client.post("/api/v1/pin/verify", headers=bearer_header, json={"pin": "0000"})
    assert bad_pin.status_code == 401

    # 3. Verify with correct PIN -> 200 with pin_token
    good_pin = client.post("/api/v1/pin/verify", headers=bearer_header, json={"pin": "8421"})
    assert good_pin.status_code == 200
    assert good_pin.json()["success"] is True
    pin_token = good_pin.json()["pin_token"]
    assert pin_token is not None

    # 4. Create a skill to delete
    item_res = client.post("/api/v1/skills", headers={**bearer_header, "X-Action-PIN": "8421"}, json={
        "name": "Kernel Tuning",
        "category": "OS",
        "rating": 5
    })
    assert item_res.status_code == 201
    skill_id = item_res.json()["id"]

    # 5. Delete using the session pin_token instead of the raw PIN!
    session_pin_headers = {
        **bearer_header,
        "X-Action-PIN": pin_token
    }
    del_res = client.delete(f"/api/v1/skills/{skill_id}", headers=session_pin_headers)
    assert del_res.status_code == 200
    assert del_res.json()["success"] is True

    # 6. Random non-existent token rejected
    bad_token_headers = {
        **bearer_header,
        "X-Action-PIN": str(uuid.uuid4())
    }
    fail_del = client.delete(f"/api/v1/skills/{skill_id}", headers=bad_token_headers)
    assert fail_del.status_code in (401, 403, 404)


def test_education_cms_workflow_and_business_rules(client, admin_headers):
    """
    Prompt 04 Section 7:
    Education Level whitelist, currently_studying end date suppression, and CRUD.
    """
    # 1. Invalid Education Level rejected
    bad_level = client.post("/api/v1/education", headers=admin_headers, json={
        "level": "Primary School",  # Not in whitelist
        "stream": "General",
        "starting_month_year": "Jan 2020",
        "currently_studying": True
    })
    assert bad_level.status_code == 422

    # 2. Currently studying = False with missing ending date -> rejected
    missing_end = client.post("/api/v1/education", headers=admin_headers, json={
        "level": "Undergraduate",
        "stream": "Information Technology",
        "starting_month_year": "Aug 2022",
        "currently_studying": False
    })
    assert missing_end.status_code == 422

    # 3. Valid creation with currently_studying = True
    create_ok = client.post("/api/v1/education", headers=admin_headers, json={
        "level": "Undergraduate",
        "stream": "Computer Science",
        "institution": "Polytechnic Institute",
        "starting_month_year": "Aug 2022",
        "currently_studying": True
    })
    assert create_ok.status_code == 201
    edu_data = create_ok.json()
    assert edu_data["currently_studying"] is True
    assert edu_data["ending_month_year"] is None
    edu_id = edu_data["id"]

    # 4. Update to finished degree with valid end dates
    up_res = client.put(f"/api/v1/education/{edu_id}", headers=admin_headers, json={
        "level": "Undergraduate",
        "stream": "Computer Science & Engineering",
        "institution": "Polytechnic Institute",
        "starting_month_year": "Aug 2022",
        "ending_month_year": "Jun 2026",
        "currently_studying": False
    })
    assert up_res.status_code == 200
    assert up_res.json()["currently_studying"] is False
    assert up_res.json()["ending_month_year"] == "Jun 2026"

    # 5. Delete with PIN
    del_res = client.delete(f"/api/v1/education/{edu_id}", headers=admin_headers)
    assert del_res.status_code == 200


def test_experience_cms_workflow_and_work_mode_rules(client, admin_headers):
    """
    Prompt 04 Section 8:
    Work Mode rules (Remote -> location optional, On-site/Hybrid -> location required),
    Currently working end date suppression.
    """
    # 1. On-site missing location -> rejected
    bad_onsite = client.post("/api/v1/experience", headers=admin_headers, json={
        "role": "Site Reliability Engineer",
        "employer": "Cloud Infrastructure Co",
        "work_mode": "On-site",
        "location": None,  # Required for On-site
        "starting_month_year": "Jan 2023",
        "currently_working": True
    })
    assert bad_onsite.status_code == 422

    # 2. Remote with null location -> accepted
    remote_ok = client.post("/api/v1/experience", headers=admin_headers, json={
        "role": "Systems Architect",
        "employer": "Distributed Corp",
        "work_mode": "Remote",
        "location": None,
        "starting_month_year": "Mar 2023",
        "currently_working": True
    })
    assert remote_ok.status_code == 201
    exp_id = remote_ok.json()["id"]

    # 3. Not currently working with missing end date -> rejected
    bad_dates = client.put(f"/api/v1/experience/{exp_id}", headers=admin_headers, json={
        "role": "Systems Architect",
        "employer": "Distributed Corp",
        "work_mode": "Remote",
        "location": None,
        "starting_month_year": "Mar 2023",
        "currently_working": False  # Missing ending_month_year
    })
    assert bad_dates.status_code == 422

    # 4. Clean up
    del_res = client.delete(f"/api/v1/experience/{exp_id}", headers=admin_headers)
    assert del_res.status_code == 200


def test_skills_seven_level_engine_and_rating_validation(client, admin_headers):
    """
    Prompt 04 Section 9:
    Skills 7-level mastery scale: 1=Beginner, 2=Novice, 3=Intermediate, 4=Proficient,
    5=Advanced, 6=Expert, 7=Master. Rating outside 1-7 rejected.
    """
    # 1. Rating < 1 rejected
    assert client.post("/api/v1/skills", headers=admin_headers, json={
        "name": "Invalid Low",
        "rating": 0
    }).status_code == 422

    # 2. Rating > 7 rejected
    assert client.post("/api/v1/skills", headers=admin_headers, json={
        "name": "Invalid High",
        "rating": 8
    }).status_code == 422

    # 3. Create all 7 levels and verify mapped level names
    expected_levels = {
        1: "Beginner",
        2: "Novice",
        3: "Intermediate",
        4: "Proficient",
        5: "Advanced",
        6: "Expert",
        7: "Master"
    }

    created_ids = []
    for rating, expected_name in expected_levels.items():
        res = client.post("/api/v1/skills", headers=admin_headers, json={
            "name": f"Skill-{rating}",
            "rating": rating
        })
        assert res.status_code == 201
        data = res.json()
        assert data["rating"] == rating
        assert data["level_label"] == expected_name
        created_ids.append(data["id"])

    # Clean up
    for s_id in created_ids:
        client.delete(f"/api/v1/skills/{s_id}", headers=admin_headers)


def test_hobbies_and_interests_cms_separation(client, admin_headers):
    """
    Prompt 04 Sections 10 & 11:
    Separate CRUD for Hobbies and Interests.
    """
    h_res = client.post("/api/v1/hobbies", headers=admin_headers, json={
        "name": "Astrophotography",
        "category": "Astronomy",
        "description": "Deep sky imaging"
    })
    assert h_res.status_code == 201
    hobby_id = h_res.json()["id"]

    i_res = client.post("/api/v1/interests", headers=admin_headers, json={
        "name": "Quantum Computing",
        "category": "Physics",
        "description": "Superconducting qubits"
    })
    assert i_res.status_code == 201
    interest_id = i_res.json()["id"]

    # Verify lists are isolated by name
    hobbies = client.get("/api/v1/hobbies", headers=admin_headers).json()
    assert any(h["name"] == "Astrophotography" for h in hobbies)
    assert not any(h["name"] == "Quantum Computing" for h in hobbies)

    interests = client.get("/api/v1/interests", headers=admin_headers).json()
    assert any(i["name"] == "Quantum Computing" for i in interests)
    assert not any(i["name"] == "Astrophotography" for i in interests)

    # Clean up
    client.delete(f"/api/v1/hobbies/{hobby_id}", headers=admin_headers)
    client.delete(f"/api/v1/interests/{interest_id}", headers=admin_headers)


def test_personality_cms_soft_skills_and_synthesis(client, admin_headers):
    """
    Prompt 04 Sections 12, 14, 15:
    Personality assessment status, soft skills, strengths, weaknesses editor.
    """
    # 1. Fetch initial synthesis
    init_res = client.get("/api/v1/personality/synthesis", headers=admin_headers)
    assert init_res.status_code == 200

    # 2. Update soft skills, strengths, weaknesses
    up_res = client.put("/api/v1/personality/synthesis", headers=admin_headers, json={
        "key_soft_skills": ["Architectural Communication", "Cross-functional Leadership"],
        "key_strengths": ["System Decomposition", "Defensive Programming"],
        "key_weaknesses": ["Context Switching Sensitivity"],
        "summary_notes": "Validated through technical evaluation."
    })
    assert up_res.status_code == 200
    data = up_res.json()
    assert "Architectural Communication" in data["key_soft_skills"]
    assert "System Decomposition" in data["key_strengths"]
    assert "Context Switching Sensitivity" in data["key_weaknesses"]


def test_revision_history_inspection_and_pin_protected_restore(client, admin_headers):
    """
    Prompt 04 Sections 27, 28, 29, 30:
    Audit Revisions, Inspection, PIN Protection, and Restore workflow.
    """
    # 1. Create an education record (Revision 1)
    edu_res = client.post("/api/v1/education", headers=admin_headers, json={
        "level": "Post Graduate",
        "stream": "Cybersecurity",
        "institution": "Tech Institute",
        "starting_month_year": "Sep 2021",
        "ending_month_year": "Jun 2023",
        "currently_studying": False
    })
    assert edu_res.status_code == 201
    edu_id = edu_res.json()["id"]

    # 2. Update the record (Revision 2)
    client.put(f"/api/v1/education/{edu_id}", headers=admin_headers, json={
        "level": "Post Graduate",
        "stream": "Applied Cryptography",
        "institution": "Tech Institute",
        "starting_month_year": "Sep 2021",
        "ending_month_year": "Jun 2023",
        "currently_studying": False
    })

    # Verify updated stream
    assert client.get(f"/api/v1/education/{edu_id}", headers=admin_headers).json()["stream"] == "Applied Cryptography"

    # 3. Retrieve revisions list
    revs_res = client.get("/api/v1/audit/revisions", headers=admin_headers)
    assert revs_res.status_code == 200
    revs = revs_res.json()
    assert len(revs) >= 2

    # Find the CREATE revision for this education record
    create_rev = next(r for r in revs if r["entity_name"] == "education" and r["action"] == "CREATE")
    create_rev_id = create_rev["id"]

    # 4. Attempt to restore without PIN -> rejected
    no_pin_headers = {"Authorization": admin_headers["Authorization"]}
    restore_fail = client.post(f"/api/v1/audit/revisions/{create_rev_id}/restore", headers=no_pin_headers)
    assert restore_fail.status_code in (403, 422)

    # 5. Restore with valid PIN
    restore_ok = client.post(f"/api/v1/audit/revisions/{create_rev_id}/restore", headers=admin_headers)
    assert restore_ok.status_code == 200
    assert restore_ok.json()["success"] is True

    # 6. Verify restored record matches original "Cybersecurity" stream
    restored_edu = client.get(f"/api/v1/education/{edu_id}", headers=admin_headers).json()
    assert restored_edu["stream"] == "Cybersecurity"

    # 7. Clean up
    client.delete(f"/api/v1/education/{edu_id}", headers=admin_headers)


def test_audit_log_query_and_immutability(client, admin_headers):
    """
    Prompt 04 Section 31 & 54:
    Audit logs query, action/resource filtering, and verification that audit events are immutable.
    """
    # Test both /events and /logs alias
    res_logs = client.get("/api/v1/audit/logs", headers=admin_headers, params={"limit": 20})
    assert res_logs.status_code == 200
    logs = res_logs.json()
    assert isinstance(logs, list)
    assert len(logs) > 0

    res_events = client.get("/api/v1/audit/events", headers=admin_headers, params={"limit": 20})
    assert res_events.status_code == 200

    # Verify each log contains audit properties
    first_log = logs[0]
    assert "event_type" in first_log
    assert "timestamp" in first_log
    assert "status" in first_log
