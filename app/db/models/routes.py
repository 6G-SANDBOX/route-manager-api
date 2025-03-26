from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

class DBRoute(SQLModel, table=True):
    __tablename__ = "saved_routes"
    to: str = Field(index=True, primary_key = True)
    via: Optional[str] = None
    dev: Optional[str] = None
    create_at: Optional[datetime] = None
    delete_at: Optional[datetime] = None
    active: bool
    status: Optional[str] = None
