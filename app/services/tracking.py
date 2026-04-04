from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from fastapi import HTTPException, status

from app.models.tracking import ShipmentTracking
from app.models.order import Order


async def create_tracking_entry(
    db: AsyncSession, order_id: UUID, status: str, description: Optional[str] = None
) -> ShipmentTracking:
    """
    Creates a new tracking entry and updates the corresponding order status.
    """
    # 1. Update Order status
    result = await db.execute(update(Order).where(Order.id == order_id).values(status=status))
    if result.rowcount == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    
    # 2. Create tracking entry
    tracking_entry = ShipmentTracking(
        order_id=order_id,
        status=status,
        description=description
    )
    db.add(tracking_entry)
    await db.commit()
    await db.refresh(tracking_entry)
    return tracking_entry


async def get_tracking_timeline(
    db: AsyncSession, order_id: UUID, user_id: UUID
) -> List[ShipmentTracking]:
    """
    Retrieves the tracking timeline for a specific order.
    Checks if the order belongs to the user or if user is admin.
    """
    # 1. Verify ownership (unless admin, but router handles admin check if needed)
    # Here we just check if order exists for this user
    order_result = await db.execute(select(Order).filter(Order.id == order_id, Order.user_id == user_id))
    order = order_result.scalar_one_or_none()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Order not found or access denied"
        )
    
    # 2. Fetch timeline
    result = await db.execute(
        select(ShipmentTracking)
        .filter(ShipmentTracking.order_id == order_id)
        .order_by(ShipmentTracking.created_at.asc())
    )
    return result.scalars().all()
