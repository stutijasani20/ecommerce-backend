from datetime import datetime
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict


class OrderItemBase(BaseModel):
    product_id: UUID
    quantity: int
    price: float


class OrderItemRead(OrderItemBase):
    id: UUID
    
    model_config = ConfigDict(from_attributes=True)


class OrderBase(BaseModel):
    total_amount: float
    status: str


class OrderCreate(BaseModel):
    # This might be empty if we always create from cart
    pass


class OrderRead(OrderBase):
    id: UUID
    user_id: UUID
    created_at: datetime
    items: List[OrderItemRead]

    model_config = ConfigDict(from_attributes=True)


class CheckoutSessionResponse(BaseModel):
    checkout_url: str
    order_id: UUID
