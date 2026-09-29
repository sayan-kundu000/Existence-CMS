import pytest


def test_health_check(client):
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ["healthy", "degraded"]
    assert data["project"] == "Existence"


def test_auth_and_pin_flow(client):
    # 1. Login with baseline seeded admin
    login_res = client.post("/api/v1/auth/login", json={"username": "admin", "password": "Admin@Existence2026!"})
    assert login_res.status_code == 200
    token = login_res.json()["access_token"]
    assert token is not None
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Check PIN status (already configured with 8421 in fixture)
    status_res = client.get("/api/v1/pin/status", headers=headers)
    assert status_res.status_code == 200
    assert status_res.json()["is_configured"] is True

    # 3. Verify PIN verification endpoint
    verify_res = client.post("/api/v1/pin/verify", json={"pin": "8421"}, headers=headers)
    assert verify_res.status_code == 200

    # 4. Test incorrect PIN failure
    wrong_pin_res = client.post("/api/v1/pin/verify", json={"pin": "0000"}, headers=headers)
    assert wrong_pin_res.status_code == 401


def test_profile_empty_state_and_update(client, admin_headers):
    # Public profile initially has is_empty = True
    res = client.get("/api/v1/profile")
    assert res.status_code == 200
    data = res.json()
    assert data["is_empty"] is True
    assert data["name"] is None

    # Try updating without PIN -> 403 Forbidden
    update_payload = {
        "name": "Alex Architect",
        "email_ids": ["alex@example.com"],
        "mobile_number": "+1234567890",
        "linkedin": "https://linkedin.com/in/alex",
        "about": "Systems architect and engineer"
    }
    auth_only_header = {"Authorization": admin_headers["Authorization"]}
    no_pin_res = client.put(
        "/api/v1/profile",
        json=update_payload,
        headers=auth_only_header
    )
    assert no_pin_res.status_code == 403

    # Update WITH valid PIN -> 200 OK
    upd_res = client.put("/api/v1/profile", json=update_payload, headers=admin_headers)
    assert upd_res.status_code == 200
    assert upd_res.json()["name"] == "Alex Architect"
    assert upd_res.json()["is_empty"] is False


def test_education_conditional_rules(client, admin_headers):
    # Rule 1: Currently studying = False, but ending_month_year missing -> Validation Error (422)
    invalid_edu = {
        "level": "Undergraduate",
        "stream": "Computer Science",
        "starting_month_year": "Sep 2020",
        "currently_studying": False
        # ending_month_year omitted
    }
    res = client.post("/api/v1/education", json=invalid_edu, headers=admin_headers)
    assert res.status_code == 422

    # Rule 2: Currently studying = True -> ending_month_year cleared/allowed null
    valid_studying_edu = {
        "level": "Graduate",
        "stream": "Software Engineering",
        "institution": "Polytechnic University",
        "starting_month_year": "Sep 2023",
        "currently_studying": True
    }
    res2 = client.post("/api/v1/education", json=valid_studying_edu, headers=admin_headers)
    assert res2.status_code == 201
    assert res2.json()["currently_studying"] is True
    assert res2.json()["ending_month_year"] is None


def test_experience_conditional_rules(client, admin_headers):
    # Rule 1: On-site work mode requires location
    invalid_exp = {
        "role": "Lead Architect",
        "employer": "Tech Corp",
        "work_mode": "On-site",
        "location": None,  # Should fail!
        "starting_month_year": "Jan 2022",
        "currently_working": True
    }
    res = client.post("/api/v1/experience", json=invalid_exp, headers=admin_headers)
    assert res.status_code == 422

    # Rule 2: Remote mode does not require location
    valid_remote_exp = {
        "role": "Principal Engineer",
        "employer": "Cloud Systems",
        "work_mode": "Remote",
        "starting_month_year": "Feb 2023",
        "currently_working": True
    }
    res2 = client.post("/api/v1/experience", json=valid_remote_exp, headers=admin_headers)
    assert res2.status_code == 201
    assert res2.json()["work_mode"] == "Remote"


def test_skills_seven_level_engine(client, admin_headers):
    # Rating < 1 or > 7 should fail
    bad_skill = {
        "name": "Quantum Computing",
        "category": "Advanced Tech",
        "rating": 9  # Invalid level!
    }
    res = client.post("/api/v1/skills", json=bad_skill, headers=admin_headers)
    assert res.status_code == 422

    # Rating = 7 should succeed and map to "Master"
    valid_skill = {
        "name": "System Architecture",
        "category": "Core Engineering",
        "rating": 7
    }
    res2 = client.post("/api/v1/skills", json=valid_skill, headers=admin_headers)
    assert res2.status_code == 201
    data = res2.json()
    assert data["rating"] == 7
    assert data["level_label"] == "Master"


def test_mbti_assessment_flow(client):
    start_res = client.post("/api/v1/assessments/start", json={"assessment_type": "MBTI"})
    assert start_res.status_code == 200
    start_data = start_res.json()
    session_id = start_data["session_id"]
    questions = start_data["questions"]

    answers = []
    for q in questions:
        if q["dimension"] == "EI": val = 1
        elif q["dimension"] == "SN": val = 5
        elif q["dimension"] == "TF": val = 1
        else: val = 1
        answers.append({"question_id": q["id"], "dimension": q["dimension"], "selected_value": val})

    submit_res = client.post("/api/v1/assessments/submit", json={"session_id": session_id, "answers": answers})
    assert submit_res.status_code == 200
    res_data = submit_res.json()
    assert res_data["result_code"] == "INTJ"
    assert "Architect" in res_data["result_title"]
    assert len(res_data["strengths"]) > 0


def test_disc_assessment_flow(client):
    start_res = client.post("/api/v1/assessments/start", json={"assessment_type": "DISC"})
    assert start_res.status_code == 200
    start_data = start_res.json()
    session_id = start_data["session_id"]
    questions = start_data["questions"]

    answers = []
    for q in questions:
        val = 5 if q["dimension"] == "D" else 2
        answers.append({"question_id": q["id"], "dimension": q["dimension"], "selected_value": val})

    submit_res = client.post("/api/v1/assessments/submit", json={"session_id": session_id, "answers": answers})
    assert submit_res.status_code == 200
    res_data = submit_res.json()
    assert "D" in res_data["result_code"]
    assert "Dominant" in res_data["result_title"] or "Driver" in res_data["result_title"]


def test_big_five_assessment_flow(client):
    start_res = client.post("/api/v1/assessments/start", json={"assessment_type": "BIG_FIVE"})
    assert start_res.status_code == 200
    start_data = start_res.json()
    session_id = start_data["session_id"]
    questions = start_data["questions"]

    answers = []
    for q in questions:
        val = 5 if q["dimension"] in ["O", "C"] else 3
        answers.append({"question_id": q["id"], "dimension": q["dimension"], "selected_value": val})

    submit_res = client.post("/api/v1/assessments/submit", json={"session_id": session_id, "answers": answers})
    assert submit_res.status_code == 200
    res_data = submit_res.json()
    assert "O" in res_data["result_code"]
    assert res_data["scores"]["O"] >= 80
