# app/db/models/routes.py
from sqlalchemy import Column, String, DateTime
from app.db.database import Base

class RouteModel(Base):
    __tablename__ = "routes"
    destination = Column(String, primary_key=True, index=True)
    gateway = Column(String, index=True)
    interface = Column(String, index=True)
    create_at = Column(DateTime, index=True, nullable=True)
    delete_at = Column(DateTime, index=True, nullable=True)
