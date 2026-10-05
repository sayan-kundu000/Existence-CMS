import os
import sys
import subprocess
import sqlite3

test_db = os.path.abspath(os.path.join(os.path.dirname(__file__), "test_fresh_migration.db"))
if os.path.exists(test_db):
    os.remove(test_db)

env = os.environ.copy()
# Format SQLite URL with forward slashes for Windows compatibility
env["DATABASE_URL"] = f"sqlite:///{test_db.replace(os.sep, '/')}"
env["PYTHONPATH"] = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
alembic_ini = os.path.join(backend_dir, "alembic.ini")

# 1. Test fresh upgrade to head
result = subprocess.run([sys.executable, "-m", "alembic", "-c", alembic_ini, "upgrade", "head"], cwd=backend_dir, env=env, capture_output=True, text=True)
print("Alembic upgrade output:\n", result.stdout)
if result.stderr:
    print("Alembic upgrade stderr:\n", result.stderr)
assert result.returncode == 0, f"Alembic upgrade failed with returncode {result.returncode}"

conn = sqlite3.connect(test_db)
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [r[0] for r in cursor.fetchall()]
conn.close()

print(f"Total tables created by migration: {len(tables)}")
print("Tables:", sorted(tables))

required_tables = [
    "profiles",
    "profile_emails",
    "educations",
    "work_experiences",
    "skills",
    "projects",
    "project_links",
    "technologies",
    "project_technologies",
    "project_skills",
    "hobbies",
    "interests",
    "admin_users",
    "auth_sessions",
    "pin_security",
    "pin_verification_sessions",
    "assessment_definitions",
    "assessment_questions",
    "assessment_sessions",
    "assessment_responses",
    "assessment_results",
    "personality_trait_scores",
    "soft_skill_records",
    "strength_records",
    "weakness_records",
    "content_revisions",
    "audit_events"
]

for req_table in required_tables:
    assert req_table in tables, f"Missing required table: {req_table}"

# 2. Test downgrade to base
down_res = subprocess.run([sys.executable, "-m", "alembic", "-c", alembic_ini, "downgrade", "base"], cwd=backend_dir, env=env, capture_output=True, text=True)
print("Downgrade returncode:", down_res.returncode)
assert down_res.returncode == 0, f"Alembic downgrade base failed: {down_res.stderr}"

# 3. Test re-upgrade to head
re_up_res = subprocess.run([sys.executable, "-m", "alembic", "-c", alembic_ini, "upgrade", "head"], cwd=backend_dir, env=env, capture_output=True, text=True)

print("Re-upgrade returncode:", re_up_res.returncode)
assert re_up_res.returncode == 0, f"Alembic re-upgrade head failed: {re_up_res.stderr}"

if os.path.exists(test_db):
    os.remove(test_db)

print(">>> Fresh database migration, downgrade, and re-upgrade tests SUCCESSFUL! <<<")
