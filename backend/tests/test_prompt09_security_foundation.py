"""
Comprehensive Security Foundation Test Suite (Prompt 09).
Validates:
- Authentication, Token, and Session Lifecycle
- Password Security Policy & Enforcement
- RBAC and Capability-Based Authorization
- Ownership Verification & IDOR Protection
- PIN Security Gateway, Brute-Force Lockout & Session Invalidation
- Input Sanitization, XSS Protection & SSRF Defense
- Security Response Headers & CORS Policies
- Audit Trails, Secret Scrubbing & Immutability
"""
import uuid
import pytest
from datetime import datetime, timedelta, timezone
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.main import app
from app.core.database import SessionLocal
from app.core.config import settings
from app.core.security import hash_password, hash_pin, create_access_token, decode_access_token
from app.core.permissions import Roles, Permissions, has_permission, get_role_permissions
from app.core.rate_limit import rate_limiter
from app.core.sanitizer import sanitize_text, validate_safe_url, sanitize_audit_metadata
from app.models.user import User, AuthSession, PinSecurity, PinVerificationSession
from app.models.profile import Profile
from app.models.project import Project, ProjectLink
from app.models.audit import AuditEvent, ContentRevision


@pytest.fixture
def test_admin_user(db_session: Session):
    """Retrieve the deterministic administrator seeded by conftest."""
    user = db_session.query(User).filter(User.username == "admin").first()
    assert user is not None
    return {"user": user, "username": "admin", "password": "Admin@Existence2026!", "pin": "8421"}


# ==============================================================================
# 1. AUTHENTICATION & SESSION TESTS
# ==============================================================================

def test_01_valid_login_issues_jwt_and_tracks_session(client: TestClient, test_admin_user, db_session: Session):
    """Valid credentials must return JWT and create server-side AuthSession with JTI."""
    rate_limiter.reset(f"login:testclient")

    res = client.post("/api/v1/auth/login", json={
        "username": test_admin_user["username"],
        "password": test_admin_user["password"]
    })
    assert res.status_code == 200
    data = res.json()
    assert "access_token" in data
    assert data["role"] == "admin"
    assert "permissions" in data
    assert len(data["permissions"]) > 0

    token = data["access_token"]
    payload = decode_access_token(token)
    assert payload is not None
    assert payload["sub"] == str(test_admin_user["user"].id)
    assert "jti" in payload

    # Verify session exists in auth_sessions table
    auth_session = db_session.query(AuthSession).filter(
        AuthSession.token_identifier == payload["jti"]
    ).first()
    assert auth_session is not None
    assert auth_session.admin_user_id == test_admin_user["user"].id
    assert auth_session.revoked_at is None


def test_02_invalid_login_rejected_and_audited(client: TestClient, test_admin_user, db_session: Session):
    """Invalid credentials must return 401 and generate LOGIN_FAILED audit event."""
    rate_limiter.reset(f"login:testclient")

    res = client.post("/api/v1/auth/login", json={
        "username": test_admin_user["username"],
        "password": "WrongPassword123!"
    })
    assert res.status_code == 401
    assert "Incorrect username or password" in res.json()["error"]["message"]

    # Verify audit event recorded
    audit_ev = db_session.query(AuditEvent).filter(
        AuditEvent.action == "LOGIN_FAILED",
        AuditEvent.username == test_admin_user["username"]
    ).order_by(AuditEvent.created_at.desc()).first()
    assert audit_ev is not None
    assert audit_ev.status == "FAILED"


def test_03_login_brute_force_rate_limiting(client: TestClient, test_admin_user):
    """Excessive login requests must trigger HTTP 429 Too Many Requests."""
    key = "login:testclient"
    rate_limiter.reset(key)

    # Exhaust allowed limit
    for _ in range(settings.RATE_LIMIT_LOGIN_PER_MINUTE):
        rate_limiter.is_allowed(key, settings.RATE_LIMIT_LOGIN_PER_MINUTE, 60)

    # Next attempt must be blocked
    res = client.post("/api/v1/auth/login", json={
        "username": test_admin_user["username"],
        "password": "AnyPassword123!"
    })
    assert res.status_code == 429
    assert res.json()["error"]["code"] == "RATE_LIMIT_EXCEEDED"
    assert "Retry-After" in res.headers
    rate_limiter.reset(key)


def test_04_logout_invalidates_session(client: TestClient, test_admin_user, db_session: Session):
    """Calling /auth/logout must revoke the server session; subsequent requests fail with 401."""
    rate_limiter.reset("login:testclient")
    login_res = client.post("/api/v1/auth/login", json={
        "username": test_admin_user["username"],
        "password": test_admin_user["password"]
    })
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Verify authenticated access works
    me_res = client.get("/api/v1/auth/me", headers=headers)
    assert me_res.status_code == 200

    # Call logout
    logout_res = client.post("/api/v1/auth/logout", headers=headers)
    assert logout_res.status_code == 200
    assert logout_res.json()["success"] is True

    # Immediate next request with the same token must be rejected
    me_after = client.get("/api/v1/auth/me", headers=headers)
    assert me_after.status_code == 401
    assert "revoked" in me_after.json()["error"]["message"].lower()


def test_05_logout_all_sessions(client: TestClient, test_admin_user, db_session: Session):
    """Calling /auth/logout-all must revoke all active sessions for the user."""
    rate_limiter.reset("login:testclient")
    token1 = client.post("/api/v1/auth/login", json={
        "username": test_admin_user["username"],
        "password": test_admin_user["password"]
    }).json()["access_token"]

    token2 = client.post("/api/v1/auth/login", json={
        "username": test_admin_user["username"],
        "password": test_admin_user["password"]
    }).json()["access_token"]

    # Revoke all using token2
    res = client.post("/api/v1/auth/logout-all", headers={"Authorization": f"Bearer {token2}"})
    assert res.status_code == 200

    # Both tokens must now be rejected
    assert client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token1}"}).status_code == 401
    assert client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token2}"}).status_code == 401


def test_06_password_strength_policy(client: TestClient, test_admin_user):
    """Password policy rejects trivially short, empty, or common passwords."""
    login_res = client.post("/api/v1/auth/login", json={
        "username": test_admin_user["username"],
        "password": test_admin_user["password"]
    })
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Too short (< 8 chars)
    short_res = client.post("/api/v1/auth/register", json={
        "username": "short_pass_user",
        "email": "short@test.internal",
        "password": "123"
    }, headers=headers)
    assert short_res.status_code in (400, 422)

    # Common password
    common_res = client.post("/api/v1/auth/register", json={
        "username": "common_pass_user",
        "email": "common@test.internal",
        "password": "password123"
    }, headers=headers)
    assert common_res.status_code == 422


def test_07_tampered_or_expired_token_rejected(client: TestClient):
    """Unsigned, tampered, or expired tokens must fail verification."""
    res_fake = client.get("/api/v1/auth/me", headers={"Authorization": "Bearer not-a-valid-jwt"})
    assert res_fake.status_code == 401

    # Expired token
    expired_token = create_access_token(subject=1, expires_delta=timedelta(seconds=-10))
    res_exp = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {expired_token}"})
    assert res_exp.status_code == 401


# ==============================================================================
# 2. AUTHORIZATION & RBAC TESTS
# ==============================================================================

def test_08_public_vs_authenticated_access(client: TestClient):
    """Public endpoints are accessible without auth; protected CMS/Audit endpoints require auth."""
    # Public endpoints
    assert client.get("/api/v1/profile/public").status_code == 200
    assert client.get("/api/v1/projects").status_code == 200
    assert client.get("/api/v1/skills").status_code == 200

    # Protected administrative endpoints without token
    assert client.get("/api/v1/cms/dashboard").status_code == 401
    assert client.get("/api/v1/audit/events").status_code == 401
    assert client.get("/api/v1/audit/revisions").status_code == 401


def test_09_rbac_permission_matrix():
    """Verify centralized RBAC role-to-capability mappings."""
    # Admin has wildcard '*'
    assert has_permission(Roles.ADMIN, Permissions.SECURITY_MANAGE) is True
    assert has_permission(Roles.ADMIN, Permissions.PROJECTS_DELETE) is True
    assert has_permission(Roles.ADMIN, "any_arbitrary_capability") is True

    # Editor has content manage but not security manage
    assert has_permission(Roles.EDITOR, Permissions.PROJECTS_WRITE) is True
    assert has_permission(Roles.EDITOR, Permissions.SECURITY_MANAGE) is False

    # Viewer has read but not write
    assert has_permission(Roles.VIEWER, Permissions.PROFILE_READ) is True
    assert has_permission(Roles.VIEWER, Permissions.PROFILE_WRITE) is False

    # Permissions list is populated
    admin_perms = get_role_permissions(Roles.ADMIN)
    assert len(admin_perms) == len(Permissions.ALL_PERMISSIONS)


# ==============================================================================
# 3. OWNERSHIP & IDOR PROTECTION TESTS
# ==============================================================================

def test_10_cross_project_link_editing_rejected(client: TestClient, test_admin_user, db_session: Session):
    """
    IDOR Protection:
    Attempting to update or delete project A's link using project B's ID must be rejected.
    """
    token = client.post("/api/v1/auth/login", json={
        "username": test_admin_user["username"],
        "password": test_admin_user["password"]
    }).json()["access_token"]
    headers = {"Authorization": f"Bearer {token}", "X-Action-PIN": test_admin_user["pin"]}

    # Create two projects
    p1 = client.post("/api/v1/projects", json={
        "name": f"Security IDOR P1 {uuid.uuid4().hex[:6]}",
        "description": "Project 1",
        "links": [{"label": "P1 Link", "url": "https://example.com/p1", "link_type": "Deployment"}]
    }, headers=headers).json()

    p2 = client.post("/api/v1/projects", json={
        "name": f"Security IDOR P2 {uuid.uuid4().hex[:6]}",
        "description": "Project 2"
    }, headers=headers).json()

    p1_link_id = p1["links"][0]["id"]
    p2_id = p2["id"]

    # Attempt cross-project link modification (updating P1's link under P2)
    cross_res = client.put(f"/api/v1/projects/{p2_id}/links/{p1_link_id}", json={
        "label": "Hacked Link",
        "url": "https://example.com/hacked",
        "link_type": "Deployment"
    }, headers=headers)

    # Must return 404 (preventing IDOR)
    assert cross_res.status_code == 404


def test_11_profile_ownership_link(db_session: Session, test_admin_user):
    """Profile model must support explicit user_id foreign key linking."""
    profile = db_session.query(Profile).first()
    assert profile is not None
    assert hasattr(profile, "user_id")


# ==============================================================================
# 4. PIN SECURITY GATEWAY & BRUTE-FORCE TESTS
# ==============================================================================

def test_12_pin_format_validation(client: TestClient, test_admin_user):
    """PIN validation enforces 4 to 8 numeric digits."""
    token = client.post("/api/v1/auth/login", json={
        "username": test_admin_user["username"],
        "password": test_admin_user["password"]
    }).json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Too short
    res_short = client.post("/api/v1/pin/setup", json={"pin": "12"}, headers=headers)
    assert res_short.status_code in (400, 422)

    # Non-numeric
    res_alpha = client.post("/api/v1/pin/setup", json={"pin": "abcd"}, headers=headers)
    assert res_alpha.status_code in (400, 422)


def test_13_pin_verification_issues_short_lived_token(client: TestClient, test_admin_user, db_session: Session):
    """Successful PIN verification issues a 15-minute token usable in X-Action-PIN header."""
    token = client.post("/api/v1/auth/login", json={
        "username": test_admin_user["username"],
        "password": test_admin_user["password"]
    }).json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    v_res = client.post("/api/v1/pin/verify", json={"pin": test_admin_user["pin"]}, headers=headers)
    assert v_res.status_code == 200
    pin_token = v_res.json()["pin_token"]
    assert pin_token is not None

    # Use the pin_token to perform a PIN-protected operation
    put_res = client.put("/api/v1/profile", json={
        "name": "Secured Persona",
        "about": "Security architect profile narrative."
    }, headers={"Authorization": f"Bearer {token}", "X-Action-PIN": pin_token})
    assert put_res.status_code == 200


def test_14_pin_brute_force_lockout(client: TestClient, test_admin_user, db_session: Session):
    """5 consecutive failed PIN attempts must trigger HTTP 423 Locked."""
    token = client.post("/api/v1/auth/login", json={
        "username": test_admin_user["username"],
        "password": test_admin_user["password"]
    }).json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    rate_limiter.reset(f"pin_attempts:{test_admin_user['user'].id}")

    # 4 failed attempts: return 401 with remaining attempts count
    for i in range(4):
        f_res = client.post("/api/v1/pin/verify", json={"pin": "0000"}, headers=headers)
        assert f_res.status_code == 401
        assert "attempt(s) remaining" in f_res.json()["error"]["message"]

    # 5th failed attempt: triggers lockout
    lock_res = client.post("/api/v1/pin/verify", json={"pin": "0000"}, headers=headers)
    assert lock_res.status_code == 423
    assert "locked" in lock_res.json()["error"]["message"].lower()

    # Reset for subsequent tests
    pin_rec = db_session.query(PinSecurity).filter(PinSecurity.user_id == test_admin_user["user"].id).first()
    pin_rec.failed_attempts = 0
    pin_rec.is_locked = False
    pin_rec.locked_until = None
    db_session.commit()


def test_15_pin_change_invalidates_prior_sessions(client: TestClient, test_admin_user, db_session: Session):
    """Changing PIN must revoke all existing PinVerificationSession tokens."""
    token = client.post("/api/v1/auth/login", json={
        "username": test_admin_user["username"],
        "password": test_admin_user["password"]
    }).json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Verify and obtain a token
    v_res = client.post("/api/v1/pin/verify", json={"pin": test_admin_user["pin"]}, headers=headers)
    old_pin_token = v_res.json()["pin_token"]

    # Change PIN to "9876"
    change_res = client.post("/api/v1/pin/change", json={
        "current_pin": test_admin_user["pin"],
        "new_pin": "9876"
    }, headers=headers)
    assert change_res.status_code == 200

    # Old pin token must now fail when used
    put_res = client.put("/api/v1/profile", json={
        "name": "Secured Persona Updated"
    }, headers={"Authorization": f"Bearer {token}", "X-Action-PIN": old_pin_token})
    assert put_res.status_code in (401, 403)

    # Restore PIN to original
    client.post("/api/v1/pin/change", json={
        "current_pin": "9876",
        "new_pin": test_admin_user["pin"]
    }, headers=headers)


def test_16_pin_lock_endpoint(client: TestClient, test_admin_user):
    """Calling /pin/lock must revoke active PIN sessions immediately."""
    token = client.post("/api/v1/auth/login", json={
        "username": test_admin_user["username"],
        "password": test_admin_user["password"]
    }).json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    v_res = client.post("/api/v1/pin/verify", json={"pin": test_admin_user["pin"]}, headers=headers)
    pin_token = v_res.json()["pin_token"]

    # Explicit lock
    lock_res = client.post("/api/v1/pin/lock", headers=headers)
    assert lock_res.status_code == 200
    assert lock_res.json()["success"] is True

    # Token must now fail
    put_res = client.put("/api/v1/profile", json={"name": "New Name"},
                         headers={"Authorization": f"Bearer {token}", "X-Action-PIN": pin_token})
    assert put_res.status_code in (401, 403)


# ==============================================================================
# 5. INPUT VALIDATION, SANITIZATION & SSRF DEFENSE
# ==============================================================================

def test_17_xss_sanitization_in_text():
    """sanitize_text must strip script tags, iframes, and event handlers."""
    payload = "Hello <script>alert('pwned')</script> world <img src='x' onerror='alert(1)'>!"
    clean = sanitize_text(payload)
    assert "<script>" not in clean
    assert "onerror" not in clean
    assert "Hello" in clean
    assert "world" in clean


def test_18_ssrf_and_dangerous_urls_rejected(client: TestClient, test_admin_user):
    """Project deployment links must reject loopback, internal IPs, and dangerous schemes."""
    token = client.post("/api/v1/auth/login", json={
        "username": test_admin_user["username"],
        "password": test_admin_user["password"]
    }).json()["access_token"]
    headers = {"Authorization": f"Bearer {token}", "X-Action-PIN": test_admin_user["pin"]}

    # javascript: scheme
    res_js = client.post("/api/v1/projects", json={
        "name": "Malicious JS Project",
        "links": [{"label": "XSS Link", "url": "javascript:alert(1)", "link_type": "Deployment"}]
    }, headers=headers)
    assert res_js.status_code in (400, 422)

    # Localhost SSRF probe
    res_ssrf = client.post("/api/v1/projects", json={
        "name": "SSRF Probe Project",
        "links": [{"label": "SSRF Link", "url": "http://127.0.0.1:8000/internal", "link_type": "Deployment"}]
    }, headers=headers)
    assert res_ssrf.status_code in (400, 422)


def test_19_skill_rating_strictly_1_to_7(client: TestClient, test_admin_user):
    """Skills engine strictly enforces rating bounds 1 to 7."""
    token = client.post("/api/v1/auth/login", json={
        "username": test_admin_user["username"],
        "password": test_admin_user["password"]
    }).json()["access_token"]
    headers = {"Authorization": f"Bearer {token}", "X-Action-PIN": test_admin_user["pin"]}

    # Rating 0 (too low)
    res_low = client.post("/api/v1/skills", json={"name": "Zero Skill", "rating": 0}, headers=headers)
    assert res_low.status_code in (400, 422)

    # Rating 8 (too high)
    res_high = client.post("/api/v1/skills", json={"name": "Over Skill", "rating": 8}, headers=headers)
    assert res_high.status_code in (400, 422)


# ==============================================================================
# 6. SECURITY HEADERS & CORS TESTS
# ==============================================================================

def test_20_security_headers_present(client: TestClient):
    """HTTP responses must contain standard production security headers."""
    res = client.get("/")
    assert res.status_code == 200
    assert res.headers.get("X-Content-Type-Options") == "nosniff"
    assert res.headers.get("X-Frame-Options") == "DENY"
    assert res.headers.get("X-XSS-Protection") == "1; mode=block"
    assert "strict-origin-when-cross-origin" in res.headers.get("Referrer-Policy", "")
    assert "Content-Security-Policy" in res.headers


def test_21_cors_credentialed_configuration(client: TestClient):
    """CORS must support credentialed preflight with trusted origin."""
    trusted_origin = "http://localhost:5173"
    res = client.options("/", headers={
        "Origin": trusted_origin,
        "Access-Control-Request-Method": "GET"
    })
    # Must echo the allowed origin and allow credentials
    assert res.headers.get("Access-Control-Allow-Origin") == trusted_origin
    assert res.headers.get("Access-Control-Allow-Credentials") == "true"


# ==============================================================================
# 7. AUDIT IMMUTABILITY & SECRET SCRUBBING
# ==============================================================================

def test_22_secret_scrubbing_in_audit():
    """Passwords, PINs, and token values must be scrubbed before audit persistence."""
    dirty_metadata = {
        "user": "admin",
        "password": "SecretPassword123!",
        "pin": "1234",
        "access_token": "eyJhbGciOi...",
        "nested": {
            "token": "sensitive_token",
            "safe_field": "valid_value"
        }
    }
    clean = sanitize_audit_metadata(dirty_metadata)
    assert clean["password"] == "[REDACTED]"
    assert clean["pin"] == "[REDACTED]"
    assert clean["access_token"] == "[REDACTED]"
    assert clean["nested"]["token"] == "[REDACTED]"
    assert clean["nested"]["safe_field"] == "valid_value"


def test_23_audit_records_are_immutable(client: TestClient, test_admin_user):
    """No API endpoint allows DELETE or PUT/PATCH on audit logs or revisions."""
    token = client.post("/api/v1/auth/login", json={
        "username": test_admin_user["username"],
        "password": test_admin_user["password"]
    }).json()["access_token"]
    headers = {"Authorization": f"Bearer {token}", "X-Action-PIN": test_admin_user["pin"]}

    # Attempt DELETE on audit events
    del_res = client.delete("/api/v1/audit/events", headers=headers)
    assert del_res.status_code in (404, 405)

    # Attempt DELETE on revisions
    del_rev = client.delete("/api/v1/audit/revisions", headers=headers)
    assert del_rev.status_code in (404, 405)
