from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.api import deps
from app.db.database import get_db
from app.models.user import User
from app.schemas.tracking import TrackingRead, TrackingCreate
from app.services import tracking as tracking_service


router = APIRouter()


@router.get("/orders/{order_id}/tracking", response_model=List[TrackingRead])
async def get_order_tracking(
    order_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
) -> List[TrackingRead]:
    """
    User can view the tracking timeline for their own order.
    """
    return await tracking_service.get_tracking_timeline(
        db, order_id=order_id, user_id=current_user.id
    )


@router.post("/orders/{order_id}/tracking", response_model=TrackingRead)
async def update_order_tracking(
    order_id: UUID,
    tracking_in: TrackingCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_admin),
) -> TrackingRead:
    """
    Admin can update the tracking status and add a description.
    """
    return await tracking_service.create_tracking_entry(
        db, 
        order_id=order_id, 
        status=tracking_in.status, 
        description=tracking_in.description
    )
