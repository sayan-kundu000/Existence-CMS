from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime, timezone
import json
from sqlalchemy.orm import Session
from app.models.assessment import (
    AssessmentDefinition,
    AssessmentQuestion,
    AssessmentSession,
    AssessmentResponse,
    AssessmentResult,
    PersonalityTraitScore,
    SoftSkillRecord,
    StrengthRecord,
    WeaknessRecord,
    PersonalitySynthesis
)


class AssessmentRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_definitions(self) -> List[AssessmentDefinition]:
        return self.db.query(AssessmentDefinition).order_by(AssessmentDefinition.id.asc()).all()

    def get_definition_by_type(self, assessment_type: str) -> Optional[AssessmentDefinition]:
        return (
            self.db.query(AssessmentDefinition)
            .filter(AssessmentDefinition.assessment_type == assessment_type.upper())
            .first()
        )

    def get_questions_by_type(self, assessment_type: str) -> List[AssessmentQuestion]:
        return (
            self.db.query(AssessmentQuestion)
            .filter(AssessmentQuestion.definition_type == assessment_type.upper())
            .order_by(AssessmentQuestion.ordering.asc())
            .all()
        )

    def create_session(self, assessment_type: str, client_info: Optional[str] = None) -> AssessmentSession:
        session = AssessmentSession(
            assessment_type=assessment_type.upper(),
            status="IN_PROGRESS",
            client_info=client_info,
            started_at=datetime.now(timezone.utc)
        )
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        return session

    def get_session(self, session_id: str) -> Optional[AssessmentSession]:
        return self.db.query(AssessmentSession).filter(AssessmentSession.id == session_id).first()

    def save_response(self, session_id: str, question_id: str, dimension: str, selected_value: int) -> AssessmentResponse:
        # Check if an answer for this question already exists in this session; update if so
        existing = (
            self.db.query(AssessmentResponse)
            .filter(AssessmentResponse.session_id == session_id, AssessmentResponse.question_id == question_id)
            .first()
        )
        if existing:
            existing.selected_value = selected_value
            self.db.commit()
            self.db.refresh(existing)
            return existing

        resp = AssessmentResponse(
            session_id=session_id,
            question_id=question_id,
            dimension=dimension,
            selected_value=selected_value,
            created_at=datetime.now(timezone.utc)
        )
        self.db.add(resp)
        self.db.commit()
        self.db.refresh(resp)
        return resp

    def get_session_responses(self, session_id: str) -> List[AssessmentResponse]:
        return self.db.query(AssessmentResponse).filter(AssessmentResponse.session_id == session_id).all()

    def complete_session_and_record_results(
        self,
        session: AssessmentSession,
        result_code: str,
        result_title: str,
        summary: Optional[str],
        scores: Dict[str, Any],
        soft_skills: List[str],
        strengths: List[str],
        weaknesses: List[str]
    ) -> AssessmentResult:
        """
        Executes atomic transaction:
        1. Marks session COMPLETED
        2. Creates AssessmentResult
        3. Creates normalized PersonalityTraitScore, SoftSkillRecord, StrengthRecord, WeaknessRecord
        """
        try:
            # 1. Update session status
            session.status = "COMPLETED"
            session.completed_at = datetime.now(timezone.utc)

            # Check if result already exists for this session and clean it up atomically
            existing_result = self.get_result_by_session_id(session.id)
            if existing_result:
                self.db.delete(existing_result)
                self.db.flush()

            # 2. Create AssessmentResult
            version_str = getattr(session, "assessment_version", "1.0") or "1.0"
            result = AssessmentResult(
                session_id=session.id,
                assessment_type=session.assessment_type,
                result_code=result_code,
                result_title=result_title,
                result_version=version_str,
                is_public=True,
                summary=summary,
                scores_json=json.dumps(scores),
                soft_skills_json=json.dumps(soft_skills),
                strengths_json=json.dumps(strengths),
                weaknesses_json=json.dumps(weaknesses),
                completed_at=datetime.now(timezone.utc)
            )
            self.db.add(result)
            self.db.flush()

            # 3. Create normalized records
            # Trait scores
            if "dimensions" in scores and isinstance(scores["dimensions"], dict):
                for trait_name, val in scores["dimensions"].items():
                    ts = PersonalityTraitScore(
                        result_id=result.id,
                        trait_name=trait_name,
                        score_value=float(val),
                        percentage=float(val)
                    )
                    self.db.add(ts)
            elif "percentages" in scores and isinstance(scores["percentages"], dict):
                for trait_name, val in scores["percentages"].items():
                    ts = PersonalityTraitScore(
                        result_id=result.id,
                        trait_name=trait_name,
                        score_value=float(val),
                        percentage=float(val)
                    )
                    self.db.add(ts)
            elif any(k in scores for k in ["O", "C", "E", "A", "N"]):
                mapping = {
                    "O": "Openness",
                    "C": "Conscientiousness",
                    "E": "Extraversion",
                    "A": "Agreeableness",
                    "N": "Neuroticism"
                }
                for k, trait_name in mapping.items():
                    if k in scores:
                        val = float(scores[k])
                        ts = PersonalityTraitScore(
                            result_id=result.id,
                            trait_name=trait_name,
                            score_value=val,
                            percentage=val
                        )
                        self.db.add(ts)

            # Soft skills
            for s in soft_skills:
                sk_rec = SoftSkillRecord(
                    result_id=result.id,
                    name=s,
                    category=session.assessment_type,
                    source=session.assessment_type
                )
                self.db.add(sk_rec)

            # Strengths
            for st in strengths:
                st_rec = StrengthRecord(
                    result_id=result.id,
                    description=st,
                    source=session.assessment_type
                )
                self.db.add(st_rec)

            # Weaknesses
            for wk in weaknesses:
                wk_rec = WeaknessRecord(
                    result_id=result.id,
                    description=wk,
                    source=session.assessment_type
                )
                self.db.add(wk_rec)

            self.db.commit()
            self.db.refresh(result)
            return result
        except Exception as e:
            self.db.rollback()
            raise e

    def get_result_by_session_id(self, session_id: str) -> Optional[AssessmentResult]:
        return self.db.query(AssessmentResult).filter(AssessmentResult.session_id == session_id).first()

    def get_result_by_id(self, result_id: int) -> Optional[AssessmentResult]:
        return self.db.query(AssessmentResult).filter(AssessmentResult.id == result_id).first()

    def get_all_results(self, limit: int = 50, public_only: bool = False) -> List[AssessmentResult]:
        query = self.db.query(AssessmentResult)
        if public_only:
            query = query.filter(AssessmentResult.is_public == True)
        return query.order_by(AssessmentResult.completed_at.desc()).limit(limit).all()

    def get_latest_result_by_type(self, assessment_type: str, public_only: bool = False) -> Optional[AssessmentResult]:
        query = self.db.query(AssessmentResult).filter(AssessmentResult.assessment_type == assessment_type.upper())
        if public_only:
            query = query.filter(AssessmentResult.is_public == True)
        return query.order_by(AssessmentResult.completed_at.desc()).first()

    def update_session_progress(self, session_id: str, progress_index: int) -> Optional[AssessmentSession]:
        session = self.get_session(session_id)
        if session:
            session.progress_index = progress_index
            self.db.commit()
            self.db.refresh(session)
        return session

    def update_result_visibility(self, result_id: int, is_public: bool) -> Optional[AssessmentResult]:
        result = self.get_result_by_id(result_id)
        if result:
            result.is_public = is_public
            self.db.commit()
            self.db.refresh(result)
        return result

    def get_results_for_comparison(
        self, session_id_1: str, session_id_2: str
    ) -> Tuple[Optional[AssessmentResult], Optional[AssessmentResult]]:
        res1 = self.get_result_by_session_id(session_id_1)
        res2 = self.get_result_by_session_id(session_id_2)
        return res1, res2
