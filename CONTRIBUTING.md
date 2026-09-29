# Contributing to Existence

Thank you for your interest in contributing to **Existence**!

Existence is built as a clean, intermediate-level full-stack modular monolith adhering to the **Master Architecture Specification** and the **Anti-Hallucination & Zero-Invention Rule**.

---

## 1. Development Principles

1. **Anti-Hallucination Invariant**: Never commit fake, mock, or fabricated user data into production schemas or bootstrap seeds. The system boots into clean, validated empty states (`is_empty = true`).
2. **PIN Security Invariant**: All destructive mutations (delete, restore) and profile modifications must require explicit PIN authorization (`X-Action-PIN` header or 15-minute verification session token).
3. **Mastery Scale Invariant**: Skill ratings must strictly adhere to the calibrated 1 to 7 integer scale (`Beginner` to `Master`).
4. **Conditional Invariants**:
   - When `currently_studying = true` or `currently_working = true`, ending month & year must be `null`.
   - When false, ending month & year is strictly required and must not precede the starting date.
   - `On-site` and `Hybrid` positions require a physical location; `Remote` positions default location to `"Remote"`.

---

## 2. Local Setup & Testing

### Backend
```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Or .venv\Scripts\activate on Windows
pip install -r requirements.txt
alembic upgrade head
pytest tests/ -v
```

### Frontend
```bash
cd frontend
npm install
npm test
npm run typecheck
npm run build
```

---

## 3. Pull Request Guidelines

1. Ensure 100% of backend tests pass (`pytest tests/ -v`).
2. Ensure all frontend tests and type checks pass (`npm test && npm run typecheck`).
3. Follow conventional commits (`feat:`, `fix:`, `docs:`, `test:`, `refactor:`).
4. Verify that Docker builds succeed cleanly (`docker compose build`).
