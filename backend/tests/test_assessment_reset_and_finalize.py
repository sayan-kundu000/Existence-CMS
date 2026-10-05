import pytest
from app.models.assessment import AssessmentResult, AssessmentSession, PersonalitySynthesis
from app.data.question_banks import QUESTION_BANKS


def test_finalize_and_take_out_results_mbti(client, admin_headers, db_session):
    """Verify finalizing an assessment session produces valid psychometric results without error."""
    # 1. Start assessment
    start_res = client.post(
        "/api/v1/assessments/start",
        json={"assessment_type": "MBTI"},
        headers=admin_headers
    )
    assert start_res.status_code == 200, start_res.text
    session_data = start_res.json()
    session_id = session_data["session_id"]
    questions = session_data["questions"]
    assert len(questions) == 75, f"Expected 75 questions, got {len(questions)}"

    # 2. Finalize & Submit responses
    answers = [
        {"question_id": q["id"], "dimension": q["dimension"], "selected_value": 4}
        for q in questions
    ]
    submit_res = client.post(
        "/api/v1/assessments/submit",
        json={"session_id": session_id, "answers": answers},
        headers=admin_headers
    )
    assert submit_res.status_code == 200, submit_res.text
    result = submit_res.json()
    assert result["assessment_type"] == "MBTI"
    assert result["result_code"] is not None
    assert "dimensions" in result["scores"]
    assert len(result["strengths"]) > 0
    assert len(result["weaknesses"]) > 0

    # 3. Retrieve ("take out") result by session_id
    get_res = client.get(f"/api/v1/assessments/results/{session_id}")
    assert get_res.status_code == 200
    assert get_res.json()["id"] == result["id"]


def test_admin_contact_change_resets_all_assessments(client, admin_headers, db_session):
    """
    Verify that assessment tests are strictly for the admin, and changing
    email, mobile number, or linkedin account automatically resets all assessment results.
    """
    # 1. Complete an assessment first to establish results
    start_res = client.post(
        "/api/v1/assessments/start",
        json={"assessment_type": "DISC"},
        headers=admin_headers
    )
    session_id = start_res.json()["session_id"]
    questions = start_res.json()["questions"]
    assert len(questions) == 75

    answers = [
        {"question_id": q["id"], "dimension": q["dimension"], "selected_value": 5}
        for q in questions
    ]
    submit_res = client.post(
        "/api/v1/assessments/submit",
        json={"session_id": session_id, "answers": answers},
        headers=admin_headers
    )
    assert submit_res.status_code == 200
    assert db_session.query(AssessmentResult).count() == 1

    # 2. Change admin mobile number -> must trigger assessment reset
    upd_mobile_res = client.put(
        "/api/v1/profile",
        json={
            "name": "Admin User",
            "mobile_number": "+1987654321",
            "linkedin": "https://linkedin.com/in/admin",
            "about": "Updated about narrative"
        },
        headers=admin_headers
    )
    assert upd_mobile_res.status_code == 200
    assert upd_mobile_res.json()["assessments_reset"] is True
    # Verify results are purged
    assert db_session.query(AssessmentResult).count() == 0
    assert db_session.query(AssessmentSession).count() == 0

    # 3. Complete another assessment
    start_b5 = client.post(
        "/api/v1/assessments/start",
        json={"assessment_type": "BIG_FIVE"},
        headers=admin_headers
    )
    s_b5_id = start_b5.json()["session_id"]
    q_b5 = start_b5.json()["questions"]
    assert len(q_b5) == 75

    sub_b5 = client.post(
        "/api/v1/assessments/submit",
        json={
            "session_id": s_b5_id,
            "answers": [{"question_id": q["id"], "dimension": q["dimension"], "selected_value": 3} for q in q_b5]
        },
        headers=admin_headers
    )
    assert sub_b5.status_code == 200
    assert db_session.query(AssessmentResult).count() == 1

    # 4. Change admin linkedin -> must trigger assessment reset
    upd_li_res = client.put(
        "/api/v1/profile",
        json={
            "name": "Admin User",
            "mobile_number": "+1987654321",
            "linkedin": "https://linkedin.com/in/new-linkedin-profile",
            "about": "Updated about narrative"
        },
        headers=admin_headers
    )
    assert upd_li_res.status_code == 200
    assert upd_li_res.json()["assessments_reset"] is True
    assert db_session.query(AssessmentResult).count() == 0

    # 5. Add / Change email -> must trigger assessment reset
    email_add_res = client.post(
        "/api/v1/profile/emails",
        json={
            "email": "newadmin@example.com",
            "label": "Work",
            "is_primary": False,
            "is_public": True,
            "display_order": 2
        },
        headers=admin_headers
    )
    assert email_add_res.status_code == 201
    assert email_add_res.json()["assessments_reset"] is True
    assert db_session.query(AssessmentResult).count() == 0
