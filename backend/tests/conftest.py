import os
os.environ["TESTING"] = "True"
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.database import Base, get_db
from app.core.security import hash_password, hash_pin
from app.models.user import User, PinSecurity
from app.models.profile import Profile
from app.models.assessment import PersonalitySynthesis
from app.main import app

from sqlalchemy import event, text
from sqlalchemy.pool import StaticPool

# In-memory SQLite for test isolation
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)


@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def db_session():
    session = TestingSessionLocal()

    # Seed baseline admin, profile, and synthesis in the isolated test transaction
    admin = User(
        username="admin",
        email="admin@existence.test",
        hashed_password=hash_password("Admin@Existence2026!"),
        role="admin",
        is_active=True
    )
    session.add(admin)
    session.flush()

    pin_rec = PinSecurity(
        user_id=admin.id,
        hashed_pin=hash_pin("8421"),
        is_configured=True,
        failed_attempts=0,
        is_locked=False
    )
    session.add(pin_rec)

    blank_profile = Profile(
        name=None,
        email_ids="[]",
        mobile_number=None,
        linkedin=None,
        about=None
    )
    session.add(blank_profile)

    blank_synthesis = PersonalitySynthesis(
        key_soft_skills="[]",
        key_strengths="[]",
        key_weaknesses="[]",
        summary_notes="Personality assessment not completed."
    )
    session.add(blank_synthesis)
    session.commit()

    yield session

    session.close()
    with engine.begin() as conn:
        conn.execute(text("PRAGMA foreign_keys=OFF;"))
        for table in reversed(Base.metadata.sorted_tables):
            conn.execute(table.delete())
        conn.execute(text("PRAGMA foreign_keys=ON;"))


@pytest.fixture()
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture()
def admin_headers(client):
    login_res = client.post("/api/v1/auth/login", json={"username": "admin", "password": "Admin@Existence2026!"})
    token = login_res.json()["access_token"]
    return {
        "Authorization": f"Bearer {token}",
        "X-Action-PIN": "8421"
    }
