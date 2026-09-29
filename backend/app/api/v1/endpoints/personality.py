import json
from typing import List, Optional
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.assessment import (
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
    ResponseAnswerItem,
    BatchResponsesRequest,
    AssessmentResultOut,
    QuestionItem,
    PersonalitySynthesisOut,
    SynthesisUpdateRequest
)
from app.repositories.assessment_repository import AssessmentRepository
from app.services.personality_scoring import (
    score_mbti,
    score_disc,
    score_big_five
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
