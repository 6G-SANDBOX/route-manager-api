# app/schemas/routes.py
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class Route(BaseModel):
    destination: str = Field(..., description="Destination network (e.g., 192.168.1.0/24)")
    gateway: Optional[str] = Field(None, description="Gateway for the route")
    interface: Optional[str] = Field(None, description="Interface for the route")
    create_at: Optional[datetime] = Field(None, description="Timestamp of scheduled route creation")
    delete_at: Optional[datetime] = Field(None, description="Timestamp of scheduled route deletion")

    class Config:
        from_attributes = True
