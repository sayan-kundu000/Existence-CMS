from fastapi import APIRouter
from app.api.v1.endpoints import (
    auth,
    pin,
    profile,
    education,
    experience,
    skills,
    hobbies,
    interests,
    hobbies_interests,
    assessments,
    personality,
    cms,
    audit,
    health,
    projects
)

api_router = APIRouter()

api_router.include_router(health.router, prefix="/health", tags=["Health"])
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(pin.router, prefix="/pin", tags=["PIN Security"])
api_router.include_router(profile.router, prefix="/profile", tags=["Profile"])
api_router.include_router(education.router, prefix="/education", tags=["Education"])
api_router.include_router(experience.router, prefix="/experience", tags=["Work Experience"])
api_router.include_router(skills.router, prefix="/skills", tags=["Skills & 7-Level Ratings"])
api_router.include_router(projects.router, prefix="/projects", tags=["Projects Engine & Multiple Links"])
api_router.include_router(hobbies.router, prefix="/hobbies", tags=["Hobbies"])
api_router.include_router(interests.router, prefix="/interests", tags=["Interests"])
api_router.include_router(hobbies_interests.router, prefix="/hobbies-interests", tags=["Hobbies & Interests (Combined)"])
api_router.include_router(assessments.router, prefix="/assessments", tags=["Personality Assessments (MBTI, DISC, Big Five)"])
api_router.include_router(personality.router, prefix="/personality", tags=["Personality Intelligence & Synthesis"])
api_router.include_router(cms.router, prefix="/cms", tags=["Custom CMS"])
api_router.include_router(audit.router, prefix="/audit", tags=["Audit & Versioning"])
