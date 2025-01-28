# app/db/database.py
from sqlmodel import SQLModel, create_engine
from app.db.models.routes import DBRoute
from app.core.config import settings


engine = create_engine(settings.DATABASE_URL, connect_args={"check_same_thread": False})

def create_db_and_tables() -> None:
    """
    Create SQLite file and tables
    """
    SQLModel.metadata.create_all(engine)
