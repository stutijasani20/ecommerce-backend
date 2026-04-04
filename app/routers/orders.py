from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.api import deps
from app.db.database import get_db
from app.models.user import User
from app.schemas.order import OrderRead, CheckoutSessionResponse
from app.services import order as order_service
from app.services import stripe_service


router = APIRouter()


@router.post("/checkout", response_model=CheckoutSessionResponse)
async def create_order_and_checkout(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
) -> CheckoutSessionResponse:
    """
    1. Create an order from current user cart items (reserves stock).
    2. Create a Stripe checkout session.
    3. Return the checkout URL.
    """
    # Create the order
    order = await order_service.create_order_from_cart(db, current_user.id)
    
    # Create checkout session
    checkout_url = await stripe_service.create_checkout_session(order, current_user.email)
    
    return CheckoutSessionResponse(
        checkout_url=checkout_url,
        order_id=order.id
    )


@router.get("/{order_id}", response_model=OrderRead)
async def get_order_details(
    order_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
) -> OrderRead:
    """
    Retrieve details of a specific order for the current user.
    """
    order = await order_service.get_order(db, order_id=order_id, user_id=current_user.id)
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    return order
