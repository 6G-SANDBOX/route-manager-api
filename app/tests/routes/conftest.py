# app/tests/conftest.py
import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, create_engine
import atexit
import os
import asyncio
import threading

from app.main import app
from app.db.database import override_engine
from app.core.config import settings
from app.services.lifecycle import route_manager_loop

# in-memory test database
TEST_DATABASE_URL = "sqlite:///file::memory:?cache=shared"
test_engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False, "uri": True})

@pytest.fixture
def auth_header():
    return {"Authorization": f"Bearer {settings.APITOKEN}"}

@pytest.fixture(scope="function")
def client():
    # Override the engine globally
    override_engine(test_engine)

    # Clean tables before each test
    SQLModel.metadata.drop_all(test_engine)
    SQLModel.metadata.create_all(test_engine)

    # Run the loop in a thread asynchronously
    loop = asyncio.new_event_loop()
    thread = threading.Thread(target=loop.run_until_complete, args=(route_manager_loop(),), daemon=True)
    thread.start()

    # Return test client
    with TestClient(app) as c:
        yield c

# Remove the in-memory SQLite file after all tests
@atexit.register
def remove_fake_sqlite_file():
    GHOST_DB_FILENAME = "file::memory:"
    if os.path.exists(GHOST_DB_FILENAME):
        print(f"Deleting ghost SQLite file: {GHOST_DB_FILENAME}")
        os.remove(GHOST_DB_FILENAME)
