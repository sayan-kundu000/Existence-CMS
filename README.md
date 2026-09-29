# EXISTENCE

> **Personal-Profile, Competency Mastery & Personality-Intelligence Platform**  
> *Engineered as a clean, intermediate-level full-stack modular monolith with a custom PIN-protected CMS.*

---

## 1. System Overview

**Existence** is an integrated software platform that unifies personal profile governance, academic and professional trajectory tracking, calibrated 7-level competency mastery ratings, and empirical psychological assessment engines (MBTI, DISC, Big Five / OCEAN) with a soft-skill synthesis layer.

Built strictly according to the **Master Architecture Specification**, the system adheres to the **Anti-Hallucination & Zero-Invention Content Rule**: the architecture, database schemas, APIs, validation rules, and CMS controls are fully operational, ready to accept genuine user information without requiring architectural modifications.

---

## 2. High-Level Architecture

```text
                    EXISTENCE
                        │
          ┌─────────────┴─────────────┐
          │                           │
       FRONTEND                  BACKEND API
  React 19 + TS + Vite         FastAPI + Pydantic v2
     Tailwind CSS                     │
          │                     ┌─────┴─────┐
          │                     │           │
          │                  SERVICES    DATABASE
          │                     │       PostgreSQL
          │                     │    (SQLite Dev Fallback)
          └──── REST API ───────┘
          (/api/v1 endpoints)
                        │
                    CUSTOM CMS
                        │
        ┌───────────────┴───────────────┐
   Admin Auth                     PIN Security
 (JWT + bcrypt)              (Lockout + Revisions)
```

---

## 3. Technology Stack

| Layer | Technologies |
| :--- | :--- |
| **Backend** | Python 3.11+, FastAPI, Pydantic v2, SQLAlchemy 2.0, Alembic, PyJWT, Bcrypt, Psycopg 3 |
| **Database** | PostgreSQL (Render production) / SQLite (zero-config local dev fallback) |
| **Frontend** | React 19, TypeScript, Vite, Tailwind CSS v4, Lucide Icons |
| **Security** | Salty bcrypt PIN hashing, JWT session bearer tokens, 5-attempt retry lockout, immutable version snapshots, audit event trail |
| **Deployment** | Render (Backend API + Managed PostgreSQL) & Vercel (Frontend SPA) |

---

## 4. Key Systems & Modules

### 4.1 Core Profile & Identity
- Supports personal coordinates: Name, Email addresses (multi-entry), Mobile Number, LinkedIn URL, and Executive Bio.
- Strictly provides clean empty states (`is_empty = true`) with zero fake personal data populated.

### 4.2 Education System with Conditional Rules
- Education levels: `Doctorate`, `Post Graduate`, `Graduate`, `Undergraduate`, `High School`, `Matriculation`.
- **Conditional Rule**:
  - When `Currently Studying = TRUE`: Ending Month & Year is disabled and set to `null`.
  - When `Currently Studying = FALSE`: Ending Month & Year is strictly required and validated on both frontend and backend API.

### 4.3 Work Experience with Conditional Rules
- Work modes: `On-site`, `Remote`, `Hybrid`.
- **Conditional Location Rule**:
  - `On-site` or `Hybrid`: Location is strictly required.
  - `Remote`: Location is optional (defaults to "Remote").
- **Current Employment Rule**:
  - `Currently Working = TRUE`: Ending Month & Year is disabled (`null`).
  - `Currently Working = FALSE`: Ending Month & Year is enabled and strictly required.

### 4.4 7-Level Skill Rating Engine
- Calibrated proficiency scale from Level 1 to Level 7:
  - **Level 1**: Beginner
  - **Level 2**: Novice
  - **Level 3**: Intermediate
  - **Level 4**: Proficient
  - **Level 5**: Advanced
  - **Level 6**: Expert
  - **Level 7**: Master
- Strict integer boundary validation (`1 <= rating <= 7`).
- Segmented visual progress bars with level-tailored glow aesthetics.

### 4.5 Personality Intelligence & Assessment Engine
- **Myers-Briggs Type Indicator (MBTI)**:
  - 16 bipolar Likert items assessing E/I, S/N, T/F, J/P dimensions.
  - Generates 4-letter type code (e.g. INTJ, ENFP), dimension percentages, and archetype title.
- **DISC Behavioral Framework**:
  - 16 items measuring Dominance (D), Influence (I), Steadiness (S), Conscientiousness (C).
  - Calculates primary/secondary traits and behavioral archetypes.
- **Big Five / OCEAN Model**:
  - 20 items assessing Openness, Conscientiousness, Extraversion, Agreeableness, Neuroticism.
- **Synthesis Layer**:
  - Automatically merges outputs across completed tests to synthesize **Key Soft Skills**, **Key Strengths**, and **Key Weaknesses/Growth Blindspots**.

### 4.6 Custom CMS & PIN Security
- Custom built from scratch (no Strapi, Sanity, or WordPress).
- Administrative authentication via JWT.
- **Dedicated PIN Security Layer**:
  - All content creation, updates, and deletions require security PIN authorization (`X-Action-PIN` header).
  - PIN hashed with bcrypt and domain salt.
  - Max 5 failed attempts before temporary account lockout.
  - Complete Content Revision snapshots (storing entity ID, action, previous JSON snapshot, current JSON snapshot, author).
  - Security audit log tracking logins, PIN checks, and data modifications.

---

## 5. 37-Chapter Master Roadmap Alignment

| Chapter | Component | Implementation Status |
| :--- | :--- | :--- |
| **01 - 03** | Master Foundation, Monorepo & System Architecture | Completed |
| **04 - 06** | Python Backend, Database Foundation & Alembic Migrations | Completed (`alembic upgrade head`) |
| **07 - 12** | Profile, Education, Experience, Skills & Hobbies Models | Completed (with conditional validators) |
| **13 - 17** | Custom CMS, Auth, PIN Security, Versioning & Audit | Completed (bcrypt PIN + JSON snapshots) |
| **18 - 22** | Personality Engine (MBTI, DISC, Big Five & Synthesis) | Completed (Standardized items & scoring) |
| **23 - 24** | REST API Architecture & Validation Contracts | Completed (FastAPI `/api/v1` routes) |
| **25 - 32** | Frontend Foundation, Profile, Journey, Skills, Tests & CMS UI | Completed (React 19 + TypeScript + Vite) |
| **33 - 34** | Security Hardening & Automated Testing Suite | Completed (100% pytest test suites pass) |
| **35 - 37** | Deployment Engineering, GitHub & Production Readiness | Completed (Render & Vercel ready) |

---

## 6. Local Quickstart

### Prerequisites
- Python 3.11 or higher
- Node.js 18+ and npm

### 6.1 Backend Setup
```bash
# 1. Navigate to backend directory
cd backend

# 2. Create virtual environment
python -m venv .venv

# 3. Activate virtual environment
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Run database migrations
alembic upgrade head

# 6. Start the API server
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```
- API Base: `http://127.0.0.1:8000/api/v1`
- Swagger UI Interactive Docs: `http://127.0.0.1:8000/docs`
- Health Endpoint: `http://127.0.0.1:8000/api/v1/health`

### 6.2 Frontend Setup
```bash
# 1. Navigate to frontend directory
cd frontend

# 2. Install dependencies
npm install

# 3. Start development server
npm run dev
```
- Frontend UI: `http://localhost:5173`

---

### 6.3 One-Command Docker Compose (Full Stack)
```bash
# Start PostgreSQL, FastAPI backend, and Nginx frontend in containers:
docker compose up --build -d
```
- Frontend UI: `http://localhost:3000`
- Backend API & Swagger: `http://localhost:8000/docs`
- PostgreSQL: `localhost:5432`

---

## 7. Default Administrative Credentials

Upon initial database initialization, a bootstrap admin is automatically seeded:
- **Username**: `admin`
- **Password**: `Admin@Existence2026!`
- **Initial PIN**: Not configured by default. Upon logging in, configure your 4 to 8 digit security PIN in the CMS to authorize content changes.

---

## 8. Automated Testing

Existence is thoroughly validated by both backend and frontend test suites:

### 8.1 Backend Test Suite (Pytest)
```bash
cd backend
.venv\Scripts\pytest tests/ -v
```

The backend test suite (42/42 passing test cases) validates:
- System Health check and correlation IDs
- Administrative authentication and JWT issuance
- PIN configuration, verification, failure counter, 15-minute session tokens, and lockout protection
- Profile empty-state verification and PIN-authorized updating
- Multi-email relational management, RFC validation, and primary email synchronization
- Education conditional validation rules (`currently_studying` suppressing end dates) and whitelisted levels
- Work Experience conditional validation rules (`work_mode` location and `currently_working` suppressing end dates)
- Skills 7-level rating boundaries (1 to 7) and label resolution (`Beginner` to `Master`)
- Separate Hobbies and Interests CRUD management
- MBTI, DISC, and Big Five assessment session execution and scoring
- Question bank integrity, exact counts, uniqueness, and psychometric dimension coverage
- Personality synthesis management (Key Soft Skills, Strengths, Weaknesses)
- Content revision tracking, snapshot diff inspection, and PIN-protected historical restore
- Immutable audit event logging and filtering

### 8.2 Frontend Test Suite (Node.js Test Runner)
```bash
cd frontend
npm test
npm run typecheck
npm run build
```

The frontend test suite (6/6 passing test cases) validates:
- Skills 7-level mastery scale invariants (Level 1 Beginner to Level 7 Master)
- Public routing and deep link resolution (`/`, `/about`, `/education`, `/experience`, `/skills`, `/personality`, `/interests`, `/contact`, `/admin`)
- Dynamic document title generation
- Active employment & education period display formatting ("Present" suppression)
- Work mode location resolution (remote vs physical)
- Public/private data boundary invariants (zero secret leakage)

---

## 9. Deployment Guide

### 9.1 Render Deployment (Backend)
1. Push repository to GitHub.
2. In Render Dashboard, click **New > Blueprint** and select this repository.
3. Render automatically picks up `backend/render.yaml`, provisioning:
   - Python Web Service
   - PostgreSQL Managed Database
4. Render runs `pip install -r requirements.txt`, applies `alembic upgrade head`, and starts `uvicorn`.

### 9.2 Vercel Deployment (Frontend)
1. Import repository into Vercel.
2. Set Root Directory to `frontend`.
3. Framework Preset: **Vite**.
4. Set Environment Variable:
   - `VITE_API_URL`: Your Render backend URL (e.g. `https://existence-backend.onrender.com`).
5. Deploy. SPA rewrites are pre-configured in `frontend/vercel.json`.

### 9.3 Containerized Production (Docker & Docker Compose)
Multi-stage Dockerfiles and compose files are provided for self-hosted or cloud VM environments:
```bash
docker compose up --build -d
```

### 9.4 Continuous Integration (GitHub Actions)
The repository includes automated CI in `.github/workflows/ci.yml`, running on every push and pull request to test both backend and frontend suites.

---

## 10. License & Security Notice

Never commit production `.env` files or secrets to public repositories. All sensitive content actions within Existence require authenticated sessions and verified cryptographic PIN authorization.
