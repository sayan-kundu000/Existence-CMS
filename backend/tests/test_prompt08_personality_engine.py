import pytest
from fastapi.testclient import TestClient
from app.models.assessment import (
    AssessmentSession,
    AssessmentResponse,
    AssessmentResult,
    PersonalityTraitScore,
    PersonalitySynthesis
)
from app.data.question_banks import QUESTION_BANKS
from app.services.personality_scoring import (
    MbtiScoringStrategy,
    DiscScoringStrategy,
    OceanScoringStrategy,
    ScoringStrategyFactory,
    compare_assessment_results,
    synthesize_personality
)
from app.schemas.assessment import ResponseAnswerItem


def test_01_scoring_strategy_factory_and_mbti():
    """Verify scoring strategy factory and MBTI 4-letter cognitive calculation."""
    strategy = ScoringStrategyFactory.get_strategy("MBTI")
    assert isinstance(strategy, MbtiScoringStrategy)

    # Synthetic answers favoring INTJ: I (EI=1), N (SN=5), T (TF=1), J (JP=1)
    answers = [
        ResponseAnswerItem(question_id="mbti_q1", dimension="EI", selected_value=1),
        ResponseAnswerItem(question_id="mbti_q2", dimension="SN", selected_value=5),
        ResponseAnswerItem(question_id="mbti_q3", dimension="TF", selected_value=1),
        ResponseAnswerItem(question_id="mbti_q4", dimension="JP", selected_value=1),
    ]
    result = strategy.score(answers)
    assert result["result_code"] == "INTJ"
    assert "Architect" in result["result_title"]
    assert len(result["strengths"]) > 0
    assert len(result["weaknesses"]) > 0
    # Strict domain separation: soft skills are empty in assessment output
    assert result["soft_skills"] == []


def test_02_disc_and_ocean_scoring():
    """Verify DISC primary/secondary calculation and Big Five OCEAN scores."""
    # DISC: High D (5), moderate I (4), low S (1), low C (2)
    disc_strat = ScoringStrategyFactory.get_strategy("DISC")
    disc_answers = [
        ResponseAnswerItem(question_id="d1", dimension="D", selected_value=5),
        ResponseAnswerItem(question_id="i1", dimension="I", selected_value=4),
        ResponseAnswerItem(question_id="s1", dimension="S", selected_value=1),
        ResponseAnswerItem(question_id="c1", dimension="C", selected_value=2),
    ]
    disc_res = disc_strat.score(disc_answers)
    assert disc_res["result_code"].startswith("D")
    assert "percentages" in disc_res["scores"]
    assert disc_res["scores"]["percentages"]["D"] == 100
    assert disc_res["scores"]["percentages"]["I"] == 75

    # Big Five: All dimensions
    ocean_strat = ScoringStrategyFactory.get_strategy("BIG_FIVE")
    ocean_answers = [
        ResponseAnswerItem(question_id="o1", dimension="O", selected_value=4),
        ResponseAnswerItem(question_id="c1", dimension="C", selected_value=5),
        ResponseAnswerItem(question_id="e1", dimension="E", selected_value=3),
        ResponseAnswerItem(question_id="a1", dimension="A", selected_value=4),
        ResponseAnswerItem(question_id="n1", dimension="N", selected_value=2),
    ]
    ocean_res = ocean_strat.score(ocean_answers)
    assert "O75-C100-E50-A75-N25" in ocean_res["result_code"]
    assert ocean_res["scores"]["C"] == 100
    assert ocean_res["scores"]["N"] == 25


def test_03_result_comparison_utility():
    """Verify dimension deltas, shift directions, and non-judgmental interpretations."""
    baseline = {
        "assessment_type": "MBTI",
        "session_id": "session-base-001",
        "result_code": "INTJ",
        "scores": {
            "dimensions": {
                "Extraversion": 20.0,
                "Introversion": 80.0,
                "Sensing": 30.0,
                "Intuition": 70.0,
                "Thinking": 75.0,
                "Feeling": 25.0,
                "Judging": 80.0,
                "Perceiving": 20.0
            }
        },
        "completed_at": "2026-09-01T10:00:00Z"
    }

    target = {
        "assessment_type": "MBTI",
        "session_id": "session-targ-002",
        "result_code": "ENTJ",
        "scores": {
            "dimensions": {
                "Extraversion": 60.0,
                "Introversion": 40.0,
                "Sensing": 30.0,
                "Intuition": 70.0,
                "Thinking": 85.0,
                "Feeling": 15.0,
                "Judging": 70.0,
                "Perceiving": 30.0
            }
        },
        "completed_at": "2026-09-30T10:00:00Z"
    }

    comp = compare_assessment_results(baseline, target)
    assert comp["assessment_type"] == "MBTI"
    assert comp["baseline_result_code"] == "INTJ"
    assert comp["target_result_code"] == "ENTJ"

    e_comp = next(d for d in comp["dimensions_comparison"] if d["dimension"] == "Extraversion")
    assert e_comp["delta"] == 40.0
    assert e_comp["direction"] == "INCREASED"

    i_comp = next(d for d in comp["dimensions_comparison"] if d["dimension"] == "Introversion")
    assert i_comp["delta"] == -40.0
    assert i_comp["direction"] == "DECREASED"


def test_04_session_lifecycle_resume_and_progress(client: TestClient):
    """Verify starting session, saving answers, resuming, and tracking progress index."""
    # 1. Start MBTI session
    start_res = client.post("/api/v1/personality/sessions", json={"assessment_type": "MBTI"})
    assert start_res.status_code == 201
    s_data = start_res.json()
    session_id = s_data["session_id"]
    total_q = s_data["total_questions"]
    assert total_q == 75

    # 2. Save partial answers (first 3 questions)
    q1 = s_data["questions"][0]
    q2 = s_data["questions"][1]
    q3 = s_data["questions"][2]

    save_res = client.post(
        f"/api/v1/personality/sessions/{session_id}/responses",
        json={
            "responses": [
                {"question_id": q1["id"], "dimension": q1["dimension"], "selected_value": 4},
                {"question_id": q2["id"], "dimension": q2["dimension"], "selected_value": 5},
                {"question_id": q3["id"], "dimension": q3["dimension"], "selected_value": 2}
            ]
        }
    )
    assert save_res.status_code == 200
    assert save_res.json()["saved_count"] == 3

    # 3. Update progress index to question 3
    prog_res = client.patch(
        f"/api/v1/personality/sessions/{session_id}/progress",
        json={"progress_index": 3}
    )
    assert prog_res.status_code == 200
    assert prog_res.json()["progress_index"] == 3

    # 4. Resume session and verify state
    resume_res = client.get(f"/api/v1/personality/sessions/{session_id}/resume")
    assert resume_res.status_code == 200
    r_data = resume_res.json()
    assert r_data["session_id"] == session_id
    assert r_data["progress_index"] == 3
    assert r_data["answered_count"] == 3
    assert r_data["answers"][q1["id"]] == 4
    assert r_data["answers"][q2["id"]] == 5
    assert r_data["answers"][q3["id"]] == 2
    assert r_data["assessment_version"] == "1.0"


def test_05_incomplete_completion_rejected(client: TestClient):
    """Verify that attempting to complete an assessment before all required questions are answered is rejected with 422."""
    start_res = client.post("/api/v1/personality/sessions", json={"assessment_type": "DISC"})
    assert start_res.status_code == 201
    session_id = start_res.json()["session_id"]

    # Only answer 1 question out of 43
    q = start_res.json()["questions"][0]
    client.post(
        f"/api/v1/personality/sessions/{session_id}/responses",
        json={"responses": [{"question_id": q["id"], "dimension": q["dimension"], "selected_value": 3}]}
    )

    complete_res = client.post(f"/api/v1/personality/sessions/{session_id}/complete")
    assert complete_res.status_code == 422
    err_body = complete_res.json()
    message = err_body.get("error", {}).get("message", "") or err_body.get("detail", "")
    assert "Incomplete assessment" in message


def test_06_complete_session_atomic_trait_scores_and_version(client: TestClient, db_session):
    """Verify full test session completion, transactional persistence of trait scores, and version locking."""
    start_res = client.post("/api/v1/personality/sessions", json={"assessment_type": "MBTI"})
    assert start_res.status_code == 201
    s_data = start_res.json()
    session_id = s_data["session_id"]
    questions = s_data["questions"]

    # Provide all 43 responses
    batch_responses = [
        {"question_id": q["id"], "dimension": q["dimension"], "selected_value": 4 if i % 2 == 0 else 2}
        for i, q in enumerate(questions)
    ]
    client.post(
        f"/api/v1/personality/sessions/{session_id}/responses",
        json={"responses": batch_responses}
    )

    # Complete session
    comp_res = client.post(f"/api/v1/personality/sessions/{session_id}/complete")
    assert comp_res.status_code == 200
    res_data = comp_res.json()
    assert res_data["session_id"] == session_id
    assert res_data["assessment_type"] == "MBTI"
    assert len(res_data["result_code"]) == 4
    assert res_data["result_version"] == "1.0"
    assert res_data["is_public"] is True

    # Verify trait scores were persisted in database
    db_result = db_session.query(AssessmentResult).filter(AssessmentResult.session_id == session_id).first()
    assert db_result is not None
    assert db_result.result_version == "1.0"
    trait_scores = db_session.query(PersonalityTraitScore).filter(PersonalityTraitScore.result_id == db_result.id).all()
    assert len(trait_scores) == 8  # 8 MBTI dimensions (Extraversion, Introversion, Sensing, etc.)


def test_07_public_vs_private_result_visibility(client: TestClient, admin_headers: dict):
    """Verify result visibility toggle and boundary protection in public endpoint."""
    # 1. Complete a test session
    start_res = client.post("/api/v1/personality/sessions", json={"assessment_type": "DISC"})
    session_id = start_res.json()["session_id"]
    questions = start_res.json()["questions"]

    batch_responses = [
        {"question_id": q["id"], "dimension": q["dimension"], "selected_value": 4}
        for q in questions
    ]
    client.post(f"/api/v1/personality/sessions/{session_id}/responses", json={"responses": batch_responses})
    comp_res = client.post(f"/api/v1/personality/sessions/{session_id}/complete")
    result_id = comp_res.json()["id"]

    # Result is public by default
    pub_res = client.get("/api/v1/personality/public")
    assert pub_res.status_code == 200
    assert pub_res.json()["has_assessments"] is True
    assert "DISC" in pub_res.json()["assessments_completed"]

    # 2. Toggle visibility to private (requires PIN)
    toggle_res = client.patch(
        f"/api/v1/personality/results/{result_id}/visibility",
        json={"is_public": False},
        headers=admin_headers
    )
    assert toggle_res.status_code == 200
    assert toggle_res.json()["is_public"] is False

    # 3. Check public endpoint again: private result is excluded
    pub_res2 = client.get("/api/v1/personality/public")
    assert pub_res2.status_code == 200
    assert pub_res2.json()["latest_results"]["DISC"] is None

    # Toggle back to public
    client.patch(
        f"/api/v1/personality/results/{result_id}/visibility",
        json={"is_public": True},
        headers=admin_headers
    )


def test_08_comparison_endpoint(client: TestClient):
    """Verify GET /api/v1/personality/compare endpoint between two completed attempts."""
    # Attempt 1
    s1 = client.post("/api/v1/personality/sessions", json={"assessment_type": "DISC"}).json()
    b1 = [{"question_id": q["id"], "dimension": q["dimension"], "selected_value": 5 if q["dimension"] == "D" else 1} for q in s1["questions"]]
    client.post(f"/api/v1/personality/sessions/{s1['session_id']}/responses", json={"responses": b1})
    client.post(f"/api/v1/personality/sessions/{s1['session_id']}/complete")

    # Attempt 2
    s2 = client.post("/api/v1/personality/sessions", json={"assessment_type": "DISC"}).json()
    b2 = [{"question_id": q["id"], "dimension": q["dimension"], "selected_value": 2 if q["dimension"] == "D" else 5} for q in s2["questions"]]
    client.post(f"/api/v1/personality/sessions/{s2['session_id']}/responses", json={"responses": b2})
    client.post(f"/api/v1/personality/sessions/{s2['session_id']}/complete")

    # Call compare endpoint
    comp_res = client.get(f"/api/v1/personality/compare?baseline_session_id={s1['session_id']}&target_session_id={s2['session_id']}")
    assert comp_res.status_code == 200
    data = comp_res.json()
    assert data["assessment_type"] == "DISC"
    assert len(data["dimensions_comparison"]) == 4
    dom_comp = next(d for d in data["dimensions_comparison"] if d["dimension"] == "Dominance")
    assert dom_comp["direction"] == "DECREASED"


def test_09_pin_protection_on_synthesis_and_deletion(client: TestClient, admin_headers: dict):
    """Verify that updating synthesis or deleting results requires valid PIN verification."""
    headers_without_pin = {k: v for k, v in admin_headers.items() if k != "X-Action-PIN"}

    # 1. Update synthesis without PIN -> 403/401
    bad_res = client.put(
        "/api/v1/personality/synthesis",
        json={"key_soft_skills": [], "key_strengths": ["Communication"], "key_weaknesses": []},
        headers=headers_without_pin
    )
    assert bad_res.status_code in (401, 403)
    err_msg = bad_res.json().get("error", {}).get("message", "") or bad_res.json().get("detail", "")
    assert "PIN" in err_msg or "pin" in err_msg

    # With PIN -> 200
    good_res = client.put(
        "/api/v1/personality/synthesis",
        json={"key_soft_skills": [], "key_strengths": ["Communication"], "key_weaknesses": []},
        headers=admin_headers
    )
    assert good_res.status_code == 200

    # 2. Delete result without PIN -> 403/401
    # Create session to delete
    s = client.post("/api/v1/personality/sessions", json={"assessment_type": "BIG_FIVE"}).json()
    b = [{"question_id": q["id"], "dimension": q["dimension"], "selected_value": 3} for q in s["questions"]]
    client.post(f"/api/v1/personality/sessions/{s['session_id']}/responses", json={"responses": b})
    r = client.post(f"/api/v1/personality/sessions/{s['session_id']}/complete").json()

    del_bad = client.delete(f"/api/v1/personality/results/{r['id']}", headers=headers_without_pin)
    assert del_bad.status_code in (401, 403)

    del_good = client.delete(f"/api/v1/personality/results/{r['id']}", headers=admin_headers)
    assert del_good.status_code == 200
    assert del_good.json()["success"] is True


def test_10_administrative_definitions_questions_and_stats(client: TestClient, admin_headers: dict):
    """Verify administrative assessment definition, question bank management, and statistics."""
    headers_without_pin = {k: v for k, v in admin_headers.items() if k != "X-Action-PIN"}

    # 1. Stats endpoint
    stats_res = client.get("/api/v1/personality/admin/stats")
    assert stats_res.status_code == 200
    stats = stats_res.json()
    assert "total_sessions" in stats
    assert "models" in stats
    assert "MBTI" in stats["models"]

    # 2. List definitions
    defs_res = client.get("/api/v1/personality/admin/definitions")
    assert defs_res.status_code == 200
    defs = defs_res.json()
    assert isinstance(defs, list)
    assert len(defs) >= 3

    # 3. Create definition/version (MBTI v2.0)
    new_def_payload = {
        "code": "MBTI",
        "name": "Myers-Briggs Type Indicator v2",
        "version": "2.0",
        "tagline": "Next-generation cognitive assessment",
        "question_count": 4,
        "estimated_minutes": 5,
        "status": "DRAFT"
    }
    # Without PIN -> 403
    p_bad = client.post("/api/v1/personality/admin/definitions", json=new_def_payload, headers=headers_without_pin)
    assert p_bad.status_code in (401, 403)

    # With PIN -> 201
    p_good = client.post("/api/v1/personality/admin/definitions", json=new_def_payload, headers=admin_headers)
    assert p_good.status_code == 201
    new_def = p_good.json()
    assert new_def["code"] == "MBTI"
    assert new_def["version"] == "2.0"
    assert new_def["status"] == "DRAFT"
    new_def_id = new_def["id"]

    # 4. Status update (Publish version)
    status_bad = client.patch(
        f"/api/v1/personality/admin/definitions/{new_def_id}/status",
        json={"status": "PUBLISHED"},
        headers=headers_without_pin
    )
    assert status_bad.status_code in (401, 403)

    status_good = client.patch(
        f"/api/v1/personality/admin/definitions/{new_def_id}/status",
        json={"status": "PUBLISHED"},
        headers=admin_headers
    )
    assert status_good.status_code == 200
    assert status_good.json()["status"] == "PUBLISHED"
    assert status_good.json()["is_active"] is True

    # 5. Question bank management: Add question
    new_q_payload = {
        "id": "mbti_v2_q1",
        "assessment_definition_id": new_def_id,
        "definition_type": "MBTI",
        "dimension": "EI",
        "question_text": "I feel energised in vibrant dynamic group environments.",
        "positive_pole": "Extraversion",
        "negative_pole": "Introversion",
        "scale_type": "likert_5",
        "question_order": 1,
        "scoring_configuration": "{}"
    }
    q_bad = client.post("/api/v1/personality/admin/questions", json=new_q_payload, headers=headers_without_pin)
    assert q_bad.status_code in (401, 403)

    q_good = client.post("/api/v1/personality/admin/questions", json=new_q_payload, headers=admin_headers)
    assert q_good.status_code == 201
    q_data = q_good.json()
    assert q_data["id"] == "mbti_v2_q1"
    assert q_data["is_active"] is True

    # 6. Question update
    q_edit = client.put(
        f"/api/v1/personality/admin/questions/{q_data['id']}",
        json={"question_text": "I feel energized after high-bandwidth collaboration sessions."},
        headers=admin_headers
    )
    assert q_edit.status_code == 200
    assert "high-bandwidth" in q_edit.json()["question_text"]

    # 7. Question active toggle
    toggle_res = client.patch(
        f"/api/v1/personality/admin/questions/{q_data['id']}/toggle",
        headers=admin_headers
    )
    assert toggle_res.status_code == 200
    assert toggle_res.json()["is_active"] is False


def test_11_synthesis_scales_with_number_of_tests_given():
    """
    Verify that strengths & weaknesses evaluation strictly scales with the number of tests given:
    - 0 tests: empty lists, assessment not completed
    - 1 test: evaluated strictly on the basis of that 1 test (no mandatory Communication)
    - 2 tests: evaluated strictly on the basis of those 2 tests (no mandatory Communication)
    - 3 tests: evaluated strictly on the basis of those 3 tests (exactly 11 core strengths)
    - Communication is NOT shown or forced as a mandatory core strength.
    """
    # Synthetic test outputs
    mbti_mock = {
        "result_code": "INTJ",
        "result_title": "Architect",
        "strengths": ["Strategic conceptual architecture", "Autonomous deep work focus"],
        "weaknesses": ["May delay speaking up in rapid unstructured meetings"]
    }
    disc_mock = {
        "result_code": "DI",
        "result_title": "Driver Inspirer",
        "strengths": ["Decisive problem-solving and focus on measurable milestones"],
        "weaknesses": ["Can experience frustration with prolonged administrative delays"]
    }
    big_five_mock = {
        "result_code": "O80-C85-E60-A70-N30",
        "result_title": "High Openness · High Conscientiousness",
        "strengths": ["High openness to pioneering concepts and multidisciplinary innovation"],
        "weaknesses": ["Risk of overcomplicating straightforward tasks with exploratory ideas"]
    }

    # Case 0: 0 tests given
    s0, str0, wk0, sum0 = synthesize_personality()
    assert s0 == []
    assert str0 == []
    assert wk0 == []
    assert "not yet completed" in sum0.lower()

    # Case 1: 1 test given (e.g. MBTI)
    s1, str1, wk1, sum1 = synthesize_personality(mbti=mbti_mock)
    assert s1 == []
    assert len(str1) == 2
    assert "Communication" not in str1
    assert "Strategic conceptual architecture" in str1
    assert "Autonomous deep work focus" in str1
    assert "Decisive problem-solving and focus on measurable milestones" not in str1
    assert wk1 == ["May delay speaking up in rapid unstructured meetings"]
    assert sum1.startswith("Evaluated on the basis of 1 completed assessment")
    assert "MBTI: INTJ (Architect)" in sum1
    assert "DISC:" not in sum1

    # Case 2: 2 tests given (e.g. MBTI + DISC)
    s2, str2, wk2, sum2 = synthesize_personality(mbti=mbti_mock, disc=disc_mock)
    assert s2 == []
    assert len(str2) == 3
    assert "Communication" not in str2
    assert "Strategic conceptual architecture" in str2
    assert "Decisive problem-solving and focus on measurable milestones" in str2
    assert "High openness to pioneering concepts and multidisciplinary innovation" not in str2
    assert "May delay speaking up in rapid unstructured meetings" in wk2
    assert "Can experience frustration with prolonged administrative delays" in wk2
    assert sum2.startswith("Evaluated on the basis of 2 completed assessments")
    assert "MBTI: INTJ (Architect)" in sum2
    assert "DISC: DI (Driver Inspirer)" in sum2
    assert "Big Five:" not in sum2

    # Case 3: 3 tests given (MBTI + DISC + Big Five) -> Exactly 11 core strengths
    s3, str3, wk3, sum3 = synthesize_personality(mbti=mbti_mock, disc=disc_mock, big_five=big_five_mock)
    assert s3 == []
    assert len(str3) == 11, f"Expected exactly 11 core strengths, got {len(str3)}"
    assert str3[0] == "Strategic conceptual architecture"
    assert "Decisive problem-solving and focus on measurable milestones" in str3
    assert "High openness to pioneering concepts and multidisciplinary innovation" in str3
    assert "May delay speaking up in rapid unstructured meetings" in wk3
    assert "Can experience frustration with prolonged administrative delays" in wk3
    assert "Risk of overcomplicating straightforward tasks with exploratory ideas" in wk3
    assert sum3.startswith("Evaluated on the basis of 3 completed assessments")
    assert "MBTI: INTJ (Architect)" in sum3
    assert "DISC: DI (Driver Inspirer)" in sum3
    assert "Big Five: High Openness · High Conscientiousness" in sum3


def test_12_synthesis_refresh_endpoint(client: TestClient):
    """Verify POST /api/v1/personality/synthesis/refresh recalculates synthesis dynamically."""
    ref_res = client.post("/api/v1/personality/synthesis/refresh")
    assert ref_res.status_code == 200
    data = ref_res.json()
    assert "has_assessments" in data
    assert "key_strengths" in data
    assert "key_weaknesses" in data
    assert "assessments_completed" in data


