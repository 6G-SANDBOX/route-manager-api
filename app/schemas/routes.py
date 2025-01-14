# app/schemas/routes.py
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class Route(BaseModel):
    destination: str
    gateway: Optional[str] = None
    interface: Optional[str] = None
    create_at: Optional[datetime] = None
    delete_at: Optional[datetime] = None

    class Config:
        from_attributes = True
