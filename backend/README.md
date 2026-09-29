# Existence Backend — REST API, PostgreSQL & Core Business Logic

Existence is a production-grade personal-profile and personality-intelligence platform with custom CMS capabilities, seven-level skill ratings, multi-framework psychometric assessments (MBTI, DISC, Big Five / OCEAN), PIN-protected content authorization, and content versioning/audit logging.

---

## 1. Technology Stack

* **Runtime**: Python 3.12+ (supports Python 3.14)
* **Framework**: FastAPI (Async, OpenAPI, Swagger UI, ReDoc)
* **Server**: Uvicorn (ASGI)
* **Validation & Schemas**: Pydantic v2
* **ORM & Database**: SQLAlchemy 2.x with Psycopg 3
* **Database Target**: PostgreSQL for production (Render / Neon / Supabase), with zero-config SQLite support for local development
* **Schema Migrations**: Alembic
* **Authentication**: JWT (HS256) & Bcrypt password hashing
* **PIN Authorization**: Salted Bcrypt with domain prefixing, failed-attempt tracking, and automatic temporary lockout
* **Automated Testing**: Pytest & HTTPX (39/39 passing test cases across all 4 prompt suites)

---

## 2. Architecture & Directory Structure

Organized as a layered modular monolith:

```text
backend/
├── app/
│   ├── main.py                  # Application entry point, lifespan, CORS, error handling
│   ├── core/
│   │   ├── config.py            # Environment-aware Pydantic Settings
│   │   ├── database.py          # SQLAlchemy engine, connection pooling, session factory
│   │   ├── security.py          # Bcrypt hashing, PIN hashing, JWT encoding/decoding
│   │   ├── exceptions.py        # Domain-specific application exceptions
│   │   └── logging.py           # Structured logging with credential scrubbing
│   ├── api/
│   │   └── v1/
│   │       ├── router.py        # Centralized versioned route registration (/api/v1)
│   │       └── endpoints/       # Route handlers (profile, education, experience, skills,
│   │                            #   hobbies, interests, personality, auth, pin, cms, audit, health)
│   ├── models/                  # SQLAlchemy 2.x relational ORM models (21 tables)
│   ├── schemas/                 # Pydantic v2 request/response validation schemas
│   ├── repositories/            # Encapsulated data-access layer
│   ├── services/                # Core business logic (scoring, audit, revisions, PIN security)
│   ├── dependencies/            # Request-scoped dependencies (get_db, require_admin, require_pin)
│   ├── middleware/              # Correlation ID tracing & centralized error handling
│   └── utils/                   # Reusable utilities (date order validators)
├── alembic/                     # Database migrations
│   ├── env.py
│   └── versions/                # Versioned migration revisions
├── tests/                       # Automated Pytest suite
├── requirements.txt             # Production dependencies
├── alembic.ini                  # Alembic configuration
├── .env.example                 # Template for required environment variables
└── README.md                    # Backend documentation
```

---

## 3. Core Business Logic & Validation Rules

### Education Management
* **Supported Levels**: `Doctorate`, `Post Graduate`, `Graduate`, `Undergraduate`, `High School`, `Matriculation`.
* **Date Precedence**: Ending month & year cannot precede starting month & year.
* **Currently Studying Rule**: When `currently_studying = True`, `ending_month_year` is automatically cleared and must be null. When `currently_studying = False`, `ending_month_year` is strictly required.

### Work Experience Management
* **Supported Modes**: `On-site`, `Remote`, `Hybrid`.
* **Conditional Location Rule**: `On-site` and `Hybrid` positions strictly require a valid physical location. `Remote` positions automatically set location to `"Remote"`, preventing stale location data.
* **Date Precedence**: Ending date cannot precede starting date.
* **Currently Working Rule**: When `currently_working = True`, `ending_month_year` must be null. When past employment, `ending_month_year` is required.

### Seven-Level Skill Ratings
* **Rating Scale**: Authoritative integer ratings from 1 to 7:
  * `1` = Beginner
  * `2` = Novice
  * `3` = Intermediate
  * `4` = Proficient
  * `5` = Advanced
  * `6` = Expert
  * `7` = Master
* Any rating outside 1–7 (such as 0, 8, negative values, or strings) is strictly rejected with a 422 Validation Error.
* Includes optional category, optional description, visibility toggle, and ordering index.

### Personality Assessment Infrastructure
* **Lifecycle**: `NOT_STARTED` -> `IN_PROGRESS` -> `COMPLETED`.
* **Assessments Supported**:
  * **MBTI**: 4 dimensions (Extraversion/Introversion, Sensing/Intuition, Thinking/Feeling, Judging/Perceiving).
  * **DISC**: 4 dimensions (Dominance, Influence, Steadiness, Conscientiousness).
  * **Big Five (OCEAN)**: 5 dimensions (Openness, Conscientiousness, Extraversion, Agreeableness, Neuroticism).
* **Completion Integrity**: Incomplete sessions cannot be submitted or scored.
* **Atomic Persistence**: Completing an assessment executes an atomic transaction creating the `AssessmentResult` alongside normalized records in `PersonalityTraitScore`, `SoftSkillRecord`, `StrengthRecord`, and `WeaknessRecord`, while recalculating the synthesized personality layer.

### Security & PIN-Protected CMS
* **Zero Invention**: Initializes with safe, empty profile states (`is_empty=True`) rather than fictitious default identities.
* **Server-Side PIN Enforcement**: Destructive or content-modifying endpoints require administrator authentication AND a valid `X-Action-PIN` header.
* **Lockout Protection**: Exceeding the maximum allowed failed attempts (`PIN_MAX_FAILED_ATTEMPTS=5`) triggers an automatic temporary lockout (`PIN_LOCKOUT_MINUTES=15`).
* **Content Versioning & Auditing**: Every content mutation creates an immutable snapshot record in `ContentRevision` and logs the actor, IP, and timestamp in `AuditEvent`.

---

## 4. API Endpoints Catalog

All endpoints are mounted under `/api/v1`:

| Area | Method | Endpoint | Description | Auth / PIN |
|---|---|---|---|---|
| **Health** | `GET` | `/api/v1/health` | Health & DB readiness check | Public |
| **Auth** | `POST` | `/api/v1/auth/login` | Administrator login (returns JWT) | Public |
| **Auth** | `GET` | `/api/v1/auth/me` | Current authenticated user details | JWT |
| **Auth** | `POST` | `/api/v1/auth/logout` | Session termination | JWT |
| **PIN** | `GET` | `/api/v1/pin/status` | Current PIN configuration & lockout status | JWT |
| **PIN** | `POST` | `/api/v1/pin/setup` | Initial PIN configuration | JWT |
| **PIN** | `POST` | `/api/v1/pin/verify` | Verify PIN validity | JWT |
| **PIN** | `POST` | `/api/v1/pin/change` | Rotate PIN with current PIN check | JWT |
| **Profile** | `GET` | `/api/v1/profile` | Retrieve public profile | Public |
| **Profile** | `PUT` / `PATCH` | `/api/v1/profile` | Update profile information | JWT + PIN |
| **Education** | `GET` | `/api/v1/education` | List all education entries | Public |
| **Education** | `POST` | `/api/v1/education` | Create education record | JWT + PIN |
| **Education** | `GET` | `/api/v1/education/{id}` | Retrieve single education record | Public |
| **Education** | `PUT` / `PATCH` | `/api/v1/education/{id}` | Update education record | JWT + PIN |
| **Education** | `DELETE` | `/api/v1/education/{id}` | Delete education record | JWT + PIN |
| **Experience** | `GET` | `/api/v1/experience` | List all work experiences | Public |
| **Experience** | `POST` | `/api/v1/experience` | Create work experience record | JWT + PIN |
| **Experience** | `GET` | `/api/v1/experience/{id}` | Retrieve single experience record | Public |
| **Experience** | `PUT` / `PATCH` | `/api/v1/experience/{id}` | Update work experience record | JWT + PIN |
| **Experience** | `DELETE` | `/api/v1/experience/{id}` | Delete work experience record | JWT + PIN |
| **Skills** | `GET` | `/api/v1/skills` | List skills & 7-level ratings | Public |
| **Skills** | `POST` | `/api/v1/skills` | Create skill with 1–7 rating | JWT + PIN |
| **Skills** | `GET` | `/api/v1/skills/{id}` | Retrieve single skill record | Public |
| **Skills** | `PUT` / `PATCH` | `/api/v1/skills/{id}` | Update skill record | JWT + PIN |
| **Skills** | `DELETE` | `/api/v1/skills/{id}` | Delete skill record | JWT + PIN |
| **Skills** | `POST` | `/api/v1/skills/reorder` | Bulk update skill ordering | JWT + PIN |
| **Hobbies** | `GET` | `/api/v1/hobbies` | List hobbies | Public |
| **Hobbies** | `POST` | `/api/v1/hobbies` | Create hobby | JWT + PIN |
| **Hobbies** | `GET` | `/api/v1/hobbies/{id}` | Retrieve single hobby | Public |
| **Hobbies** | `PUT` / `PATCH` | `/api/v1/hobbies/{id}` | Update hobby | JWT + PIN |
| **Hobbies** | `DELETE` | `/api/v1/hobbies/{id}` | Delete hobby | JWT + PIN |
| **Interests** | `GET` | `/api/v1/interests` | List interests | Public |
| **Interests** | `POST` | `/api/v1/interests` | Create interest | JWT + PIN |
| **Interests** | `GET` | `/api/v1/interests/{id}` | Retrieve single interest | Public |
| **Interests** | `PUT` / `PATCH` | `/api/v1/interests/{id}` | Update interest | JWT + PIN |
| **Interests** | `DELETE` | `/api/v1/interests/{id}` | Delete interest | JWT + PIN |
| **Personality** | `GET` | `/api/v1/personality/assessments` | List assessment definitions | Public |
| **Personality** | `POST` | `/api/v1/personality/sessions` | Start an assessment session | Public |
| **Personality** | `GET` | `/api/v1/personality/sessions/{id}` | Check session progress | Public |
| **Personality** | `POST` | `/api/v1/personality/sessions/{id}/responses` | Save response batch (duplicate-safe) | Public |
| **Personality** | `POST` | `/api/v1/personality/sessions/{id}/complete` | Validate, score & persist results | Public |
| **Personality** | `GET` | `/api/v1/personality/results` | List all completed assessment results | Public |
| **Personality** | `GET` | `/api/v1/personality/results/{id}` | Retrieve single result | Public |
| **Personality** | `GET` | `/api/v1/personality/history` | Chronological assessment history | Public |
| **Personality** | `GET` | `/api/v1/personality/synthesis` | Synthesized soft skills & strengths | Public |
| **Personality** | `PUT` | `/api/v1/personality/synthesis` | Manually customize synthesis layer | JWT + PIN |
| **Audit** | `GET` | `/api/v1/audit/events` | Paginated audit trail | JWT |
| **Audit** | `GET` | `/api/v1/audit/revisions` | Paginated content version history | JWT |

---

## 5. Local Setup & Running

### Prerequisites
* Python 3.12+ (or compatible)
* Virtual environment tool (`venv` or `uv`)

### Installation Steps

```bash
# Navigate to backend directory
cd backend

# Create and activate virtual environment
python -m venv .venv
# On Windows PowerShell:
.venv\Scripts\Activate.ps1
# On Linux / macOS:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env

# Run database migrations
alembic upgrade head

# Start development server
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Interactive documentation is available at:
* Swagger UI: `http://127.0.0.1:8000/docs`
* ReDoc: `http://127.0.0.1:8000/redoc`

---

## 6. Running Automated Tests

Run the full Pytest test suite:

```bash
cd backend
pytest -v
```

All 29 test cases across Prompt 01, Prompt 02, and Prompt 03 validate:
* Standardized error response contracts (`{"error": {"code": ...}}`)
* Conditional education date ordering rules, levels, and currently-studying invariants
* Conditional work experience location and date ordering rules, modes, and currently-working invariants
* 1-to-7 skill rating bounds, invalid inputs, and label mappings
* Distinct Hobbies and Interests resource endpoints with PATCH
* Personality session lifecycle (`NOT_STARTED` -> `IN_PROGRESS` -> `COMPLETED`)
* Premature completion rejection
* Normalized trait score and soft-skill record persistence
* PIN security, failed-attempt tracking, and lockout protection
* Profile empty states and PATCH operations
* PostgreSQL relational integrity, unique constraints, and cascade behaviors
* Check constraints on ratings, months, years, and actions
* Multi-step transaction safety and rollback isolation
* Render PostgreSQL connection pool configuration

---

## 7. PostgreSQL Persistence Architecture & Migrations

Existence uses a relational, normalized, migration-driven PostgreSQL architecture implemented with SQLAlchemy 2.x and Psycopg 3.

### 7.1 Schema Domains & Models

| Domain | Table | Primary Key | Key Invariants & Constraints |
|---|---|---|---|
| **Profile** | `profiles` | `id` (int/uuid) | Zero-invention initial state (`is_empty=True`) |
| **Profile** | `profile_emails` | `id` (uuid) | RFC email validation regex, `display_order >= 0`, cascade on profile delete |
| **Education** | `education` | `id` (int) | Check constraint: `level IN ('Doctorate', 'Post Graduate', 'Graduate', 'Undergraduate', 'High School', 'Matriculation')`, `start_month/end_month BETWEEN 1 AND 12`, `start_year/end_year > 0`, `currently_studying = 1 -> end_month IS NULL`, `end >= start` |
| **Experience** | `work_experiences` | `id` (int) | Check constraint: `work_mode IN ('On-site', 'Remote', 'Hybrid')`, `On-site/Hybrid -> location != ''`, `currently_working = 1 -> end_month IS NULL`, `end >= start` |
| **Skills** | `skills` | `id` (int) | Check constraint: `rating >= 1 AND rating <= 7`, `display_order >= 0`, `length(trim(name)) > 0` |
| **Hobbies** | `hobbies` | `id` (int) | `display_order >= 0`, `length(trim(name)) > 0`, cascade on profile delete |
| **Interests** | `interests` | `id` (int) | `display_order >= 0`, `length(trim(name)) > 0`, cascade on profile delete |
| **Security** | `admin_users` | `id` (int) | `email` unique, `username` unique, bcrypt `password_hash`, no raw password stored |
| **Security** | `auth_sessions` | `id` (int/uuid) | `token_identifier` unique, cascade on user delete |
| **Security** | `pin_security` | `id` (int) | `user_id` unique FK, salted bcrypt `pin_hash`, failed attempt counter, lockout expiry |
| **Security** | `pin_verification_sessions` | `id` (uuid) | `verification_identifier` unique, time-limited token expiry |
| **Assessments** | `assessment_definitions` | `id` (str) | Versioned (`code`, `version`) uniqueness |
| **Assessments** | `assessment_questions` | `id` (str) | Ordering index, dimension code, scale type |
| **Assessments** | `assessment_sessions` | `id` (int) | Check constraint: `status IN ('NOT_STARTED', 'IN_PROGRESS', 'COMPLETED', 'ABANDONED')` |
| **Assessments** | `assessment_responses` | `id` (int) | Unique constraint: `(session_id, question_id)` prevents duplicate responses |
| **Assessments** | `assessment_results` | `id` (int) | `session_id` FK, structured summary JSONB |
| **Assessments** | `personality_trait_scores` | `id` (int) | Normalized dimension scores and normalized 0.0–1.0 values |
| **Assessments** | `soft_skill_records` | `id` (int) | Profile relationship, assessment source provenance |
| **Assessments** | `strength_records` | `id` (int) | Profile relationship, assessment source provenance |
| **Assessments** | `weakness_records` | `id` (int) | Profile relationship, assessment source provenance |
| **CMS & Audit** | `content_revisions` | `id` (int) | Check constraint: `action IN ('CREATE', 'UPDATE', 'DELETE', 'RESTORE', 'PATCH')`, sensitive field scrubber |
| **CMS & Audit** | `audit_events` | `id` (int) | Actor, entity, request ID, structured non-secret metadata |

### 7.2 Alembic Migration History

```text
e65b956aa4c4_initial_existence_schema (Base)
  ↓
002_profile_emails_and_data
  ↓
003_education_and_experience_domain
  ↓
004_skills_hobbies_interests_domain
  ↓
005_authentication_and_pin_security
  ↓
006_personality_assessments_domain
  ↓
007_content_revisions_and_audit_domain
  ↓
008_postgresql_indexes_and_integrity (Head)
```

### 7.3 Fresh Database Bootstrap

To bootstrap a brand new PostgreSQL database:
```bash
# 1. Set DATABASE_URL to your PostgreSQL connection string
export DATABASE_URL="postgresql+psycopg://user:password@host:5432/dbname"

# 2. Run migrations
alembic upgrade head

# 3. Start API
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

---

## 8. Render Deployment Instructions

### Service Specification
* **Environment**: Python 3
* **Build Command**:
  ```bash
  pip install -r requirements.txt && alembic upgrade head
  ```
* **Start Command**:
  ```bash
  uvicorn app.main:app --host 0.0.0.0 --port $PORT
  ```

### Required Production Environment Variables
Configure these in the Render dashboard under **Environment**:
* `APP_NAME`: `Existence`
* `APP_ENV`: `production`
* `DATABASE_URL`: Your PostgreSQL connection string (Render managed PostgreSQL or external PostgreSQL). Psycopg 3 handles `postgresql+psycopg://` automatically.
* `JWT_SECRET_KEY`: High-entropy random secret key (min 32 characters)
* `JWT_ALGORITHM`: `HS256`
* `ACCESS_TOKEN_EXPIRE_MINUTES`: `1440`
* `REFRESH_TOKEN_EXPIRE_DAYS`: `7`
* `PIN_MAX_FAILED_ATTEMPTS`: `5`
* `PIN_LOCKOUT_MINUTES`: `15`
* `CORS_ORIGINS`: Comma-separated list of allowed frontend domains (e.g. `https://existence.vercel.app`)
* `LOG_LEVEL`: `INFO`

---

## 9. Custom Admin CMS, CRUD & PIN Security (Prompt 04)

The custom administrative CMS provides comprehensive data governance across all 11 domains:

```text
Admin Panel / CMS
│
├── Dashboard (Real-time DB Counts: Education, Experience, Skills, Hobbies, Interests, Revisions, Security Events)
├── Profile (Personal Coordinates + Relational Multi-Email Management)
├── Education (CRUD, Whitelisted Levels, Date Order, Currently Studying End Date Suppression)
├── Experience (CRUD, Work Modes, Conditional Physical Location, Currently Working End Date Suppression)
├── Skills (CRUD, Strict 1–7 Mastery Scale, Visual Rating Selectors)
├── Hobbies (CRUD, Ordering, Visibility Toggles, Normalized Table)
├── Interests (CRUD, Ordering, Category, Normalized Table)
├── Personality (Assessment Status, Trait Scores, Key Soft Skills, Strengths, Weaknesses Synthesis Editor)
├── Revisions (ContentRevision History, Expandable JSON Diff Inspection, Transaction-Safe Snapshot Restore)
├── Audit Log (Immutable Security Audit Events, Search & Action Filtering, Zero Edit Capability)
└── PIN Security (Cryptographic Salted Hash, 15-Minute Session Tokens, Failed Attempt Tracker, Lockout Defense)
```

### 9.1 CMS API Endpoints Reference

| Endpoint | Method | Security Requirements | Description |
|---|---|---|---|
| `/api/v1/cms/dashboard` | `GET` | Bearer Token (`Admin`) | Real-time counts (zero fake statistics) and recent events |
| `/api/v1/profile` | `GET`, `PUT`, `PATCH` | Bearer + PIN | Profile coordinates management |
| `/api/v1/profile/emails` | `GET`, `POST` | Bearer Token | Relational multi-email listing and creation |
| `/api/v1/profile/emails/{id}` | `PUT`, `DELETE` | Bearer + PIN (on delete) | Relational email update, primary synchronization, and delete |
| `/api/v1/education` | `GET`, `POST` | Bearer + PIN (on create) | Whitelisted levels, date precedence, currently-studying rules |
| `/api/v1/education/{id}` | `GET`, `PUT`, `PATCH`, `DELETE` | Bearer + PIN (on delete) | Education item modification and deletion |
| `/api/v1/experience` | `GET`, `POST` | Bearer + PIN (on create) | Work mode rules, location requirement, currently-working rules |
| `/api/v1/experience/{id}` | `GET`, `PUT`, `PATCH`, `DELETE` | Bearer + PIN (on delete) | Work experience modification and deletion |
| `/api/v1/skills` | `GET`, `POST` | Bearer + PIN (on create) | Strict 1–7 rating mastery scale (`Beginner` to `Master`) |
| `/api/v1/skills/{id}` | `GET`, `PUT`, `PATCH`, `DELETE` | Bearer + PIN (on delete) | Skill level updates and deletion |
| `/api/v1/hobbies` | `GET`, `POST` | Bearer + PIN (on create) | Hobbies collection management |
| `/api/v1/hobbies/{id}` | `GET`, `PUT`, `PATCH`, `DELETE` | Bearer + PIN (on delete) | Hobby updates and deletion |
| `/api/v1/interests` | `GET`, `POST` | Bearer + PIN (on create) | Interests collection management |
| `/api/v1/interests/{id}` | `GET`, `PUT`, `PATCH`, `DELETE` | Bearer + PIN (on delete) | Interest updates and deletion |
| `/api/v1/personality/synthesis` | `GET`, `PUT` | Bearer + PIN (on update) | Key soft skills, strengths, weaknesses, and summary notes |
| `/api/v1/audit/revisions` | `GET` | Bearer Token (`Admin`) | Paginated revision history with before/after state snapshots |
| `/api/v1/audit/revisions/{id}/restore` | `POST` | Bearer + PIN (`Admin`) | Restores historical snapshot, creates new RESTORE revision |
| `/api/v1/audit/events` / `/logs` | `GET` | Bearer Token (`Admin`) | Filterable, immutable security and mutation audit trail |
| `/api/v1/pin/verify` | `POST` | Bearer Token | Verifies PIN and issues 15-minute `PinVerificationSession` token |

### 9.2 PIN Verification Session Token Lifecycle

```text
Admin Login
   │
   ▼
POST /api/v1/pin/verify (with { "pin": "8421" })
   │
   ▼
Server validates salted bcrypt hash, creates PinVerificationSession in PostgreSQL:
- verification_identifier: UUID4 token string
- expires_at: UTC now + 15 minutes
- is_revoked: false
   │
   ▼
Returns: { "success": true, "pin_token": "<UUID4>" }
   │
   ▼
Subsequent Sensitive Mutations (Delete, Restore, Security Settings)
Headers:
- Authorization: Bearer <JWT>
- X-Action-PIN: <UUID4 pin_token> (or raw PIN)
   │
   ▼
Backend checks active, unexpired, unrevoked session token -> Authorized!
```

