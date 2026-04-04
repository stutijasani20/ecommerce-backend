from typing import List, Optional, Tuple
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status

from app.models.cart import CartItem
from app.models.product import Product
from app.schemas.cart import CartItemCreate, CartItemUpdate


async def get_user_cart(db: AsyncSession, user_id: UUID) -> Tuple[List[CartItem], int, float]:
    """
    Get all items in user's cart with product details.
    Returns (items, total_count, total_price)
    """
    result = await db.execute(
        select(CartItem)
        .filter(CartItem.user_id == user_id)
        .options(selectinload(CartItem.product))
    )
    items = result.scalars().all()
    
    total_count = sum(item.quantity for item in items)
    total_price = sum(item.quantity * item.product.price for item in items)
    
    return items, total_count, total_price


async def add_to_cart(db: AsyncSession, user_id: UUID, item_in: CartItemCreate) -> CartItem:
    """
    Add a product to the cart or update quantity if it already exists.
    Includes stock validation.
    """
    # Check if product exists and has enough stock
    result = await db.execute(select(Product).filter(Product.id == item_in.product_id))
    product = result.scalar_one_or_none()
    
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    
    if product.stock < item_in.quantity:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Not enough stock. Available: {product.stock}"
        )
    
    # Check if item already in cart
    result = await db.execute(
        select(CartItem).filter(
            CartItem.user_id == user_id,
            CartItem.product_id == item_in.product_id
        )
    )
    db_item = result.scalar_one_or_none()
    
    if db_item:
        # Check stock for updated total quantity
        if product.stock < (db_item.quantity + item_in.quantity):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Not enough stock. Current in cart: {db_item.quantity}, Available: {product.stock}"
            )
        db_item.quantity += item_in.quantity
    else:
        db_item = CartItem(
            user_id=user_id,
            product_id=item_in.product_id,
            quantity=item_in.quantity
        )
        db.add(db_item)
    
    await db.commit()
    await db.refresh(db_item)
    
    # Reload with product relationship for response
    result = await db.execute(
        select(CartItem)
        .filter(CartItem.id == db_item.id)
        .options(selectinload(CartItem.product))
    )
    return result.scalar_one()


async def update_cart_item(
    db: AsyncSession, user_id: UUID, item_id: UUID, item_in: CartItemUpdate
) -> CartItem:
    """
    Update quantity of a cart item with stock validation.
    """
    result = await db.execute(
        select(CartItem)
        .filter(CartItem.id == item_id, CartItem.user_id == user_id)
        .options(selectinload(CartItem.product))
    )
    db_item = result.scalar_one_or_none()
    
    if not db_item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cart item not found")
    
    if db_item.product.stock < item_in.quantity:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Not enough stock. Available: {db_item.product.stock}"
        )
    
    db_item.quantity = item_in.quantity
    await db.commit()
    await db.refresh(db_item)
    return db_item


async def remove_cart_item(db: AsyncSession, user_id: UUID, item_id: UUID) -> None:
    """
    Remove an item from the cart.
    """
    result = await db.execute(
        delete(CartItem).filter(CartItem.id == item_id, CartItem.user_id == user_id)
    )
    if result.rowcount == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cart item not found")
    
    await db.commit()


async def clear_cart(db: AsyncSession, user_id: UUID) -> None:
    """
    Clear all items for a user.
    """
    await db.execute(delete(CartItem).filter(CartItem.user_id == user_id))
    await db.commit()
