# app/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

# Base Class for models
Base = declarative_base()
# Database connection
engine = create_engine(settings.DATABASE_URL, connect_args={"check_same_thread": False})
# Database session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
