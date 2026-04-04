from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict


class TrackingBase(BaseModel):
    status: str
    description: Optional[str] = None


class TrackingCreate(TrackingBase):
    pass


class TrackingRead(TrackingBase):
    id: UUID
    order_id: UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
