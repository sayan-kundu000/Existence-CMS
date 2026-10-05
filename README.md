# EXISTENCE

> **Personal-Profile, Competency Mastery, Projects Showcase & Personality-Intelligence Platform**  
> *Engineered as a clean, intermediate-level full-stack modular monolith with a centralized security foundation, PIN-protected CMS, and automated CI/CD.*

---

## 1. System Overview

**Existence** is a unified software platform that consolidates personal profile governance, academic and professional trajectory tracking, calibrated 7-level competency mastery ratings, a multi-tier projects engine with technology taxonomies and deployment links, and empirical psychological assessment engines (MBTI, DISC, Big Five / OCEAN) with an automated soft-skill synthesis layer.

The platform adheres to the **Anti-Hallucination & Zero-Invention Content Rule**: schemas, APIs, validation rules, and CMS controls are fully operational, ready to accept genuine user information without requiring architectural modifications.

---

## 2. High-Level Architecture

```text
                                    EXISTENCE
                                        │
                    ┌───────────────────┴───────────────────┐
                    │                                       │
                 FRONTEND                              BACKEND API
           React 19 + TS + Vite                   FastAPI + Pydantic v2
               Tailwind CSS                                 │
                    │                                ┌──────┴──────┐
                    │                                │             │
                    │                             SERVICES      DATABASE
                    │                                │         PostgreSQL
                    │                                │      (SQLite Dev Fallback)
                    └─────────── REST API ───────────┘
                             (/api/v1 endpoints)
                                        │
                        ┌───────────────┴───────────────┐
                        │    CENTRALIZED SECURITY CORE  │
                        ├───────────────────────────────┤
                        │ - JWT Auth & Session Tracking │
                        │ - Capability RBAC Matrix      │
                        │ - Salted Bcrypt PIN Gateway   │
                        │ - SSRF, XSS & IDOR Defense    │
                        │ - Sliding Window Rate Limit   │
                        │ - Immutable Audit Trail       │
                        └───────────────┬───────────────┘
                                        │
                                   CUSTOM CMS
```

---

## 3. Technology Stack

| Layer | Technologies |
| :--- | :--- |
| **Backend** | Python 3.11+, FastAPI, Pydantic v2, SQLAlchemy 2.0, Alembic, PyJWT, Bcrypt, Psycopg 3 |
| **Database** | PostgreSQL (Render production) / SQLite (zero-config local dev fallback) |
| **Frontend** | React 19, TypeScript, Vite, Tailwind CSS v4, Lucide Icons |
| **Security** | Centralized RBAC permissions, Bcrypt PIN hashing with domain salt, JWT session tracking with revocation, 5-attempt brute-force lockout, SSRF & XSS sanitization, production security headers |
| **Testing** | Pytest (116 tests), Node.js Test Runner (22 tests), TypeScript static analysis |
| **CI/CD & Deploy** | GitHub Actions (`ci.yml`), Render (API + PostgreSQL), Vercel (Frontend SPA), Docker Compose |

---

## 4. Key Systems & Modules

### 4.1 Core Profile & Identity
- Coordinates: Verified Name, Multi-entry Email Addresses, Mobile Number, LinkedIn URL, and Executive Bio.
- Clean empty states (`is_empty = true`) with zero placeholder or fictitious data.
- Linked to `admin_users` table via `profiles.user_id` foreign key.

### 4.2 Education System with Conditional Date Rules
- Levels: `Doctorate`, `Post Graduate`, `Graduate`, `Undergraduate`, `High School`, `Matriculation`.
- **Business Rule**:
  - `Currently Studying = TRUE`: Ending Month & Year is disabled and suppressed to `null`.
  - `Currently Studying = FALSE`: Ending Month & Year is strictly required and verified to be on or after start date.

### 4.3 Work Experience with Conditional Rules
- Modes: `On-site`, `Remote`, `Hybrid`.
- **Location Rule**: `On-site` and `Hybrid` require an explicit location; `Remote` automatically normalizes location to `"Remote"`.
- **Current Employment Rule**: `Currently Working = TRUE` suppresses ending date; `Currently Working = FALSE` strictly requires it.

### 4.4 7-Level Skill Rating Engine
- Calibrated proficiency scale from Level 1 to Level 7:
  - **Level 1**: Beginner | **Level 2**: Novice | **Level 3**: Intermediate | **Level 4**: Proficient
  - **Level 5**: Advanced | **Level 6**: Expert | **Level 7**: Master
- Strict integer boundary validation (`1 <= rating <= 7`).
- 17 canonical skill categories with multi-category mapping and deduplication.

### 4.5 Projects Engine with Technologies & Multiple Links
- Full CRUD for showcase projects with statuses (`Planned`, `In Progress`, `Completed`, `Archived`).
- **Technologies**: Categorized tech stack (Frontend, Backend, Database, Cloud/Deployment, DevOps, etc.).
- **Multiple Deployment Links**: Supports primary and secondary links (`Live Demo`, `Deployment`, `GitHub`, `Repository`, `Documentation`, `API`, `Video Demo`, `Case Study`, `Other`).
- **SSRF Defense**: Deployment URLs are validated to block private, loopback (`127.0.0.1`), link-local metadata (`169.254.169.254`), and dangerous schemes (`javascript:`, `data:`).

### 4.6 Personality Intelligence & Assessment Engine
- **MBTI**: 16 bipolar Likert items evaluating E/I, S/N, T/F, J/P; calculates dimension percentages and 4-letter type.
- **DISC**: 16 items assessing Dominance, Influence, Steadiness, Conscientiousness with primary/secondary traits.
- **Big Five / OCEAN**: 20 items assessing Openness, Conscientiousness, Extraversion, Agreeableness, Neuroticism.
- **Synthesis Layer**: Automatically generates Key Soft Skills, Key Strengths, and Key Weaknesses/Growth Blindspots.

### 4.7 Centralized Security, PIN Gateway & Audit Trail
- Single security layer cross-cutting all modules.
- **PIN Gateway**: Sensitive operations (e.g. project deletion, profile bio updates, PIN resets) require dual-factor PIN confirmation via `X-Action-PIN` header or short-lived `PinVerificationSession` token (15-minute window).
- **Brute-Force Protection**: 5 consecutive failed attempts trigger `HTTP 423 Locked` for 15 minutes.
- **Audit Immutability**: Append-only audit records with automatic scrubbing of passwords, PINs, tokens, and authorization headers (`[REDACTED]`).

---

## 5. Health & Observability Model

| Endpoint | Probe Type | Description | Expected Status |
| :--- | :--- | :--- | :--- |
| `/health` or `/api/v1/health` | **Liveness** | Checks that process is running | `200 OK` (`status: healthy`) |
| `/readiness` or `/api/v1/health/readiness` | **Readiness** | Validates database connectivity | `200 OK` (`status: ready`) or `503 Unavailable` (`status: not_ready`) |

*Health checks never expose credentials, connection strings, or internal traces.*

---

## 6. Local Quickstart

### Prerequisites
- Python 3.11+
- Node.js 18+ and npm

### 6.1 Backend Setup
```bash
# 1. Navigate to backend directory
cd backend

# 2. Create and activate virtual environment
python -m venv .venv
# Windows:
.\.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Apply database migrations
alembic upgrade head

# 5. Start development API server
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```
- API Base: `http://127.0.0.1:8000/api/v1`
- Swagger UI Documentation: `http://127.0.0.1:8000/docs`
- Health Liveness: `http://127.0.0.1:8000/health`
- Dependency Readiness: `http://127.0.0.1:8000/readiness`

### 6.2 Frontend Setup
```bash
# 1. Navigate to frontend directory
cd frontend

# 2. Install dependencies
npm install

# 3. Start Vite dev server
npm run dev
```
- Frontend UI: `http://localhost:5173`

### 6.3 One-Command Docker Compose (Full Stack)
```bash
docker compose up --build -d
```
- Frontend UI: `http://localhost:3000`
- Backend API: `http://localhost:8000/docs`
- PostgreSQL: `localhost:5432`

---

## 7. Default Administrative Credentials

Upon initial database initialization, a bootstrap admin account is automatically seeded:
- **Username**: `admin`
- **Password**: `Admin@Existence2026!`
- **Initial PIN**: `8421` (configurable via CMS PIN Management)

---

## 8. Automated Testing & Verification

### 8.1 Backend Test Suite (Pytest — 116 / 116 Passed)
```bash
cd backend
.\.venv\Scripts\pytest -v
```
Covers:
- `test_all_features.py` (9 tests)
- `test_prompt02_backend.py` (10 tests)
- `test_prompt03_database.py` (10 tests)
- `test_prompt04_cms.py` (10 tests)
- `test_prompt06_profile_engine.py` (10 tests)
- `test_prompt07_skills_engine.py` (10 tests)
- `test_prompt08_personality_engine.py` (10 tests)
- `test_prompt09_projects_engine.py` (11 tests)
- `test_prompt09_security_foundation.py` (23 tests)
- `test_prompt10_integration_production_readiness.py` (10 tests)
- `test_question_banks.py` (3 tests)

### 8.2 Frontend Test Suite (Node Test Runner — 22 / 22 Passed)
```bash
cd frontend
npm test
npm run typecheck
npm run build
```
Validates:
- 7-Level Mastery Scale invariants and clamping
- Public routing and deep link navigation
- Period formatters ("Present" suppression)
- Remote vs Physical work mode logic
- Public profile secret isolation
- Case-insensitive duplicate prevention
- Project technology deduplication & URL protocol security
- Complete MBTI (16 types), DISC, and Big Five psychometric calculation invariants

### 8.3 Migration Lifecycle Test
```bash
cd backend
python tests/verify_fresh_migration.py
```
Validates fresh upgrade from blank database, downgrade to base, and re-upgrade to head across all 30 database tables.

---

## 9. Production Deployment Guide

### 9.1 Render Deployment (Backend API + PostgreSQL)
1. Push repository to GitHub.
2. In Render Dashboard, click **New > Blueprint** and connect this repository.
3. Render reads `backend/render.yaml` and provisions:
   - Python Web Service: binds to `$PORT`, runs `alembic upgrade head`, starts `uvicorn`.
   - Managed PostgreSQL: automatically assigns connection string to `DATABASE_URL`.
4. Configure environment variables in Render:
   - `JWT_SECRET_KEY`: Set to a secure random 64-character hex string.
   - `CORS_ORIGINS`: Set to your Vercel frontend URL (e.g. `https://existence-app.vercel.app`).

### 9.2 Vercel Deployment (Frontend SPA)
1. Import repository into Vercel.
2. Set Root Directory to `frontend`.
3. Framework Preset: **Vite**.
4. Configure Environment Variable:
   - `VITE_API_URL`: Your Render backend URL (e.g. `https://existence-backend.onrender.com`).
5. Deploy. Client-side routing rewrites are pre-configured in `frontend/vercel.json`.

---

## 10. Release & Rollback Procedures

### Release Checklist
1. Verify all backend tests pass: `pytest tests/` (116 passing).
2. Verify all frontend tests pass: `npm test` (22 passing).
3. Verify TypeScript compiles cleanly: `npm run typecheck`.
4. Run production frontend build: `npm run build`.
5. Test fresh migration on empty database: `python tests/verify_fresh_migration.py`.
6. Confirm `.gitignore` excludes `.env`, `*.db`, `node_modules`, and build artifacts.
7. Push to `main` branch to trigger GitHub Actions CI.

### Rollback Strategy
- **Application Rollback**: In Render/Vercel dashboards, select previous successful deployment and click "Instant Rollback".
- **Database Migrations**: Backward-compatible schema design ensures old backend versions run on current schema. If downgrade is required: `alembic downgrade -1`.
