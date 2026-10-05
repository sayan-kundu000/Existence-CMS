# Security Architecture, Threat Model & Governance Guide — Existence

This document specifies the unified security foundation for **Existence**, establishing the single, cross-cutting security infrastructure across all modules (`Profile`, `Skills`, `Projects`, `CMS`, `Personality`, `Assessment Data`, and future extensions).

---

## 1. Core Architectural Principle

> **"One Application, One Security Foundation"**

Security in Existence is a cross-cutting infrastructural layer, not a per-feature implementation. Protected functionality in every module delegates authentication, authorization, ownership verification, PIN confirmation, validation, and audit tracking to this centralized system.

```text
                        ┌────────────────────────────────────────┐
                        │        Centralized Security Core       │
                        │  (Auth, RBAC, PIN, RateLimit, Audit)   │
                        └───────────────────┬────────────────────┘
                                            │
        ┌───────────────┬───────────────────┼───────────────────┬───────────────┐
        ↓               ↓                   ↓                   ↓               ↓
     Profile          Skills             Projects              CMS         Personality
  (Bio/Edu/Exp)   (1-7 Mastery)   (Taxonomies/Links/SSRF)  (Revisions)  (Synthesis/Privacy)
        │               │                   │                   │               │
        └───────────────┴───────────────────┴───────────────────┴───────────────┘
                                            │
                                    Authoritative APIs
                                            │
                                 PostgreSQL / SQLAlchemy
```

---

## 2. Authentication & Session Architecture

### Identity & Token Model
1. **Password Security**:
   - Passwords hashed using Bcrypt with auto-salted rounds (`app.core.security.hash_password`).
   - Raw passwords never logged, cached, or returned in API responses.
   - Enforces minimum 8 chars, max 128 chars, non-empty, and rejects common weak passwords.
2. **Access Tokens**:
   - Signed JSON Web Tokens (JWT) using `HS256` and cryptographically random 64-byte `JWT_SECRET_KEY`.
   - Algorithm confusion prevented by strictly binding `algorithms=[settings.ALGORITHM]` during decoding.
   - Every token payload embeds:
     - `sub`: User ID
     - `username`: User identifier
     - `role`: Canonical RBAC role (`admin`, `editor`, `viewer`, `public`)
     - `jti`: Unique UUIDv4 token identifier for server-side state tracking
     - `exp`: Deterministic expiration timestamp
3. **Server-Side Session Tracking (`AuthSession`)**:
   - Each token `jti` is stored in the `auth_sessions` table with client IP, user agent, and creation timestamp.
   - Invalidation via `/api/v1/auth/logout` sets `revoked_at=utcnow()`. Subsequent requests with that JWT are rejected with `401 Unauthorized`.
   - Global revocation via `/api/v1/auth/logout-all` revokes all active sessions for the user across all devices.

---

## 3. Role-Based Authorization & Capabilities (RBAC)

Existence decouples roles from individual business operations using a capabilities-based permission matrix:

| Capability / Permission | Admin | Editor | Viewer | Public |
| :--- | :---: | :---: | :---: | :---: |
| `profile.read` | ✅ | ✅ | ✅ | ✅ (Public fields only) |
| `profile.write` | ✅ | ✅ | ❌ | ❌ |
| `skills.read` | ✅ | ✅ | ✅ | ✅ (Public skills only) |
| `skills.write` | ✅ | ✅ | ❌ | ❌ |
| `projects.read` | ✅ | ✅ | ✅ | ✅ (Published projects) |
| `projects.write` | ✅ | ✅ | ❌ | ❌ |
| `projects.delete` | ✅ | ❌ | ❌ | ❌ |
| `personality.read` | ✅ | ✅ | ❌ | ❌ |
| `personality.write` | ✅ | ❌ | ❌ | ❌ |
| `cms.manage` | ✅ | ✅ | ❌ | ❌ |
| `assessment.manage` | ✅ | ❌ | ❌ | ❌ |
| `audit.read` | ✅ | ❌ | ❌ | ❌ |
| `security.manage` | ✅ | ❌ | ❌ | ❌ |

- **Admin Wildcard**: The `admin` role automatically satisfies wildcard `*`, giving full management access.
- **Dependency Guard**: Routes declare capability dependencies:
  ```python
  @router.post("/items", dependencies=[Depends(require_permission(Permissions.PROJECTS_WRITE))])
  ```

---

## 4. Ownership Model & IDOR Protection

Frontend visibility is never treated as a security boundary. All entity-level mutations verify ownership server-side via `app.core.ownership`:

1. **Profile Ownership**:
   - Linked to `admin_users.id` via `profiles.user_id` foreign key.
   - `verify_profile_ownership(user, profile)` asserts `user.role == 'admin'` or `profile.user_id == user.id`.
2. **Project & Link Hierarchy**:
   - `verify_project_ownership(user, project)` ensures the authenticated user owns the parent project.
   - `verify_project_link_belongs_to_project(db, project_id, link_id)` strictly validates that `link_id` is a child of `project_id`. Attempting to modify Project A's link under Project B's URL path triggers `404 Not Found`.
3. **Skills, Education, & Experience**:
   - Verified against profile ownership before any update or deletion.

---

## 5. PIN Security Gateway (Dual-Factor Sensitive Action Protection)

Destructive and sensitive operations require secondary confirmation via a PIN.

```text
  Authenticated User
         ↓
  Sensitive Action (e.g. Delete Project, Update Profile Bio, Reset PIN)
         ↓
  PIN Gateway Check
  ├── Has valid X-Action-PIN header?
  │    ├── Direct Raw PIN: Verified via Bcrypt + Domain Salt
  │    └── Short-Lived PIN Token: Verified via PinVerificationSession table (15 min window)
  ├── 5 Failed Attempts? → HTTP 423 Locked (15 min temporary lockout)
  └── Success → Execute operation & emit scrubbed AUDIT event
```

### PIN Security Invariants:
- **Hashing**: PINs are never stored in plaintext. Hashed using Bcrypt with a domain salt (`existence_pin_salt_...`).
- **Format Validation**: Strictly 4 to 8 numeric digits (`^\d{4,8}$`).
- **Short-Lived Verification Session**: `/api/v1/pin/verify` issues a 15-minute token (`PinVerificationSession`), allowing rapid administrative work without re-entering the PIN on every keystroke.
- **PIN Change Invalidation**: Changing the PIN immediately revokes all prior `PinVerificationSession` tokens and audits the action.
- **Instant Revocation**: Users can click "Lock PIN" (`/api/v1/pin/lock`) to immediately terminate the sensitive session window.

---

## 6. Input Validation, XSS & SSRF Defense

1. **Input Validation**:
   - Pydantic v2 schemas enforce types, regex patterns, string length constraints, and bounded numbers.
   - Skill ratings strictly restricted to `1 <= rating <= 7`.
2. **Stored XSS Sanitization (`app.core.sanitizer.sanitize_text`)**:
   - User-supplied rich text, bios, and descriptions are sanitized using regular expressions that strip dangerous `<script>`, `<iframe>`, `<object>`, `<embed>`, and inline event handlers (`onerror=`, `onload=`, etc.).
   - Frontend renders using framework-safe JSX interpolation (`{text}`) without `dangerouslySetInnerHTML`.
3. **SSRF Defense (`app.core.sanitizer.validate_safe_url`)**:
   - Project deployment URLs and link endpoints only permit `http://` and `https://` schemes.
   - Prohibits dangerous schemes (`javascript:`, `data:`, `file:`, `vbscript:`).
   - Rejects loopback addresses (`127.0.0.1`, `localhost`, `::1`), link-local metadata addresses (`169.254.169.254`), and private IPv4 blocks (`10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`).
   - External links on the frontend always specify `rel="noopener noreferrer"` and `target="_blank"`.

---

## 7. Rate Limiting Architecture

A centralized thread-safe sliding window rate limiter protects endpoints against brute-force attacks:

- **Login Attempts**: 10 requests per minute per IP. Exceeding triggers `HTTP 429 Too Many Requests` with `Retry-After: 60`.
- **PIN Verification**: 5 requests per minute per User.
- **General APIs**: 60 requests per minute.
- **Reset on Success**: Valid authentication resets the attempt counter.

---

## 8. HTTP Security Headers & CORS Policy

### Security Headers (`SecurityHeadersMiddleware`)
Included on all API responses in staging and production:
- `X-Content-Type-Options: nosniff` — Prevents MIME-sniffing.
- `X-Frame-Options: DENY` — Prevents clickjacking in iframes.
- `X-XSS-Protection: 1; mode=block` — Enables legacy browser XSS filters.
- `Referrer-Policy: strict-origin-when-cross-origin` — Protects token and path leakage in referrer headers.
- `Permissions-Policy: camera=(), microphone=(), geolocation=()` — Restricts unneeded browser APIs.
- `Content-Security-Policy: default-src 'self'; script-src 'self'; ...` — Restricts script execution origins.

### CORS Configuration
- **No Wildcards with Credentials**: Does not use wildcard `*` with `allow_credentials=True`.
- **Explicit Allowed Origins**: Loaded from `CORS_ORIGINS` environment variable (e.g., `http://localhost:5173,https://*.vercel.app,https://*.onrender.com`).

---

## 9. Audit Logging & Revision Immutability

### Audit Trail (`AuditEvent`)
- Tracks actor (`user_id`, `username`), IP address, user agent, action, resource type, resource ID, status (`SUCCESS`, `FAILED`), and metadata.
- **Secret Scrubbing**: All metadata passes through `sanitize_audit_metadata()`, which recursively scrubs `password`, `pin`, `token`, `secret`, `authorization`, and `api_key` values to `[REDACTED]`.
- **Immutability**: Audit logs are append-only. There are no `UPDATE` or `DELETE` endpoints for audit records.

---

## 10. Security Threat Model & Mitigations

| Threat | Impact | Implemented Mitigation |
| :--- | :--- | :--- |
| **Credential Theft** | Account takeover | Bcrypt password hashing, minimum complexity, rate-limited login, no credential echoing. |
| **Session Hijacking / Stale Tokens** | Unauthorized persistent access | Server-side session tracking (`auth_sessions`), `/auth/logout` revocation, `/auth/logout-all` invalidation. |
| **PIN Brute Force** | Bypass of sensitive actions | 5-attempt limit, 15-minute temporary lockout (`HTTP 423`), salted Bcrypt hashing, format enforcement. |
| **Insecure Direct Object Reference (IDOR)** | Cross-tenant data tampering | `verify_profile_ownership`, `verify_project_ownership`, `verify_project_link_belongs_to_project`. |
| **Mass Assignment** | Privilege escalation | Explicit Pydantic schemas; protected fields (`id`, `user_id`, `role`, `created_at`) excluded from updates. |
| **Cross-Site Scripting (XSS)** | Token theft, session impersonation | Text sanitization regex filter, framework-safe React rendering, strict Content-Security-Policy. |
| **SQL Injection** | Database leakage | Parameterized queries via SQLAlchemy 2.0 ORM; zero string interpolation in SQL. |
| **Cross-Site Request Forgery (CSRF)** | Unauthorized state changes | Bearer JWT token authentication in `Authorization` header (immune to browser cookie CSRF). |
| **Server-Side Request Forgery (SSRF)** | Internal infrastructure probing | `validate_safe_url` blocks loopback, AWS metadata `169.254.169.254`, private subnets, and dangerous URI schemes. |
| **Open Redirects** | Phishing via trusted domain | No unvalidated redirection endpoints; frontend routes internally. |
| **Secret Leakage in Git / Logs** | System compromise | `.gitignore` filters `.env`, DBs, logs; `sanitize_audit_metadata` scrubs all audit records. |
| **Personality Data Exposure** | Privacy violation | Raw assessment responses restricted to authenticated owner; public API returns only verified synthesis. |

---

## 11. Production Deployment & DevSecOps Checklist

### Render (Backend)
- Set `APP_ENV=production`.
- Generate secure random 64-char hex strings for `JWT_SECRET_KEY`.
- Connect PostgreSQL via `postgresql+psycopg://...`.
- Set explicit `CORS_ORIGINS` to trusted Vercel frontend domains.
- Never commit `.env` to Git.

### Vercel (Frontend)
- Set `VITE_API_URL` to the Render backend URL (e.g. `https://existence-api.onrender.com`).
- Do not store backend secrets or service keys in client environment variables.
