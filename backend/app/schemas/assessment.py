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


class SessionResumeOut(BaseModel):
    session_id: str
    assessment_type: AssessmentType
    assessment_version: str = "1.0"
    status: str
    progress_index: int = 0
    total_questions: int
    answered_count: int
    answers: Dict[str, int] = Field(default_factory=dict)
    questions: List[QuestionItem]
    started_at: datetime


class ResultVisibilityUpdate(BaseModel):
    is_public: bool


class DimensionComparisonItem(BaseModel):
    dimension: str
    baseline_score: float
    target_score: float
    delta: float
    direction: str  # "INCREASED", "DECREASED", "UNCHANGED"
    interpretation: str


class ResultComparisonOut(BaseModel):
    assessment_type: AssessmentType
    baseline_session_id: str
    target_session_id: str
    baseline_result_code: str
    target_result_code: str
    baseline_completed_at: datetime
    target_completed_at: datetime
    dimensions_comparison: List[DimensionComparisonItem]
    summary: str


class AssessmentResultOut(BaseModel):
    id: int
    session_id: str
    assessment_type: AssessmentType
    result_code: str
    result_title: str
    result_version: str = "1.0"
    is_public: bool = True
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


class AssessmentDefinitionOut(BaseModel):
    id: int
    code: str
    name: str
    version: str = "1.0"
    tagline: Optional[str] = None
    description: Optional[str] = None
    is_active: bool = True
    question_count: int = 0
    estimated_minutes: int = 5
    status: str = "PUBLISHED"
    created_at: datetime
    updated_at: datetime


class AssessmentDefinitionCreate(BaseModel):
    code: str
    name: str
    version: str = "1.0"
    tagline: Optional[str] = None
    description: Optional[str] = None
    question_count: int = 0
    estimated_minutes: int = 5
    status: Literal["DRAFT", "PUBLISHED", "ARCHIVED"] = "DRAFT"


class AssessmentDefinitionStatusUpdate(BaseModel):
    status: Literal["DRAFT", "PUBLISHED", "ARCHIVED"]


class AssessmentQuestionOut(BaseModel):
    id: str
    assessment_definition_id: Optional[int] = None
    definition_type: Optional[str] = None
    question_key: Optional[str] = None
    dimension: str
    question_text: str
    positive_pole: Optional[str] = None
    negative_pole: Optional[str] = None
    scale_type: str = "likert_5"
    question_order: int = 0
    is_active: bool = True
    scoring_configuration: Optional[str] = "{}"
    created_at: datetime
    updated_at: datetime


class AssessmentQuestionCreate(BaseModel):
    id: str
    assessment_definition_id: Optional[int] = None
    definition_type: str
    dimension: str
    question_text: str
    positive_pole: Optional[str] = None
    negative_pole: Optional[str] = None
    scale_type: str = "likert_5"
    question_order: int = 0
    scoring_configuration: str = "{}"


class AssessmentQuestionUpdate(BaseModel):
    question_text: Optional[str] = None
    dimension: Optional[str] = None
    positive_pole: Optional[str] = None
    negative_pole: Optional[str] = None
    scale_type: Optional[str] = None
    question_order: Optional[int] = None
    is_active: Optional[bool] = None
    scoring_configuration: Optional[str] = None


class AssessmentStatsOut(BaseModel):
    total_sessions: int
    completed_sessions: int
    in_progress_sessions: int
    total_results: int
    public_results: int
    private_results: int
    models: Dict[str, Dict[str, Any]]


