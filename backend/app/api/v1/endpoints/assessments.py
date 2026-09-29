import json
from typing import List
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
    SubmitAssessmentRequest,
    AssessmentResultOut,
    QuestionItem
)
from app.services.personality_scoring import (
    score_mbti,
    score_disc,
    score_big_five,
    synthesize_personality
)
from app.services.audit_service import log_audit_event
from app.api.deps import require_pin_verification

router = APIRouter()


def result_to_dict(res: AssessmentResult) -> dict:
    scores = {}
    soft_skills = []
    strengths = []
    weaknesses = []

    try:
        scores = json.loads(res.scores_json) if res.scores_json else {}
    except Exception:
        scores = {}

    try:
        soft_skills = json.loads(res.soft_skills_json) if res.soft_skills_json else []
    except Exception:
        soft_skills = []

    try:
        strengths = json.loads(res.strengths_json) if res.strengths_json else []
    except Exception:
        strengths = []

    try:
        weaknesses = json.loads(res.weaknesses_json) if res.weaknesses_json else []
    except Exception:
        weaknesses = []

    return {
        "id": res.id,
        "session_id": res.session_id,
        "assessment_type": res.assessment_type,
        "result_code": res.result_code,
        "result_title": res.result_title,
        "summary": res.summary,
        "scores": scores,
        "soft_skills": soft_skills,
        "strengths": strengths,
        "weaknesses": weaknesses,
        "completed_at": res.completed_at
    }


def refresh_synthesis(db: Session) -> None:
    """Helper to recalculate personality synthesis based on the latest completed assessments."""
    latest_mbti = db.query(AssessmentResult).filter(AssessmentResult.assessment_type == "MBTI").order_by(AssessmentResult.completed_at.desc()).first()
    latest_disc = db.query(AssessmentResult).filter(AssessmentResult.assessment_type == "DISC").order_by(AssessmentResult.completed_at.desc()).first()
    latest_b5 = db.query(AssessmentResult).filter(AssessmentResult.assessment_type == "BIG_FIVE").order_by(AssessmentResult.completed_at.desc()).first()

    mbti_dict = result_to_dict(latest_mbti) if latest_mbti else None
    disc_dict = result_to_dict(latest_disc) if latest_disc else None
    b5_dict = result_to_dict(latest_b5) if latest_b5 else None

    soft_skills, strengths, weaknesses, summary = synthesize_personality(
        mbti=mbti_dict,
        disc=disc_dict,
        big_five=b5_dict
    )

    synthesis = db.query(PersonalitySynthesis).first()
    if not synthesis:
        synthesis = PersonalitySynthesis(
            key_soft_skills=json.dumps(soft_skills),
            key_strengths=json.dumps(strengths),
            key_weaknesses=json.dumps(weaknesses),
            summary_notes=summary
        )
        db.add(synthesis)
    else:
        synthesis.key_soft_skills = json.dumps(soft_skills)
        synthesis.key_strengths = json.dumps(strengths)
        synthesis.key_weaknesses = json.dumps(weaknesses)
        synthesis.summary_notes = summary
        synthesis.updated_at = datetime.now(timezone.utc)

    db.commit()


@router.get("/registry", response_model=List[AssessmentMeta])
def get_assessment_registry():
    """Retrieve list of available personality assessments and metadata."""
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


@router.post("/start", response_model=SessionStartResponse)
def start_assessment_session(req: SessionStartRequest, db: Session = Depends(get_db)):
    """Initialize a new assessment session and return its question bank."""
    if req.assessment_type not in QUESTION_BANKS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unknown assessment type '{req.assessment_type}'"
        )

    session = AssessmentSession(
        assessment_type=req.assessment_type,
        status="IN_PROGRESS",
        client_info=req.client_info
    )
    db.add(session)
    db.commit()
    db.refresh(session)

    raw_questions = QUESTION_BANKS[req.assessment_type]
    questions = [QuestionItem(**q) for q in raw_questions]

    return SessionStartResponse(
        session_id=session.id,
        assessment_type=req.assessment_type,
        total_questions=len(questions),
        questions=questions,
        started_at=session.started_at
    )


@router.post("/submit", response_model=AssessmentResultOut)
def submit_assessment(
    req: SubmitAssessmentRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Submit completed responses, score the assessment, persist results,
    and update the personality synthesis layer.
    """
    session = db.query(AssessmentSession).filter(AssessmentSession.id == req.session_id).first()
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assessment session not found")

    if session.status == "COMPLETED":
        # If already completed, return existing result
        existing_result = db.query(AssessmentResult).filter(AssessmentResult.session_id == req.session_id).first()
        if existing_result:
            return result_to_dict(existing_result)

    # Persist individual responses
    for ans in req.answers:
        resp = AssessmentResponse(
            session_id=session.id,
            question_id=ans.question_id,
            dimension=ans.dimension,
            selected_value=ans.selected_value
        )
        db.add(resp)

    # Score based on type
    scored_data = None
    if session.assessment_type == "MBTI":
        scored_data = score_mbti(req.answers)
    elif session.assessment_type == "DISC":
        scored_data = score_disc(req.answers)
    elif session.assessment_type == "BIG_FIVE":
        scored_data = score_big_five(req.answers)
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unsupported assessment scoring type")

    # Save AssessmentResult
    result = AssessmentResult(
        session_id=session.id,
        assessment_type=session.assessment_type,
        result_code=scored_data["result_code"],
        result_title=scored_data["result_title"],
        scores_json=json.dumps(scored_data["scores"]),
        soft_skills_json=json.dumps(scored_data["soft_skills"]),
        strengths_json=json.dumps(scored_data["strengths"]),
        weaknesses_json=json.dumps(scored_data["weaknesses"]),
        summary=scored_data["summary"],
        completed_at=datetime.now(timezone.utc)
    )
    db.add(result)

    # Mark session completed
    session.status = "COMPLETED"
    session.completed_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(result)

    # Refresh Personality Synthesis
    refresh_synthesis(db)

    # Audit logging
    client_ip = request.client.host if request.client else "unknown"
    log_audit_event(
        db=db,
        event_type="ASSESSMENT_COMPLETED",
        status="SUCCESS",
        details={"type": session.assessment_type, "result_code": result.result_code},
        ip_address=client_ip
    )

    return result_to_dict(result)


@router.get("/results/{session_id}", response_model=AssessmentResultOut)
def get_assessment_result(session_id: str, db: Session = Depends(get_db)):
    """Retrieve result for a specific session."""
    res = db.query(AssessmentResult).filter(AssessmentResult.session_id == session_id).first()
    if not res:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assessment result not found")
    return result_to_dict(res)


@router.get("/history", response_model=List[AssessmentResultOut])
def get_assessment_history(db: Session = Depends(get_db)):
    """Retrieve all completed assessment results in chronological order."""
    results = db.query(AssessmentResult).order_by(AssessmentResult.completed_at.desc()).all()
    return [result_to_dict(r) for r in results]


@router.delete("/results/{result_id}", status_code=status.HTTP_200_OK)
def delete_assessment_result(
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
    # Also delete the session
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
