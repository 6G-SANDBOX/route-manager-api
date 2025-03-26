from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

class DeletedRoute(SQLModel, table=True):
    __tablename__ = "deleted_routes"

    id: Optional[int] = Field(default=None, primary_key=True)
    to: Optional[str] = Field(default=None, index=True)
    via: Optional[str] = None
    dev: Optional[str] = None
    create_at: Optional[datetime] = None
    delete_at: Optional[datetime] = None
    removed_at: datetime = Field(default_factory=datetime.utcnow)
    status: Optional[str] = None
