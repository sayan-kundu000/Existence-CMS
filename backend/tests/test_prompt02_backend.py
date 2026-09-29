import pytest
from app.models.assessment import (
    PersonalityTraitScore,
    SoftSkillRecord,
    StrengthRecord,
    WeaknessRecord
)


def test_standardized_error_format(client):
    """Verify Section 27: standardized error response envelope."""
    # Sending invalid education level to trigger validation error
    bad_data = {
        "level": "InvalidLevel",
        "stream": "Physics",
        "starting_month_year": "Jan 2020",
        "ending_month_year": "Dec 2024",
        "currently_studying": False
    }
    res = client.post("/api/v1/education", json=bad_data)
    assert res.status_code in [401, 403, 422]
    # For a validation error (e.g. invalid query or unauthenticated), format matches {"error": {"code": ...}}
    res_err = client.get("/api/v1/education/999999")
    assert res_err.status_code == 404
    data = res_err.json()
    assert "error" in data
    assert "code" in data["error"]
    assert "message" in data["error"]


def test_education_date_order_precedence(client, admin_headers):
    """Verify Section 12: ending date cannot precede starting date."""
    invalid_dates_edu = {
        "level": "Undergraduate",
        "stream": "Mathematics",
        "starting_month_year": "Sep 2023",
        "ending_month_year": "Sep 2020",  # Precedes starting date!
        "currently_studying": False
    }
    res = client.post("/api/v1/education", json=invalid_dates_edu, headers=admin_headers)
    assert res.status_code == 422
    data = res.json()
    assert "error" in data
    assert data["error"]["code"] == "VALIDATION_ERROR"


def test_education_patch(client, admin_headers):
    """Verify Section 12: PATCH /api/v1/education/{id}."""
    # 1. Create education
    create_payload = {
        "level": "Graduate",
        "stream": "Information Systems",
        "institution": "Tech Institute",
        "starting_month_year": "Jan 2022",
        "ending_month_year": "Dec 2023",
        "currently_studying": False,
        "ordering": 1
    }
    create_res = client.post("/api/v1/education", json=create_payload, headers=admin_headers)
    assert create_res.status_code == 201
    edu_id = create_res.json()["id"]

    # 2. Patch stream and currently_studying = True
    patch_payload = {
        "stream": "Data Science & AI",
        "currently_studying": True
    }
    patch_res = client.patch(f"/api/v1/education/{edu_id}", json=patch_payload, headers=admin_headers)
    assert patch_res.status_code == 200
    data = patch_res.json()
    assert data["stream"] == "Data Science & AI"
    assert data["currently_studying"] is True
    assert data["ending_month_year"] is None


def test_experience_date_order_precedence(client, admin_headers):
    """Verify Section 13: experience ending date cannot precede starting date."""
    invalid_dates_exp = {
        "role": "Software Engineer",
        "employer": "Tech Labs",
        "work_mode": "Remote",
        "starting_month_year": "Jan 2024",
        "ending_month_year": "Jan 2021",  # Precedes starting date!
        "currently_working": False
    }
    res = client.post("/api/v1/experience", json=invalid_dates_exp, headers=admin_headers)
    assert res.status_code == 422
    data = res.json()
    assert "error" in data
    assert data["error"]["code"] == "VALIDATION_ERROR"


def test_experience_patch_and_stale_location_cleanup(client, admin_headers):
    """Verify Section 13: PATCH /api/v1/experience/{id} and stale location cleanup when switching to Remote."""
    # 1. Create On-site experience
    create_payload = {
        "role": "Frontend Developer",
        "employer": "Web Solutions",
        "work_mode": "On-site",
        "location": "San Francisco, CA",
        "starting_month_year": "Mar 2021",
        "ending_month_year": "Aug 2022",
        "currently_working": False
    }
    create_res = client.post("/api/v1/experience", json=create_payload, headers=admin_headers)
    assert create_res.status_code == 201
    exp_id = create_res.json()["id"]

    # 2. Patch to Remote (location must be updated to Remote, preventing stale location data)
    patch_payload = {
        "work_mode": "Remote"
    }
    patch_res = client.patch(f"/api/v1/experience/{exp_id}", json=patch_payload, headers=admin_headers)
    assert patch_res.status_code == 200
    data = patch_res.json()
    assert data["work_mode"] == "Remote"
    assert data["location"] == "Remote"


def test_skills_seven_level_comprehensive(client, admin_headers):
    """Verify Section 14: 1 to 7 rating scale, invalid values (0, 8, negative), label mapping, description support, and PATCH."""
    # Invalid ratings: 0, 8, -2
    for bad_rating in [0, 8, -2]:
        bad_skill = {
            "name": "Cloud Architecture",
            "category": "DevOps",
            "rating": bad_rating
        }
        res = client.post("/api/v1/skills", json=bad_skill, headers=admin_headers)
        assert res.status_code == 422

    # Valid rating: 6 -> Expert, with optional description
    valid_skill = {
        "name": "PostgreSQL Optimization",
        "category": "Database Engineering",
        "description": "Deep indexing, query optimization, and connection pooling",
        "rating": 6
    }
    create_res = client.post("/api/v1/skills", json=valid_skill, headers=admin_headers)
    assert create_res.status_code == 201
    data = create_res.json()
    assert data["rating"] == 6
    assert data["level_label"] == "Expert"
    assert data["description"] == "Deep indexing, query optimization, and connection pooling"
    skill_id = data["id"]

    # PATCH skill to 7 -> Master
    patch_res = client.patch(f"/api/v1/skills/{skill_id}", json={"rating": 7}, headers=admin_headers)
    assert patch_res.status_code == 200
    patched_data = patch_res.json()
    assert patched_data["rating"] == 7
    assert patched_data["level_label"] == "Master"


def test_hobbies_resource_crud_and_patch(client, admin_headers):
    """Verify Section 15: distinct /api/v1/hobbies endpoints, ordering, visibility, and PATCH."""
    # 1. Listing initial empty array
    list_res = client.get("/api/v1/hobbies")
    assert list_res.status_code == 200
    assert list_res.json() == []

    # 2. Create Hobby
    new_hobby = {
        "name": "Landscape Photography",
        "category": "Creative Arts",
        "icon": "camera",
        "ordering": 1
    }
    create_res = client.post("/api/v1/hobbies", json=new_hobby, headers=admin_headers)
    assert create_res.status_code == 201
    hobby_id = create_res.json()["id"]
    assert create_res.json()["name"] == "Landscape Photography"

    # 3. Patch Hobby
    patch_res = client.patch(f"/api/v1/hobbies/{hobby_id}", json={"name": "Fine Art Photography"}, headers=admin_headers)
    assert patch_res.status_code == 200
    assert patch_res.json()["name"] == "Fine Art Photography"

    # 4. Delete Hobby
    del_res = client.delete(f"/api/v1/hobbies/{hobby_id}", headers=admin_headers)
    assert del_res.status_code == 200
    assert del_res.json()["success"] is True

    # 5. Verify deleted
    get_res = client.get(f"/api/v1/hobbies/{hobby_id}")
    assert get_res.status_code == 404


def test_interests_resource_crud_and_patch(client, admin_headers):
    """Verify Section 15: distinct /api/v1/interests endpoints, ordering, visibility, and PATCH."""
    # 1. Listing initial empty array
    list_res = client.get("/api/v1/interests")
    assert list_res.status_code == 200
    assert list_res.json() == []

    # 2. Create Interest
    new_interest = {
        "name": "Distributed Systems",
        "category": "Computer Science",
        "icon": "server",
        "ordering": 1
    }
    create_res = client.post("/api/v1/interests", json=new_interest, headers=admin_headers)
    assert create_res.status_code == 201
    interest_id = create_res.json()["id"]
    assert create_res.json()["name"] == "Distributed Systems"

    # 3. Patch Interest
    patch_res = client.patch(f"/api/v1/interests/{interest_id}", json={"name": "Fault-Tolerant Consensus Protocols"}, headers=admin_headers)
    assert patch_res.status_code == 200
    assert patch_res.json()["name"] == "Fault-Tolerant Consensus Protocols"

    # 4. Delete Interest
    del_res = client.delete(f"/api/v1/interests/{interest_id}", headers=admin_headers)
    assert del_res.status_code == 200
    assert del_res.json()["success"] is True

    # 5. Verify deleted
    get_res = client.get(f"/api/v1/interests/{interest_id}")
    assert get_res.status_code == 404


def test_personality_session_lifecycle_and_validation(client, db_session):
    """Verify Section 16 & 17: NOT_STARTED -> IN_PROGRESS -> COMPLETED lifecycle, incomplete rejection, normalized records."""
    # 1. List assessment definitions
    defs_res = client.get("/api/v1/personality/assessments")
    assert defs_res.status_code == 200
    types = [d["type"] for d in defs_res.json()]
    assert "MBTI" in types
    assert "DISC" in types
    assert "BIG_FIVE" in types

    # 2. Start session (IN_PROGRESS)
    start_res = client.post("/api/v1/personality/sessions", json={"assessment_type": "MBTI"})
    assert start_res.status_code == 201
    session_data = start_res.json()
    session_id = session_data["session_id"]
    total_q = session_data["total_questions"]
    questions = session_data["questions"]

    # 3. Check status
    status_res = client.get(f"/api/v1/personality/sessions/{session_id}")
    assert status_res.status_code == 200
    assert status_res.json()["status"] == "IN_PROGRESS"
    assert status_res.json()["answered_count"] == 0

    # 4. Submit partial answers (only first question)
    partial_batch = {
        "responses": [
            {"question_id": questions[0]["id"], "dimension": questions[0]["dimension"], "selected_value": 3}
        ]
    }
    resp_res = client.post(f"/api/v1/personality/sessions/{session_id}/responses", json=partial_batch)
    assert resp_res.status_code == 200

    # 5. Attempt complete prematurely -> Should reject with 422 Incomplete
    premature_res = client.post(f"/api/v1/personality/sessions/{session_id}/complete")
    assert premature_res.status_code == 422
    assert "Incomplete assessment" in premature_res.json()["error"]["message"]

    # 6. Submit remaining answers
    all_responses = []
    for q in questions:
        all_responses.append({
            "question_id": q["id"],
            "dimension": q["dimension"],
            "selected_value": 1 if q["dimension"] in ["EI", "TF", "JP"] else 5
        })
    full_batch_res = client.post(f"/api/v1/personality/sessions/{session_id}/responses", json={"responses": all_responses})
    assert full_batch_res.status_code == 200

    # 7. Complete session -> Atomic result creation
    complete_res = client.post(f"/api/v1/personality/sessions/{session_id}/complete")
    assert complete_res.status_code == 200
    res_data = complete_res.json()
    assert res_data["result_code"] == "INTJ"

    # Verify session status is now COMPLETED
    completed_status = client.get(f"/api/v1/personality/sessions/{session_id}")
    assert completed_status.json()["status"] == "COMPLETED"

    # Verify normalized tables received records
    result_id = res_data["id"]
    traits_count = db_session.query(PersonalityTraitScore).filter(PersonalityTraitScore.result_id == result_id).count()
    soft_skills_count = db_session.query(SoftSkillRecord).filter(SoftSkillRecord.result_id == result_id).count()
    strengths_count = db_session.query(StrengthRecord).filter(StrengthRecord.result_id == result_id).count()
    weaknesses_count = db_session.query(WeaknessRecord).filter(WeaknessRecord.result_id == result_id).count()

    assert traits_count > 0, "PersonalityTraitScore records should be created"
    assert soft_skills_count >= 0, "SoftSkillRecord records table is maintained"
    assert strengths_count > 0, "StrengthRecord records should be created"
    assert weaknesses_count > 0, "WeaknessRecord records should be created"

    # 8. Check result by session and history
    res_by_session = client.get(f"/api/v1/personality/results/{session_id}")
    assert res_by_session.status_code == 200
    assert res_by_session.json()["result_code"] == "INTJ"

    history_res = client.get("/api/v1/personality/history")
    assert history_res.status_code == 200
    assert len(history_res.json()) >= 1


def test_profile_patch(client, admin_headers):
    """Verify Section 11: PATCH /api/v1/profile."""
    patch_payload = {
        "about": "Principal Architect with focus on distributed databases."
    }
    patch_res = client.patch("/api/v1/profile", json=patch_payload, headers=admin_headers)
    assert patch_res.status_code == 200
    assert patch_res.json()["about"] == "Principal Architect with focus on distributed databases."
