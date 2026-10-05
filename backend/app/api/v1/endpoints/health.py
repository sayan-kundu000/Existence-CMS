from datetime import datetime, timezone
from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.core.database import get_db
from app.core.config import settings

router = APIRouter()


@router.get("", summary="Liveness check")
@router.get("/live", summary="Process liveness check")
def liveness():
    """Application process health check (Liveness). Returns 200 if process is running."""
    return {
        "status": "healthy",
        "project": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


@router.get("/readiness", summary="Dependency readiness check")
def readiness(response: Response, db: Session = Depends(get_db)):
    """
    Readiness check verifying database connectivity.
    Returns 200 OK when ready to accept traffic; returns 503 Service Unavailable if database is unreachable.
    Never leaks credentials, connection strings, or internal traces.
    """
    db_connected = False
    try:
        db.execute(text("SELECT 1"))
        db_connected = True
    except Exception:
        db_connected = False

    if not db_connected:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return {
            "status": "not_ready",
            "project": settings.PROJECT_NAME,
            "version": settings.VERSION,
            "environment": settings.ENVIRONMENT,
            "database": "disconnected",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

    return {
        "status": "ready",
        "project": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "database": "connected",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
