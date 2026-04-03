from typing import Optional, List
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class ProductBase(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    bulk_price: Optional[float] = None
    stock: Optional[int] = 0
    image_url: Optional[str] = None


class ProductCreate(ProductBase):
    name: str
    price: float


class ProductUpdate(ProductBase):
    pass


class ProductInDBBase(ProductBase):
    id: UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class Product(ProductInDBBase):
    pass


class ProductOut(ProductInDBBase):
    pass


class ProductList(BaseModel):
    total: int
    items: List[ProductOut]
