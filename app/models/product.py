from sqlalchemy import Column, String, DateTime, func, Float, Integer, Text
from sqlalchemy.dialects.postgresql import UUID
import uuid
from app.db.database import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    name = Column(String, index=True, nullable=False)
    description = Column(Text)
    price = Column(Float, nullable=False)
    bulk_price = Column(Float)
    stock = Column(Integer, default=0)
    reserved_stock = Column(Integer, default=0)
    image_url = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
