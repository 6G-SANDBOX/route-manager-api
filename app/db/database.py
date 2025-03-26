# app/db/database.py
from sqlmodel import SQLModel, create_engine
from app.db.models.routes import DBRoute
from app.db.models.deleted_routes import DeletedRoute
from app.core.config import settings
from sqlalchemy.engine import Engine

# Default engine (used in normal app runtime)
_default_engine = create_engine(settings.DATABASE_URL, connect_args={"check_same_thread": False})

# Override engine (used in testing)
_override_engine: Engine | None = None

def get_engine() -> Engine:
    """
    Return the active SQL engine.
    If overridden (e.g., during testing), returns that one.
    Otherwise, returns the default engine.
    """
    return _override_engine or _default_engine

def override_engine(engine: Engine) -> None:
    """
    Override the default SQL engine.
    Used in tests to inject an in-memory database.
    """
    global _override_engine
    _override_engine = engine

def create_db_and_tables() -> None:
    """
    Create SQLite file and tables
    """
    SQLModel.metadata.create_all(get_engine())
