from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field
from app.schemas.product import ProductOut


class CartItemBase(BaseModel):
    product_id: UUID
    quantity: int = Field(..., gt=0)


class CartItemCreate(CartItemBase):
    pass


class CartItemUpdate(BaseModel):
    quantity: int = Field(..., gt=0)


class CartItemInDBBase(CartItemBase):
    id: UUID
    user_id: UUID

    model_config = ConfigDict(from_attributes=True)


class CartItem(CartItemInDBBase):
    pass


class CartItemDetail(CartItemInDBBase):
    product: ProductOut


class CartRead(BaseModel):
    items: List[CartItemDetail]
    total_items: int
    total_price: float
