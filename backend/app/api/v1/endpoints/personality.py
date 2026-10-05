import json
from typing import List, Optional, Dict
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.assessment import (
    AssessmentDefinition,
    AssessmentQuestion,
    AssessmentSession,
    AssessmentResponse,
    AssessmentResult,
    PersonalitySynthesis
)
from app.models.user import User
from app.data.question_banks import ASSESSMENT_REGISTRY, QUESTION_BANKS
from app.schemas.assessment import (
    AssessmentMeta,
    SessionStartRequest,
    SessionStartResponse,
    SessionStatusOut,
    SessionResumeOut,
    ResultVisibilityUpdate,
    ResultComparisonOut,
    ResponseAnswerItem,
    BatchResponsesRequest,
    AssessmentResultOut,
    QuestionItem,
    PersonalitySynthesisOut,
    SynthesisUpdateRequest,
    AssessmentDefinitionOut,
    AssessmentDefinitionCreate,
    AssessmentDefinitionStatusUpdate,
    AssessmentQuestionOut,
    AssessmentQuestionCreate,
    AssessmentQuestionUpdate,
    AssessmentStatsOut
)
from app.repositories.assessment_repository import AssessmentRepository
from app.services.personality_scoring import (
    score_mbti,
    score_disc,
    score_big_five,
    compare_assessment_results
)
from app.api.v1.endpoints.assessments import result_to_dict, refresh_synthesis
from app.api.deps import require_pin_verification
from app.services.audit_service import log_audit_event, record_content_revision

router = APIRouter()


# ---------------------------------------------------------------------------
# Assessment Definitions & Discovery
# ---------------------------------------------------------------------------

@router.get("/assessments", response_model=List[AssessmentMeta])
def list_assessments():
    """Retrieve list of available personality assessment definitions and dimensions."""
    results = []
    for test_key, data in ASSESSMENT_REGISTRY.items():
        results.append(
            AssessmentMeta(
                type=test_key,
                name=data["name"],
                tagline=data["tagline"],
                dimensions=data["dimensions"],
                question_count=data["question_count"],
                estimated_minutes=data["estimated_minutes"],
                description=data["description"]
            )
        )
    return results


# ---------------------------------------------------------------------------
# Assessment Session Lifecycle (NOT_STARTED -> IN_PROGRESS -> COMPLETED)
# ---------------------------------------------------------------------------

@router.post("/sessions", response_model=SessionStartResponse, status_code=status.HTTP_201_CREATED)
def start_session(req: SessionStartRequest, db: Session = Depends(get_db)):
    """
    Start a new assessment session.
    Transitions lifecycle to IN_PROGRESS and delivers authorized questions.
    """
    if req.assessment_type not in QUESTION_BANKS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unknown or unconfigured assessment type '{req.assessment_type}'"
        )

    repo = AssessmentRepository(db)
    session = repo.create_session(assessment_type=req.assessment_type, client_info=req.client_info)

    raw_questions = QUESTION_BANKS[req.assessment_type]
    questions = [QuestionItem(**q) for q in raw_questions]

    return SessionStartResponse(
        session_id=session.id,
        assessment_type=req.assessment_type,
        total_questions=len(questions),
        questions=questions,
        started_at=session.started_at
    )


@router.get("/sessions/{session_id}", response_model=SessionStatusOut)
def get_session_status(session_id: str, db: Session = Depends(get_db)):
    """Retrieve session lifecycle progress, verification status, and questions answered."""
    repo = AssessmentRepository(db)
    session = repo.get_session(session_id)
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assessment session not found")

    total_q = len(QUESTION_BANKS.get(session.assessment_type, []))
    answered_q = db.query(AssessmentResponse).filter(AssessmentResponse.session_id == session_id).count()

    return SessionStatusOut(
        session_id=session.id,
        assessment_type=session.assessment_type,
        status=session.status,
        total_questions=total_q,
        answered_count=answered_q,
        started_at=session.started_at,
        completed_at=session.completed_at
    )


@router.get("/sessions/{session_id}/resume", response_model=SessionResumeOut)
def resume_session(session_id: str, db: Session = Depends(get_db)):
    """
    Resume an assessment session. Delivers saved answers, current progress index,
    and authorized question set to allow seamless continuation without answer loss.
    """
    repo = AssessmentRepository(db)
    session = repo.get_session(session_id)
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assessment session not found")

    raw_questions = QUESTION_BANKS.get(session.assessment_type, [])
    questions = [QuestionItem(**q) for q in raw_questions]
    responses = repo.get_session_responses(session_id)
    answers_map = {r.question_id: r.selected_value for r in responses}

    return SessionResumeOut(
        session_id=session.id,
        assessment_type=session.assessment_type,
        assessment_version=getattr(session, "assessment_version", "1.0") or "1.0",
        status=session.status,
        progress_index=getattr(session, "progress_index", 0) or 0,
        total_questions=len(questions),
        answered_count=len(answers_map),
        answers=answers_map,
        questions=questions,
        started_at=session.started_at
    )


@router.patch("/sessions/{session_id}/progress", status_code=status.HTTP_200_OK)
def update_session_progress(session_id: str, payload: Dict[str, int], db: Session = Depends(get_db)):
    """Update current progress question index for an active session."""
    progress_index = payload.get("progress_index", 0)
    repo = AssessmentRepository(db)
    session = repo.update_session_progress(session_id, progress_index)
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assessment session not found")
    return {"success": True, "session_id": session_id, "progress_index": session.progress_index}


@router.post("/sessions/{session_id}/responses", status_code=status.HTTP_200_OK)
def save_responses(
    session_id: str,
    req: BatchResponsesRequest,
    db: Session = Depends(get_db)
):
    """
    Save responses for an active session with duplicate-answer protection (updates in-place).
    Requires active session in IN_PROGRESS status.
    """
    repo = AssessmentRepository(db)
    session = repo.get_session(session_id)
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assessment session not found")

    if session.status == "COMPLETED":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot record responses for an already completed session. Please start a retake session."
        )

    saved_count = 0
    for item in req.responses:
        repo.save_response(
            session_id=session.id,
            question_id=item.question_id,
            dimension=item.dimension,
            selected_value=item.selected_value
        )
        saved_count += 1

    return {
        "success": True,
        "session_id": session_id,
        "saved_count": saved_count,
        "status": session.status
    }


@router.post("/sessions/{session_id}/complete", response_model=AssessmentResultOut)
def complete_session(
    session_id: str,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Complete an assessment session, validate completion completeness, score the assessment,
    persist results atomically in PostgreSQL, and update personality synthesis.
    """
    repo = AssessmentRepository(db)
    session = repo.get_session(session_id)
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assessment session not found")

    if session.status == "COMPLETED":
        existing_result = repo.get_result_by_session_id(session_id)
        if existing_result:
            return result_to_dict(existing_result)

    # 1. Completion Validation: ensure all questions were answered
    total_q = len(QUESTION_BANKS.get(session.assessment_type, []))
    responses = repo.get_session_responses(session_id)
    answered_map = {r.question_id: r for r in responses}

    if len(answered_map) < total_q:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Incomplete assessment: answered {len(answered_map)} of {total_q} questions. Incomplete sessions cannot be finalized."
        )

    # 2. Convert to Answer Items for scoring
    answer_items = [
        ResponseAnswerItem(
            question_id=r.question_id,
            dimension=r.dimension,
            selected_value=r.selected_value
        )
        for r in responses
    ]

    # 3. Calculate Scores
    scored_data = None
    if session.assessment_type == "MBTI":
        scored_data = score_mbti(answer_items)
    elif session.assessment_type == "DISC":
        scored_data = score_disc(answer_items)
    elif session.assessment_type == "BIG_FIVE":
        scored_data = score_big_five(answer_items)
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported assessment scoring type"
        )

    # 4. Atomic Transaction: record results and normalized trait scores
    result = repo.complete_session_and_record_results(
        session=session,
        result_code=scored_data["result_code"],
        result_title=scored_data["result_title"],
        summary=scored_data["summary"],
        scores=scored_data["scores"],
        soft_skills=scored_data["soft_skills"],
        strengths=scored_data["strengths"],
        weaknesses=scored_data["weaknesses"]
    )

    # 5. Refresh Personality Synthesis
    refresh_synthesis(db)

    # 6. Audit Event
    client_ip = request.client.host if request.client else "unknown"
    log_audit_event(
        db=db,
        event_type="ASSESSMENT_COMPLETED",
        status="SUCCESS",
        details={"type": session.assessment_type, "result_code": result.result_code, "session_id": session.id},
        ip_address=client_ip
    )

    return result_to_dict(result)


# ---------------------------------------------------------------------------
# Results & History
# ---------------------------------------------------------------------------

@router.get("/results", response_model=List[AssessmentResultOut])
def get_all_results(db: Session = Depends(get_db)):
    """Retrieve all completed assessment results."""
    repo = AssessmentRepository(db)
    results = repo.get_all_results()
    return [result_to_dict(r) for r in results]


@router.get("/results/{session_id}", response_model=AssessmentResultOut)
def get_result_by_session(session_id: str, db: Session = Depends(get_db)):
    """Retrieve scored result for a specific session."""
    repo = AssessmentRepository(db)
    res = repo.get_result_by_session_id(session_id)
    if not res:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assessment result not found")
    return result_to_dict(res)


@router.get("/history", response_model=List[AssessmentResultOut])
def get_assessment_history(db: Session = Depends(get_db)):
    """Retrieve all assessment history in chronological order."""
    repo = AssessmentRepository(db)
    results = repo.get_all_results(limit=100)
    return [result_to_dict(r) for r in results]


@router.patch("/results/{result_id}/visibility", response_model=AssessmentResultOut)
def toggle_result_visibility(
    result_id: int,
    req: ResultVisibilityUpdate,
    request: Request,
    current_user: User = Depends(require_pin_verification),
    db: Session = Depends(get_db)
):
    """
    Toggle public/private visibility of an assessment result.
    Requires PIN verification via X-Action-PIN header.
    """
    repo = AssessmentRepository(db)
    result = repo.update_result_visibility(result_id, req.is_public)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assessment result not found")

    client_ip = request.client.host if request.client else "unknown"
    log_audit_event(
        db=db,
        event_type="RESULT_VISIBILITY_UPDATED",
        status="SUCCESS",
        user_id=current_user.id,
        username=current_user.username,
        details={"result_id": result_id, "is_public": req.is_public},
        ip_address=client_ip
    )

    return result_to_dict(result)


@router.get("/compare", response_model=ResultComparisonOut)
def compare_results(
    baseline_session_id: str,
    target_session_id: str,
    db: Session = Depends(get_db)
):
    """
    Compare two completed assessment attempts of the same model.
    Returns dimension score differentials, shift directions, and non-judgmental psychometric analysis.
    """
    repo = AssessmentRepository(db)
    res1, res2 = repo.get_results_for_comparison(baseline_session_id, target_session_id)
    if not res1 or not res2:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="One or both assessment sessions for comparison were not found"
        )
    if res1.assessment_type != res2.assessment_type:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot compare differing assessment types ({res1.assessment_type} vs {res2.assessment_type})"
        )

    b_dict = result_to_dict(res1)
    t_dict = result_to_dict(res2)
    comparison_data = compare_assessment_results(b_dict, t_dict)
    return ResultComparisonOut(**comparison_data)


@router.get("/public", response_model=PersonalitySynthesisOut)
def get_public_personality(db: Session = Depends(get_db)):
    """
    Public personality profile endpoint:
    Returns only assessments and synthesis items explicitly marked is_public=True.
    Strictly protects raw responses and private historical data.
    """
    repo = AssessmentRepository(db)
    latest_mbti = repo.get_latest_result_by_type("MBTI", public_only=True)
    latest_disc = repo.get_latest_result_by_type("DISC", public_only=True)
    latest_b5 = repo.get_latest_result_by_type("BIG_FIVE", public_only=True)

    assessments_completed = []
    if latest_mbti: assessments_completed.append("MBTI")
    if latest_disc: assessments_completed.append("DISC")
    if latest_b5: assessments_completed.append("BIG_FIVE")

    synthesis = db.query(PersonalitySynthesis).first()
    soft_skills = []
    strengths = []
    weaknesses = []
    summary = None

    if synthesis and assessments_completed:
        try:
            soft_skills = json.loads(synthesis.key_soft_skills) if synthesis.key_soft_skills else []
            strengths = json.loads(synthesis.key_strengths) if synthesis.key_strengths else []
            weaknesses = json.loads(synthesis.key_weaknesses) if synthesis.key_weaknesses else []
            summary = synthesis.summary_notes
        except Exception:
            pass

    return PersonalitySynthesisOut(
        has_assessments=len(assessments_completed) > 0,
        key_soft_skills=soft_skills,
        key_strengths=strengths,
        key_weaknesses=weaknesses,
        summary_notes=summary,
        assessments_completed=assessments_completed,
        latest_results={
            "MBTI": result_to_dict(latest_mbti) if latest_mbti else None,
            "DISC": result_to_dict(latest_disc) if latest_disc else None,
            "BIG_FIVE": result_to_dict(latest_b5) if latest_b5 else None
        },
        updated_at=synthesis.updated_at if synthesis else None
    )


@router.delete("/results/{result_id}", status_code=status.HTTP_200_OK)
def delete_personality_result(
    result_id: int,
    request: Request,
    current_user: User = Depends(require_pin_verification),
    db: Session = Depends(get_db)
):
    """
    Delete an assessment result.
    Requires admin privileges and PIN verification via X-Action-PIN header.
    """
    res = db.query(AssessmentResult).filter(AssessmentResult.id == result_id).first()
    if not res:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assessment result not found")

    session_id = res.session_id
    db.delete(res)
    session = db.query(AssessmentSession).filter(AssessmentSession.id == session_id).first()
    if session:
        db.delete(session)
    db.commit()

    # Recalculate synthesis
    refresh_synthesis(db)

    client_ip = request.client.host if request.client else "unknown"
    log_audit_event(
        db=db,
        event_type="ASSESSMENT_DELETED",
        status="SUCCESS",
        user_id=current_user.id,
        username=current_user.username,
        details={"result_id": result_id},
        ip_address=client_ip
    )

    return {"success": True, "message": "Assessment result deleted"}


# ---------------------------------------------------------------------------
# Personality Intelligence & Synthesis Layer
# ---------------------------------------------------------------------------

@router.get("/synthesis", response_model=PersonalitySynthesisOut)
def get_personality_synthesis(db: Session = Depends(get_db)):
    """
    Retrieve unified personality intelligence synthesis:
    aggregates key soft skills, key strengths, key weaknesses,
    and latest individual assessment results.
    """
    synthesis = db.query(PersonalitySynthesis).first()
    
    # Retrieve latest for each assessment
    latest_mbti = db.query(AssessmentResult).filter(AssessmentResult.assessment_type == "MBTI").order_by(AssessmentResult.completed_at.desc()).first()
    latest_disc = db.query(AssessmentResult).filter(AssessmentResult.assessment_type == "DISC").order_by(AssessmentResult.completed_at.desc()).first()
    latest_b5 = db.query(AssessmentResult).filter(AssessmentResult.assessment_type == "BIG_FIVE").order_by(AssessmentResult.completed_at.desc()).first()

    assessments_completed = []
    if latest_mbti: assessments_completed.append("MBTI")
    if latest_disc: assessments_completed.append("DISC")
    if latest_b5: assessments_completed.append("BIG_FIVE")

    soft_skills = []
    strengths = []
    weaknesses = []
    summary = None

    if synthesis:
        try:
            soft_skills = json.loads(synthesis.key_soft_skills) if synthesis.key_soft_skills else []
            strengths = json.loads(synthesis.key_strengths) if synthesis.key_strengths else []
            weaknesses = json.loads(synthesis.key_weaknesses) if synthesis.key_weaknesses else []
            summary = synthesis.summary_notes
        except Exception:
            pass

    # If assessments exist but synthesis is empty or not yet derived, re-evaluate automatically
    if not synthesis or (assessments_completed and not strengths):
        refresh_synthesis(db)
        synthesis = db.query(PersonalitySynthesis).first()
        if synthesis:
            try:
                soft_skills = json.loads(synthesis.key_soft_skills) if synthesis.key_soft_skills else []
                strengths = json.loads(synthesis.key_strengths) if synthesis.key_strengths else []
                weaknesses = json.loads(synthesis.key_weaknesses) if synthesis.key_weaknesses else []
                summary = synthesis.summary_notes
            except Exception:
                pass

    return PersonalitySynthesisOut(
        has_assessments=len(assessments_completed) > 0,
        key_soft_skills=soft_skills,
        key_strengths=strengths,
        key_weaknesses=weaknesses,
        summary_notes=summary,
        assessments_completed=assessments_completed,
        latest_results={
            "MBTI": result_to_dict(latest_mbti) if latest_mbti else None,
            "DISC": result_to_dict(latest_disc) if latest_disc else None,
            "BIG_FIVE": result_to_dict(latest_b5) if latest_b5 else None
        },
        updated_at=synthesis.updated_at if synthesis else None
    )


@router.post("/synthesis/refresh", response_model=PersonalitySynthesisOut)
def refresh_personality_synthesis(db: Session = Depends(get_db)):
    """
    Force re-evaluation of personality synthesis based strictly on the number of completed tests:
    - 1 test -> evaluated on 1 test.
    - 2 tests -> evaluated on 2 tests.
    - 3 tests -> evaluated on 3 tests.
    - 0 tests -> empty lists.
    """
    refresh_synthesis(db)
    return get_personality_synthesis(db)


@router.put("/synthesis", response_model=PersonalitySynthesisOut)
def update_personality_synthesis(
    req: SynthesisUpdateRequest,
    request: Request,
    current_user: User = Depends(require_pin_verification),
    db: Session = Depends(get_db)
):
    """
    Manually customize or refine synthesized key soft skills, strengths, and weaknesses.
    Protected by PIN verification via X-Action-PIN header.
    """
    synthesis = db.query(PersonalitySynthesis).first()
    if not synthesis:
        synthesis = PersonalitySynthesis(
            key_soft_skills=json.dumps(req.key_soft_skills),
            key_strengths=json.dumps(req.key_strengths),
            key_weaknesses=json.dumps(req.key_weaknesses),
            summary_notes=req.summary_notes
        )
        db.add(synthesis)
    else:
        prev_snapshot = {
            "key_soft_skills": json.loads(synthesis.key_soft_skills or "[]"),
            "key_strengths": json.loads(synthesis.key_strengths or "[]"),
            "key_weaknesses": json.loads(synthesis.key_weaknesses or "[]"),
            "summary_notes": synthesis.summary_notes
        }
        synthesis.key_soft_skills = json.dumps(req.key_soft_skills)
        synthesis.key_strengths = json.dumps(req.key_strengths)
        synthesis.key_weaknesses = json.dumps(req.key_weaknesses)
        synthesis.summary_notes = req.summary_notes
        synthesis.updated_at = datetime.now(timezone.utc)

        record_content_revision(
            db=db,
            entity_name="personality_synthesis",
            action="UPDATE",
            entity_id=str(synthesis.id),
            editor_username=current_user.username,
            change_summary="Refined personality synthesis through CMS",
            previous_snapshot=prev_snapshot,
            current_snapshot={
                "key_soft_skills": req.key_soft_skills,
                "key_strengths": req.key_strengths,
                "key_weaknesses": req.key_weaknesses,
                "summary_notes": req.summary_notes
            }
        )

    db.commit()

    client_ip = request.client.host if request.client else "unknown"
    log_audit_event(
        db=db,
        event_type="SYNTHESIS_UPDATED",
        status="SUCCESS",
        user_id=current_user.id,
        username=current_user.username,
        details={"soft_skills_count": len(req.key_soft_skills)},
        ip_address=client_ip
    )

    return get_personality_synthesis(db)


# ---------------------------------------------------------------------------
# Administrative Assessment & Question Bank Management (Sections 37, 38, 39)
# ---------------------------------------------------------------------------

@router.get("/admin/stats", response_model=AssessmentStatsOut)
def get_assessment_admin_stats(db: Session = Depends(get_db)):
    """
    Retrieve psychometric assessment analytics and completion statistics across models.
    """
    total_sessions = db.query(AssessmentSession).count()
    completed_sessions = db.query(AssessmentSession).filter(AssessmentSession.status == "COMPLETED").count()
    in_prog_sessions = db.query(AssessmentSession).filter(AssessmentSession.status == "IN_PROGRESS").count()
    total_results = db.query(AssessmentResult).count()
    public_results = db.query(AssessmentResult).filter(AssessmentResult.is_public == True).count()
    private_results = db.query(AssessmentResult).filter(AssessmentResult.is_public == False).count()

    models = {}
    for m in ["MBTI", "DISC", "BIG_FIVE"]:
        m_sess = db.query(AssessmentSession).filter(AssessmentSession.assessment_type == m).count()
        m_comp = db.query(AssessmentSession).filter(AssessmentSession.assessment_type == m, AssessmentSession.status == "COMPLETED").count()
        m_res = db.query(AssessmentResult).filter(AssessmentResult.assessment_type == m).count()
        m_pub = db.query(AssessmentResult).filter(AssessmentResult.assessment_type == m, AssessmentResult.is_public == True).count()
        models[m] = {
            "total_sessions": m_sess,
            "completed_sessions": m_comp,
            "total_results": m_res,
            "public_results": m_pub,
            "completion_rate": round((m_comp / m_sess * 100), 1) if m_sess > 0 else 0.0
        }

    return AssessmentStatsOut(
        total_sessions=total_sessions,
        completed_sessions=completed_sessions,
        in_progress_sessions=in_prog_sessions,
        total_results=total_results,
        public_results=public_results,
        private_results=private_results,
        models=models
    )


@router.get("/admin/definitions", response_model=List[AssessmentDefinitionOut])
def list_assessment_definitions(db: Session = Depends(get_db)):
    """
    List all configured assessment definitions including versions and publishing statuses.
    Auto-populates from ASSESSMENT_REGISTRY if database table is initially unpopulated.
    """
    definitions = db.query(AssessmentDefinition).order_by(AssessmentDefinition.id.asc()).all()
    if not definitions:
        for code, meta in ASSESSMENT_REGISTRY.items():
            defn = AssessmentDefinition(
                code=code,
                name=meta["name"],
                version="1.0",
                tagline=meta.get("tagline"),
                description=meta.get("description"),
                question_count=meta["question_count"],
                estimated_minutes=meta.get("estimated_minutes", 10),
                status="PUBLISHED",
                is_active=True
            )
            db.add(defn)
        db.commit()
        definitions = db.query(AssessmentDefinition).order_by(AssessmentDefinition.id.asc()).all()
    return definitions



@router.post("/admin/definitions", response_model=AssessmentDefinitionOut, status_code=status.HTTP_201_CREATED)
def create_assessment_definition(
    req: AssessmentDefinitionCreate,
    request: Request,
    current_user: User = Depends(require_pin_verification),
    db: Session = Depends(get_db)
):
    """
    Create a new assessment definition or version.
    PIN-protected with audit logging.
    """
    existing = db.query(AssessmentDefinition).filter(
        AssessmentDefinition.code == req.code,
        AssessmentDefinition.version == req.version
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Assessment definition for code '{req.code}' version '{req.version}' already exists."
        )

    defn = AssessmentDefinition(
        code=req.code.upper(),
        name=req.name,
        version=req.version,
        tagline=req.tagline,
        description=req.description,
        question_count=req.question_count,
        estimated_minutes=req.estimated_minutes,
        status=req.status,
        is_active=(req.status == "PUBLISHED")
    )
    db.add(defn)
    db.commit()
    db.refresh(defn)

    client_ip = request.client.host if request.client else "unknown"
    log_audit_event(
        db=db,
        event_type="ASSESSMENT_DEFINITION_CREATED",
        status="SUCCESS",
        user_id=current_user.id,
        username=current_user.username,
        details={"code": defn.code, "version": defn.version, "status": defn.status},
        ip_address=client_ip
    )
    return defn


@router.patch("/admin/definitions/{definition_id}/status", response_model=AssessmentDefinitionOut)
def update_definition_status(
    definition_id: int,
    req: AssessmentDefinitionStatusUpdate,
    request: Request,
    current_user: User = Depends(require_pin_verification),
    db: Session = Depends(get_db)
):
    """
    Publish or archive an assessment definition version.
    Enforces Section 39 publishing immutability rules.
    """
    defn = db.query(AssessmentDefinition).filter(AssessmentDefinition.id == definition_id).first()
    if not defn:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assessment definition not found")

    old_status = defn.status
    defn.status = req.status
    defn.is_active = (req.status == "PUBLISHED")
    defn.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(defn)

    client_ip = request.client.host if request.client else "unknown"
    log_audit_event(
        db=db,
        event_type="ASSESSMENT_DEFINITION_STATUS_UPDATED",
        status="SUCCESS",
        user_id=current_user.id,
        username=current_user.username,
        details={"definition_id": definition_id, "old_status": old_status, "new_status": req.status},
        ip_address=client_ip
    )
    return defn


@router.get("/admin/definitions/{definition_id}/questions", response_model=List[AssessmentQuestionOut])
def get_definition_questions(definition_id: int, db: Session = Depends(get_db)):
    """
    Retrieve full question bank for an assessment definition.
    """
    defn = db.query(AssessmentDefinition).filter(AssessmentDefinition.id == definition_id).first()
    if not defn:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assessment definition not found")

    questions = (
        db.query(AssessmentQuestion)
        .filter(AssessmentQuestion.assessment_definition_id == definition_id)
        .order_by(AssessmentQuestion.question_order.asc())
        .all()
    )
    return questions


@router.post("/admin/questions", response_model=AssessmentQuestionOut, status_code=status.HTTP_201_CREATED)
def create_assessment_question(
    req: AssessmentQuestionCreate,
    request: Request,
    current_user: User = Depends(require_pin_verification),
    db: Session = Depends(get_db)
):
    """
    Create a new question in the assessment bank.
    PIN-protected with audit logging.
    """
    existing = db.query(AssessmentQuestion).filter(AssessmentQuestion.id == req.id).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Question with ID '{req.id}' already exists")

    q = AssessmentQuestion(
        id=req.id,
        assessment_definition_id=req.assessment_definition_id,
        definition_type=req.definition_type.upper(),
        question_key=req.id,
        dimension=req.dimension,
        question_text=req.question_text,
        positive_pole=req.positive_pole,
        negative_pole=req.negative_pole,
        scale_type=req.scale_type,
        question_order=req.question_order,
        scoring_configuration=req.scoring_configuration,
        is_active=True
    )
    db.add(q)
    db.commit()
    db.refresh(q)

    client_ip = request.client.host if request.client else "unknown"
    log_audit_event(
        db=db,
        event_type="ASSESSMENT_QUESTION_CREATED",
        status="SUCCESS",
        user_id=current_user.id,
        username=current_user.username,
        details={"question_id": q.id, "definition_type": q.definition_type, "dimension": q.dimension},
        ip_address=client_ip
    )
    return q


@router.put("/admin/questions/{question_id}", response_model=AssessmentQuestionOut)
def update_assessment_question(
    question_id: str,
    req: AssessmentQuestionUpdate,
    request: Request,
    current_user: User = Depends(require_pin_verification),
    db: Session = Depends(get_db)
):
    """
    Update question text, poles, order, dimension, or scoring metadata.
    PIN-protected with revision tracking.
    """
    q = db.query(AssessmentQuestion).filter(AssessmentQuestion.id == question_id).first()
    if not q:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assessment question not found")

    prev_snapshot = {
        "question_text": q.question_text,
        "dimension": q.dimension,
        "positive_pole": q.positive_pole,
        "negative_pole": q.negative_pole,
        "question_order": q.question_order,
        "is_active": q.is_active
    }

    if req.question_text is not None:
        q.question_text = req.question_text
    if req.dimension is not None:
        q.dimension = req.dimension
    if req.positive_pole is not None:
        q.positive_pole = req.positive_pole
    if req.negative_pole is not None:
        q.negative_pole = req.negative_pole
    if req.scale_type is not None:
        q.scale_type = req.scale_type
    if req.question_order is not None:
        q.question_order = req.question_order
    if req.is_active is not None:
        q.is_active = req.is_active
    if req.scoring_configuration is not None:
        q.scoring_configuration = req.scoring_configuration
    q.updated_at = datetime.now(timezone.utc)

    record_content_revision(
        db=db,
        entity_name="assessment_question",
        action="UPDATE",
        entity_id=question_id,
        editor_username=current_user.username,
        change_summary=f"Updated assessment question {question_id}",
        previous_snapshot=prev_snapshot,
        current_snapshot={
            "question_text": q.question_text,
            "dimension": q.dimension,
            "positive_pole": q.positive_pole,
            "negative_pole": q.negative_pole,
            "question_order": q.question_order,
            "is_active": q.is_active
        }
    )

    db.commit()
    db.refresh(q)

    client_ip = request.client.host if request.client else "unknown"
    log_audit_event(
        db=db,
        event_type="ASSESSMENT_QUESTION_UPDATED",
        status="SUCCESS",
        user_id=current_user.id,
        username=current_user.username,
        details={"question_id": question_id},
        ip_address=client_ip
    )
    return q


@router.patch("/admin/questions/{question_id}/toggle", response_model=AssessmentQuestionOut)
def toggle_question_active(
    question_id: str,
    request: Request,
    current_user: User = Depends(require_pin_verification),
    db: Session = Depends(get_db)
):
    """
    Toggle an assessment question active/inactive state.
    PIN-protected.
    """
    q = db.query(AssessmentQuestion).filter(AssessmentQuestion.id == question_id).first()
    if not q:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assessment question not found")

    q.is_active = not q.is_active
    q.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(q)

    client_ip = request.client.host if request.client else "unknown"
    log_audit_event(
        db=db,
        event_type="ASSESSMENT_QUESTION_TOGGLED",
        status="SUCCESS",
        user_id=current_user.id,
        username=current_user.username,
        details={"question_id": question_id, "is_active": q.is_active},
        ip_address=client_ip
    )
    return q

