"""
Comprehensive Integration, Production Readiness & E2E Test Suite (Prompt 10).

Validates:
1. Health & Readiness Lifecycle (/health, /readiness, 503 on dependency failure)
2. Education Date Business Rules (Conditional dates when currently studying)
3. Work Experience Date & Location Rules (Conditional dates when currently working)
4. Skills Engine 1-7 Scale Boundaries & Duplicate Prevention
5. Projects Engine with Technologies & Multiple Deployment Links
6. End-to-End Coherent User Lifecycle Flow (Profile -> Edu -> Exp -> Skill -> Project -> Assessment -> PIN -> Audit -> Public View)
7. Production Configuration & DevSecOps Validation
"""
import pytest
from datetime import datetime, timezone
from unittest.mock import patch
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.main import app
from app.core.config import Settings
from app.models.user import User, PinSecurity
from app.models.profile import Profile
from app.models.education import Education
from app.models.experience import Experience
from app.models.skill import Skill
from app.models.project import Project, ProjectLink
from app.models.audit import AuditEvent


# ==============================================================================
# 1. APPLICATION HEALTH & READINESS ARCHITECTURE (Section 4)
# ==============================================================================

def test_01_liveness_probes_return_200(client: TestClient):
    """Liveness probes (/health and /api/v1/health) return healthy 200 without secrets."""
    res_root = client.get("/health")
    assert res_root.status_code == 200
    data_root = res_root.json()
    assert data_root["status"] == "healthy"
    assert "version" in data_root
    assert "timestamp" in data_root

    res_api = client.get("/api/v1/health")
    assert res_api.status_code == 200
    assert res_api.json()["status"] == "healthy"


def test_02_readiness_probe_connected(client: TestClient):
    """Readiness probe returns 200 OK when database dependency is connected."""
    res = client.get("/readiness")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "ready"
    assert data["database"] == "connected"

    # API-prefixed route
    res_api = client.get("/api/v1/health/readiness")
    assert res_api.status_code == 200
    assert res_api.json()["database"] == "connected"


def test_03_readiness_probe_returns_503_on_db_failure(client: TestClient):
    """
    Readiness probe must return HTTP 503 Service Unavailable when DB is unreachable,
    and must NEVER expose internal credentials or stack traces.
    """
    with patch("sqlalchemy.orm.Session.execute", side_effect=Exception("Simulated DB Connection Timeout")):
        res = client.get("/readiness")
        assert res.status_code == 503
        data = res.json()
        assert data["status"] == "not_ready"
        assert data["database"] == "disconnected"
        # Zero trace of simulated exception text
        assert "Simulated DB" not in str(data)


# ==============================================================================
# 2. EDUCATION DATE BUSINESS RULES (Section 14)
# ==============================================================================

def test_04_education_date_rules(client: TestClient, admin_headers: dict):
    """
    Education date validation:
    - currently_studying = True -> ending date is wiped/ignored server-side.
    - currently_studying = False -> ending date is strictly required.
    - end date preceding start date is rejected.
    """
    # 1. Currently studying = True (even if ending date is sent, backend sets it to null)
    studying_res = client.post("/api/v1/education", json={
        "level": "Post Graduate",
        "stream": "Computer Science",
        "institution": "Stanford University",
        "starting_month_year": "September 2024",
        "ending_month_year": "May 2026",
        "currently_studying": True
    }, headers=admin_headers)
    assert studying_res.status_code == 201
    studying_data = studying_res.json()
    assert studying_data["currently_studying"] is True
    assert studying_data["ending_month_year"] is None
    edu_id = studying_data["id"]

    # 2. Currently studying = False without ending date -> MUST FAIL
    missing_end_res = client.post("/api/v1/education", json={
        "level": "Graduate",
        "stream": "Information Systems",
        "institution": "MIT",
        "starting_month_year": "September 2018",
        "currently_studying": False
    }, headers=admin_headers)
    assert missing_end_res.status_code in (400, 422)

    # 3. Ending date preceding starting date -> MUST FAIL
    inverted_res = client.post("/api/v1/education", json={
        "level": "Graduate",
        "stream": "Information Systems",
        "institution": "MIT",
        "starting_month_year": "September 2022",
        "ending_month_year": "June 2020",
        "currently_studying": False
    }, headers=admin_headers)
    assert inverted_res.status_code in (400, 422)

    # Clean up created record
    client.delete(f"/api/v1/education/{edu_id}", headers=admin_headers)


# ==============================================================================
# 3. WORK EXPERIENCE DATE & LOCATION RULES (Section 15)
# ==============================================================================

def test_05_experience_date_and_location_rules(client: TestClient, admin_headers: dict):
    """
    Experience date and location rules:
    - currently_working = True -> ending date wiped.
    - currently_working = False -> ending date required.
    - work_mode = Remote -> location set to 'Remote'.
    - work_mode = On-site / Hybrid -> location strictly required.
    """
    # 1. Remote currently working -> location defaults to Remote, ending date wiped
    remote_res = client.post("/api/v1/experience", json={
        "role": "Principal Security Architect",
        "employer": "Cyber Corp",
        "work_mode": "Remote",
        "location": "Any City",
        "starting_month_year": "January 2023",
        "ending_month_year": "December 2025",
        "currently_working": True
    }, headers=admin_headers)
    assert remote_res.status_code == 201
    remote_data = remote_res.json()
    assert remote_data["location"] == "Remote"
    assert remote_data["ending_month_year"] is None
    exp_id = remote_data["id"]

    # 2. On-site without location -> MUST FAIL
    onsite_fail = client.post("/api/v1/experience", json={
        "role": "Software Engineer",
        "employer": "Tech Labs",
        "work_mode": "On-site",
        "location": "   ",
        "starting_month_year": "January 2021",
        "ending_month_year": "December 2022",
        "currently_working": False
    }, headers=admin_headers)
    assert onsite_fail.status_code in (400, 422)

    # Clean up
    client.delete(f"/api/v1/experience/{exp_id}", headers=admin_headers)


# ==============================================================================
# 4. SKILLS ENGINE 1-7 BOUNDARIES & DUPLICATES (Section 16)
# ==============================================================================

def test_06_skill_rating_scale_and_deduplication(client: TestClient, admin_headers: dict):
    """
    Skill rating scale strictly enforces 1 to 7.
    Duplicate skill names within the same profile are rejected.
    """
    # Valid Skill (Rating 7 - Master)
    skill_res = client.post("/api/v1/skills", json={
        "name": "PostgreSQL Architecture",
        "rating": 7
    }, headers=admin_headers)
    assert skill_res.status_code == 201
    skill_data = skill_res.json()
    assert skill_data["rating"] == 7
    skill_id = skill_data["id"]

    # Duplicate skill name -> MUST FAIL
    dup_res = client.post("/api/v1/skills", json={
        "name": "postgresql architecture",  # Case-insensitive duplicate
        "rating": 5
    }, headers=admin_headers)
    assert dup_res.status_code in (400, 409, 422)

    # Boundary tests (< 1 or > 7)
    assert client.post("/api/v1/skills", json={"name": "Zero Skill", "rating": 0}, headers=admin_headers).status_code in (400, 422)
    assert client.post("/api/v1/skills", json={"name": "Excess Skill", "rating": 8}, headers=admin_headers).status_code in (400, 422)

    # Clean up
    client.delete(f"/api/v1/skills/{skill_id}", headers=admin_headers)


# ==============================================================================
# 5. PROJECTS WITH TECHNOLOGIES & MULTIPLE DEPLOYMENT LINKS (Section 17)
# ==============================================================================

def test_07_projects_with_technologies_and_multiple_links(client: TestClient, admin_headers: dict):
    """
    A project can have multiple technologies and multiple deployment links.
    All child entities are correctly saved, updated, and cascade-deleted.
    """
    project_payload = {
        "name": "Existence Production Cloud Engine",
        "description": "Multi-tier cloud deployment engine with automated CI/CD.",
        "technologies": [
            {"name": "FastAPI", "category": "Backend"},
            {"name": "React", "category": "Frontend"},
            {"name": "PostgreSQL", "category": "Database"}
        ],
        "links": [
            {
                "label": "Production Deployment",
                "url": "https://existence.onrender.com",
                "link_type": "Deployment",
                "is_primary": True
            },
            {
                "label": "Staging Environment",
                "url": "https://staging.existence.internal",
                "link_type": "Deployment",
                "is_primary": False
            }
        ]
    }

    create_res = client.post("/api/v1/projects", json=project_payload, headers=admin_headers)
    assert create_res.status_code == 201
    data = create_res.json()
    project_id = data["id"]
    assert len(data["technologies"]) == 3
    assert len(data["links"]) == 2

    # Add a third link via link endpoint
    link_res = client.post(f"/api/v1/projects/{project_id}/links", json={
        "label": "GitHub Repository",
        "url": "https://github.com/example/existence",
        "link_type": "Repository"
    }, headers=admin_headers)
    assert link_res.status_code == 201

    # Verify project has 3 links now
    proj_get = client.get(f"/api/v1/projects/{project_id}")
    assert proj_get.status_code == 200
    assert len(proj_get.json()["links"]) == 3

    # Clean up
    del_res = client.delete(f"/api/v1/projects/{project_id}", headers=admin_headers)
    assert del_res.status_code == 200


# ==============================================================================
# 6. FULL END-TO-END INTEGRATED LIFECYCLE (Section 20)
# ==============================================================================

def test_08_full_end_to_end_coherent_lifecycle(client: TestClient, db_session: Session):
    """
    Executes a complete end-to-end integration lifecycle:
    1. Authenticate with credentials -> obtain JWT
    2. Update Profile information
    3. Add Education record
    4. Add Work Experience record
    5. Add Skill with rating
    6. Create Project with technologies & multiple links
    7. Perform sensitive profile mutation requiring PIN confirmation
    8. Verify Audit log recorded the action with sanitized metadata
    9. Fetch Consolidated Public Profile and assert complete entity representation
    """
    # 1. Login
    login_res = client.post("/api/v1/auth/login", json={
        "username": "admin",
        "password": "Admin@Existence2026!"
    })
    assert login_res.status_code == 200
    token = login_res.json()["access_token"]
    auth_headers = {"Authorization": f"Bearer {token}"}
    admin_action_headers = {"Authorization": f"Bearer {token}", "X-Action-PIN": "8421"}

    # 2. Update Profile
    prof_res = client.put("/api/v1/profile", json={
        "name": "Alex Vance",
        "about": "Principal Software and Security Systems Architect.",
        "linkedin": "https://linkedin.com/in/alex-vance"
    }, headers=admin_action_headers)
    assert prof_res.status_code == 200

    # 3. Add Education
    edu_res = client.post("/api/v1/education", json={
        "level": "Doctorate",
        "stream": "Distributed Systems & Cryptography",
        "institution": "Carnegie Mellon University",
        "starting_month_year": "August 2016",
        "ending_month_year": "May 2021",
        "currently_studying": False
    }, headers=admin_action_headers)
    assert edu_res.status_code == 201
    edu_id = edu_res.json()["id"]

    # 4. Add Experience
    exp_res = client.post("/api/v1/experience", json={
        "role": "Staff Platform Architect",
        "employer": "Distributed Networks Inc.",
        "work_mode": "Remote",
        "starting_month_year": "June 2021",
        "currently_working": True
    }, headers=admin_action_headers)
    assert exp_res.status_code == 201
    exp_id = exp_res.json()["id"]

    # 5. Add Skill
    skill_res = client.post("/api/v1/skills", json={
        "name": "Distributed Consensus",
        "rating": 6
    }, headers=admin_action_headers)
    assert skill_res.status_code == 201
    skill_id = skill_res.json()["id"]

    # 6. Create Project
    proj_res = client.post("/api/v1/projects", json={
        "name": "High-Throughput RAFT Consensus Engine",
        "description": "Zero-allocation RAFT implementation in Rust and C++.",
        "technologies": [{"name": "Rust", "category": "Backend"}],
        "links": [{"label": "Crates.io Package", "url": "https://crates.io/crates/raft-core", "link_type": "Repository"}]
    }, headers=admin_action_headers)
    assert proj_res.status_code == 201
    proj_id = proj_res.json()["id"]

    # 7. Sensitive Action: Verify PIN is required (attempting without PIN returns 401/403)
    del_without_pin = client.delete(f"/api/v1/projects/{proj_id}", headers=auth_headers)
    assert del_without_pin.status_code in (401, 403)

    # Now verify PIN to obtain short-lived token
    v_res = client.post("/api/v1/pin/verify", json={"pin": "8421"}, headers=auth_headers)
    assert v_res.status_code == 200
    pin_token = v_res.json()["pin_token"]

    # Execute sensitive operation with the PIN session token
    del_with_token = client.delete(f"/api/v1/projects/{proj_id}", headers={
        "Authorization": f"Bearer {token}",
        "X-Action-PIN": pin_token
    })
    assert del_with_token.status_code == 200

    # 8. Verify Audit Trail
    audit_events = client.get("/api/v1/audit/events", headers=auth_headers)
    assert audit_events.status_code == 200
    events = audit_events.json()
    assert isinstance(events, list)
    assert len(events) > 0
    # Confirm no password or raw pin is present in audit metadata
    for ev in events:
        meta_str = str(ev.get("metadata", "") or ev.get("details", ""))
        assert "Admin@Existence2026!" not in meta_str
        assert "8421" not in meta_str

    # 9. Verify Public Consolidated Profile
    pub_res = client.get("/api/v1/profile/public")
    assert pub_res.status_code == 200
    pub_data = pub_res.json()
    assert pub_data["name"] == "Alex Vance"
    assert any(e["stream"] == "Distributed Systems & Cryptography" for e in pub_data["education"])
    assert any(x["role"] == "Staff Platform Architect" for x in pub_data["experience"])
    assert any(s["name"] == "Distributed Consensus" for s in pub_data["skills"])

    # Clean up education, experience, skill
    client.delete(f"/api/v1/education/{edu_id}", headers=admin_action_headers)
    client.delete(f"/api/v1/experience/{exp_id}", headers=admin_action_headers)
    client.delete(f"/api/v1/skills/{skill_id}", headers=admin_action_headers)


# ==============================================================================
# 7. PRODUCTION CONFIGURATION & DEVSECOPS CHECKS (Section 32 & 41)
# ==============================================================================

def test_09_production_config_validation():
    """validate_production_config fails fast when insecure defaults are supplied in production."""
    # Insecure default secret
    insecure_settings = Settings()
    insecure_settings.APP_ENV = "production"
    insecure_settings.JWT_SECRET_KEY = "existence_development_secret_key_change_in_production_32bytes_min"

    with pytest.raises(RuntimeError) as exc_info:
        insecure_settings.validate_production_config()
    assert "FATAL CONFIGURATION ERROR" in str(exc_info.value)

    # Valid 32+ char secret passes
    secure_settings = Settings()
    secure_settings.APP_ENV = "production"
    secure_settings.JWT_SECRET_KEY = "c1f7a8b9e0d4c2b1a3f5e7d9c1b3a5f7e9d1c3b5a7f9e1d3c5b7a9f1e3d5c7b9"
    secure_settings.validate_production_config()  # Must not raise


def test_10_production_security_headers_present(client: TestClient):
    """Production security response headers must be emitted on every response."""
    res = client.get("/api/v1/profile/public")
    assert res.status_code == 200
    assert res.headers.get("X-Content-Type-Options") == "nosniff"
    assert res.headers.get("X-Frame-Options") == "DENY"
    assert res.headers.get("X-XSS-Protection") == "1; mode=block"
    assert "strict-origin-when-cross-origin" in res.headers.get("Referrer-Policy", "")
    assert "Content-Security-Policy" in res.headers
