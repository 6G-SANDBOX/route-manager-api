# app/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

# Database connection
engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False} if "sqlite" in settings.database_url else {})
# Database session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# Base Class for models
Base = declarative_base()
