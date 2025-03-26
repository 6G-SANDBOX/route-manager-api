# app/tests/conftest.py
import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, Session, create_engine
from app.main import app
from app.db.models.routes import DBRoute
from app.db.models.deleted_routes import DeletedRoute
from app.db.routes import get_routes_from_database  # si necesitas override
from app.core.config import settings


@pytest.fixture
def auth_header():
    return {"Authorization": f"Bearer {settings.APITOKEN}"}

# Memory temporary database
TEST_DATABASE_URL = "sqlite:///:memory:"
test_engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})

# We use a test session that will use this base
@pytest.fixture(name="session")
def session_fixture():
    SQLModel.metadata.create_all(test_engine)
    with Session(test_engine) as session:
        yield session

@pytest.fixture(name="client")
def client_fixture(session: Session):
    return TestClient(app)

