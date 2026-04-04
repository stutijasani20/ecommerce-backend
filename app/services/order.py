from typing import List, Optional, Tuple
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status

from app.models.order import Order, OrderItem, OrderStatus
from app.models.product import Product
from app.models.cart import CartItem
from app.services import cart as cart_service
from app.services import tracking as tracking_service
from app.services import email as email_service


async def create_order_from_cart(db: AsyncSession, user_id: UUID) -> Order:
    """
    Creates an order from the user's cart, reserves stock, but DOES NOT clear the cart.
    """
    # 1. Get cart items
    items, total_count, total_price = await cart_service.get_user_cart(db, user_id)
    
    if not items:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Your cart is empty"
        )
    
    # 2. Check availability and reserve stock
    for item in items:
        available_stock = item.product.stock - item.product.reserved_stock
        if available_stock < item.quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Not enough stock for product '{item.product.name}'. Available: {available_stock}"
            )
        
        # Increment reserved_stock
        item.product.reserved_stock += item.quantity
    
    # 3. Create Order
    order = Order(
        user_id=user_id,
        total_amount=total_price,
        status=OrderStatus.PENDING
    )
    db.add(order)
    await db.flush()  # Get order.id
    
    # 4. Create OrderItems
    for item in items:
        order_item = OrderItem(
            order_id=order.id,
            product_id=item.product_id,
            quantity=item.quantity,
            price=item.product.price
        )
        db.add(order_item)
    
    await db.commit()
    await db.refresh(order)
    
    # Reload with items
    result = await db.execute(
        select(Order)
        .filter(Order.id == order.id)
        .options(selectinload(Order.items))
    )
    return result.scalar_one()


async def get_order(db: AsyncSession, order_id: UUID, user_id: UUID) -> Optional[Order]:
    """
    Get order by ID and user ID.
    """
    result = await db.execute(
        select(Order)
        .filter(Order.id == order_id, Order.user_id == user_id)
        .options(selectinload(Order.items))
    )
    return result.scalar_one_or_none()


async def handle_order_payment_success(db: AsyncSession, order_id: UUID) -> Order:
    """
    On payment success:
    - Update order status to PAID
    - Finalize stock: decrement 'stock' and decrement 'reserved_stock'
    - Clear user's cart
    """
    result = await db.execute(
        select(Order)
        .filter(Order.id == order_id)
        .options(selectinload(Order.items).selectinload(OrderItem.product))
    )
    order = result.scalar_one_or_none()
    
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    
    if order.status == OrderStatus.PAID:
        return order
        
    # Update status
    order.status = OrderStatus.PAID
    
    # Finalize stock for each item
    for item in order.items:
        # Physical stock decreases
        item.product.stock -= item.quantity
        # Reservation released
        item.product.reserved_stock -= item.quantity
    
    # Clear cart
    await cart_service.clear_cart(db, user_id=order.user_id)
    
    # Initialize tracking timeline
    await tracking_service.create_tracking_entry(
        db, order_id=order.id, status=OrderStatus.PAID, description="Payment confirmed. Order is being processed."
    )
    
    # Reload order with items and user for email
    result = await db.execute(
        select(Order)
        .filter(Order.id == order_id)
        .options(
            selectinload(Order.items).selectinload(OrderItem.product),
            selectinload(Order.user)
        )
    )
    order_full = result.scalar_one()
    
    # Send Notification Emails (Don't let email failure block order completion)
    try:
        await email_service.send_order_confirmation_email(order_full, order_full.user)
        await email_service.send_new_order_admin_alert(order_full, order_full.user)
    except Exception as e:
        # In a real app, you might want to log this or retry
        pass
    
    await db.commit()
    await db.refresh(order)
    return order


async def handle_order_cancellation(db: AsyncSession, order_id: UUID) -> Order:
    """
    On cancellation/timeout:
    - Update status to CANCELLED
    - Release stock: decrement 'reserved_stock'
    """
    result = await db.execute(
        select(Order)
        .filter(Order.id == order_id)
        .options(selectinload(Order.items).selectinload(OrderItem.product))
    )
    order = result.scalar_one_or_none()
    
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
        
    if order.status != OrderStatus.PENDING:
        return order
        
    order.status = OrderStatus.CANCELLED
    
    # Release stock
    for item in order.items:
        item.product.reserved_stock -= item.quantity
        
    await db.commit()
    await db.refresh(order)
    return order
