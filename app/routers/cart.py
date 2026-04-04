from uuid import UUID
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.api import deps
from app.db.database import get_db
from app.models.user import User
from app.schemas.cart import CartItem, CartItemCreate, CartItemUpdate, CartRead
from app.services import cart as cart_service

router = APIRouter()


@router.get("/", response_model=CartRead)
async def get_cart(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
) -> CartRead:
    """
    Retrieve the current user's cart.
    """
    items, total_count, total_price = await cart_service.get_user_cart(
        db, user_id=current_user.id
    )
    return CartRead(
        items=items,
        total_items=total_count,
        total_price=total_price
    )


@router.post("/", response_model=CartItem, status_code=status.HTTP_201_CREATED)
async def add_to_cart(
    item_in: CartItemCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
) -> CartItem:
    """
    Add a product to the cart. If the product is already in the cart, 
    the quantity is incremented.
    """
    return await cart_service.add_to_cart(
        db, user_id=current_user.id, item_in=item_in
    )


@router.patch("/{item_id}", response_model=CartItem)
async def update_cart_item(
    item_id: UUID,
    item_in: CartItemUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
) -> CartItem:
    """
    Update the quantity of a specific cart item.
    """
    return await cart_service.update_cart_item(
        db, user_id=current_user.id, item_id=item_id, item_in=item_in
    )


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_from_cart(
    item_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
) -> None:
    """
    Remove an item from the cart.
    """
    await cart_service.remove_cart_item(
        db, user_id=current_user.id, item_id=item_id
    )


@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
async def clear_cart(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
) -> None:
    """
    Clear all items from the current user's cart.
    """
    await cart_service.clear_cart(db, user_id=current_user.id)
