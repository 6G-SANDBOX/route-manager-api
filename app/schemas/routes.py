# app/schemas/routes.py
import psutil
from pydantic import BaseModel, Field, model_validator
from pydantic.networks import IPvAnyNetwork, IPvAnyAddress
from datetime import datetime, timezone
from typing import Optional

class Route(BaseModel):
    to: IPvAnyNetwork = Field(..., description="Destination network or IP Address (e.g. 192.168.1.24, 192.168.1.0/24)")
    via: Optional[IPvAnyAddress] = Field(None, description="Gateway for the route")
    dev: Optional[str] = Field(None, description="Output NIC for the route")
    create_at: Optional[datetime] = Field(None, description="Timestamp of scheduled route creation")
    delete_at: Optional[datetime] = Field(None, description="Timestamp of scheduled route deletion")

    @model_validator(mode='after')
    def check_via_or_dev(cls, values):
        if not values.via and not values.dev:
            raise ValueError("Route must include at least one of 'via' or 'dev'.")
        return values

    @model_validator(mode='after')
    def check_dev_exists(cls, values):
        valid_interfaces =  psutil.net_if_addrs().keys()
        if values.dev and values.dev not in valid_interfaces:
            raise ValueError(f"Route dev: '{values.dev}' is not a valid network interface. Valid interfaces are: {list(valid_interfaces)}")
        return values

    @model_validator(mode='after')
    def check_create_at(cls, values):
        if not values.create_at:
            values.create_at = datetime.now(timezone.utc)
        elif values.create_at.tzinfo is None:
            raise ValueError(f"Route create_at timestamp: '{values.create_at}' must include timezone information")
        return values

    @model_validator(mode='after')
    def check_delete_at(cls, values):
        if values.delete_at:
            if values.delete_at.tzinfo is None:
                raise ValueError(f"Route create_at timestamp: '{values.delete_at}' must include timezone information")
            elif values.delete_at < datetime.now(timezone.utc):
                raise ValueError(f"Route delete_at timestamp: '{values.delete_at}' has already passed")
            elif values.delete_at < values.create_at:
                raise ValueError(f"Route delete_at timestamp: '{values.delete_at}' can't be set before create_at or present time")
        return values
