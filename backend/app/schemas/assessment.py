from datetime import datetime
from typing import List, Dict, Any, Optional, Literal
from pydantic import BaseModel, Field

AssessmentType = Literal["MBTI", "DISC", "BIG_FIVE"]


class QuestionItem(BaseModel):
    id: str
    dimension: str
    text: str
    positive_pole: Optional[str] = None
    negative_pole: Optional[str] = None
    scale_type: str = "likert_5"  # 1 to 5 scale or 1 to 7


class AssessmentMeta(BaseModel):
    type: AssessmentType
    name: str
    tagline: str
    dimensions: List[str]
    question_count: int
    estimated_minutes: int
    description: str


class SessionStartRequest(BaseModel):
    assessment_type: AssessmentType
    client_info: Optional[str] = None


class SessionStartResponse(BaseModel):
    session_id: str
    assessment_type: AssessmentType
    total_questions: int
    questions: List[QuestionItem]
    started_at: datetime


class ResponseAnswerItem(BaseModel):
    question_id: str
    dimension: str
    selected_value: int = Field(..., ge=1, le=5)


class SubmitAssessmentRequest(BaseModel):
    session_id: str
    answers: List[ResponseAnswerItem]


class BatchResponsesRequest(BaseModel):
    responses: List[ResponseAnswerItem]


class SessionStatusOut(BaseModel):
    session_id: str
    assessment_type: AssessmentType
    status: str
    total_questions: int
    answered_count: int
    started_at: datetime
    completed_at: Optional[datetime] = None


class AssessmentResultOut(BaseModel):
    id: int
    session_id: str
    assessment_type: AssessmentType
    result_code: str
    result_title: str
    summary: Optional[str] = None
    scores: Dict[str, Any]
    soft_skills: List[str]
    strengths: List[str]
    weaknesses: List[str]
    completed_at: datetime


class PersonalitySynthesisOut(BaseModel):
    has_assessments: bool
    key_soft_skills: List[str]
    key_strengths: List[str]
    key_weaknesses: List[str]
    summary_notes: Optional[str] = None
    assessments_completed: List[str]  # e.g., ["MBTI", "DISC"]
    latest_results: Dict[str, Optional[AssessmentResultOut]] = Field(default_factory=dict)
    updated_at: Optional[datetime] = None


class SynthesisUpdateRequest(BaseModel):
    key_soft_skills: List[str]
    key_strengths: List[str]
    key_weaknesses: List[str]
    summary_notes: Optional[str] = None


class TraitScoreOut(BaseModel):
    id: int
    result_id: int
    trait_code: str
    score: float
    normalized_score: float
    created_at: datetime


class SoftSkillRecordOut(BaseModel):
    id: int
    profile_id: Optional[int] = None
    result_id: Optional[int] = None
    name: str
    description: Optional[str] = None
    category: str
    source: str
    created_at: datetime


class StrengthRecordOut(BaseModel):
    id: int
    profile_id: Optional[int] = None
    result_id: Optional[int] = None
    title: str
    description: Optional[str] = None
    source: str
    created_at: datetime


class WeaknessRecordOut(BaseModel):
    id: int
    profile_id: Optional[int] = None
    result_id: Optional[int] = None
    title: str
    description: Optional[str] = None
    source: str
    created_at: datetime

