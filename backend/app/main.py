import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from app.core.config import settings
from app.core.database import engine, Base, SessionLocal
from app.core.security import hash_password
from app.core.exceptions import AppException
from app.middleware.correlation_id import CorrelationIdMiddleware
from app.middleware.error_handler import (
    app_exception_handler,
    validation_exception_handler,
    http_exception_handler,
    unhandled_exception_handler
)
from app.models.user import User, PinSecurity
from app.models.profile import Profile
from app.models.assessment import PersonalitySynthesis, AssessmentDefinition, AssessmentQuestion
from app.data.question_banks import ASSESSMENT_REGISTRY, QUESTION_BANKS
from app.api.v1.router import api_router


def init_db():
    """Ensure database schema and initial baseline state are created."""
    if os.getenv("TESTING") == "True":
        return
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        # 1. Initialize Profile baseline if none exists (strictly empty, no invented info)
        existing_profile = db.query(Profile).first()
        if not existing_profile:
            blank_profile = Profile(
                name=None,
                email_ids="[]",
                mobile_number=None,
                linkedin=None,
                about=None
            )
            db.add(blank_profile)
            db.commit()

        # 2. Initialize Personality Synthesis baseline if none exists
        existing_synthesis = db.query(PersonalitySynthesis).first()
        if not existing_synthesis:
            blank_synthesis = PersonalitySynthesis(
                key_soft_skills="[]",
                key_strengths="[]",
                key_weaknesses="[]",
                summary_notes="Personality assessment not completed."
            )
            db.add(blank_synthesis)
            db.commit()

        # 3. Initialize default administrator if no users exist
        user_count = db.query(User).count()
        if user_count == 0:
            default_username = os.getenv("ADMIN_USERNAME", "admin")
            default_password = os.getenv("ADMIN_PASSWORD", "Admin@Existence2026!")
            default_email = os.getenv("ADMIN_EMAIL", "admin@existence.internal")

            admin_user = User(
                username=default_username,
                email=default_email,
                hashed_password=hash_password(default_password),
                role="admin",
                is_active=True
            )
            db.add(admin_user)
            db.commit()
            db.refresh(admin_user)

            # Unconfigured PIN record ready for admin setup
            pin_record = PinSecurity(
                user_id=admin_user.id,
                hashed_pin="",
                is_configured=False,
                failed_attempts=0,
                is_locked=False
            )
            db.add(pin_record)
            db.commit()
            print(f"[Existence Init] Seeded initial admin account: username='{default_username}'")

        # 4. Synchronize Assessment Definitions & Question Banks (43 items per assessment)
        for code, meta in ASSESSMENT_REGISTRY.items():
            defn = db.query(AssessmentDefinition).filter(AssessmentDefinition.code == code).first()
            if not defn:
                defn = AssessmentDefinition(
                    code=code,
                    name=meta["name"],
                    version="1.0",
                    tagline=meta.get("tagline"),
                    description=meta.get("description"),
                    question_count=meta["question_count"],
                    estimated_minutes=meta.get("estimated_minutes", 10),
                    is_active=True
                )
                db.add(defn)
                db.flush()
            else:
                defn.question_count = meta["question_count"]
                defn.estimated_minutes = meta.get("estimated_minutes", 10)
                defn.name = meta["name"]
                defn.tagline = meta.get("tagline")
                defn.description = meta.get("description")

            # Sync questions
            raw_questions = QUESTION_BANKS.get(code, [])
            for idx, q_data in enumerate(raw_questions, start=1):
                q_row = db.query(AssessmentQuestion).filter(AssessmentQuestion.id == q_data["id"]).first()
                if not q_row:
                    q_row = AssessmentQuestion(
                        id=q_data["id"],
                        assessment_definition_id=defn.id,
                        definition_type=code,
                        question_key=q_data["id"],
                        dimension=q_data["dimension"],
                        question_text=q_data["text"],
                        positive_pole=q_data.get("positive_pole"),
                        negative_pole=q_data.get("negative_pole"),
                        scale_type=q_data.get("scale_type", "likert_5"),
                        question_order=idx,
                        is_active=True
                    )
                    db.add(q_row)
                else:
                    q_row.dimension = q_data["dimension"]
                    q_row.question_text = q_data["text"]
                    q_row.positive_pole = q_data.get("positive_pole")
                    q_row.negative_pole = q_data.get("negative_pole")
                    q_row.question_order = idx
        db.commit()
    finally:
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    init_db()
    yield
    # Shutdown


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Existence Personal-Profile and Personality-Intelligence Platform REST API.",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/api/v1/openapi.json",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.ENVIRONMENT == "development" else settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request Correlation ID Middleware
app.add_middleware(CorrelationIdMiddleware)

# Standardized Centralized Exception Handlers (Section 27 Contract)
app.add_exception_handler(AppException, app_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(Exception, unhandled_exception_handler)


# Mount versioned API routes
app.include_router(api_router, prefix=settings.API_V1_PREFIX)


@app.get("/")
def root_redirect():
    return {
        "app": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "docs": "/docs",
        "api": settings.API_V1_PREFIX,
        "status": "operational"
    }
