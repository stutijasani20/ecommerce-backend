from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.api import deps
from app.db.database import get_db
from app.models.user import User
from app.schemas.product import Product, ProductCreate, ProductUpdate, ProductList
from app.services import product as product_service


router = APIRouter()


@router.get("/", response_model=ProductList)
async def list_products(
    db: AsyncSession = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    search: Optional[str] = Query(None),
) -> ProductList:
    """
    List products with pagination and search. (Public)
    """
    total, items = await product_service.list_products(
        db, skip=skip, limit=limit, search=search
    )
    return ProductList(total=total, items=items)


@router.get("/{id}", response_model=Product)
async def get_product(
    id: UUID,
    db: AsyncSession = Depends(get_db),
) -> Product:
    """
    Get a single product by ID. (Public)
    """
    db_product = await product_service.get_product(db, id=id)
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    return db_product


@router.post("/", response_model=Product, status_code=status.HTTP_201_CREATED)
async def create_product(
    product_in: ProductCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_admin),
) -> Product:
    """
    Create a new product. (Admin Only)
    """
    return await product_service.create_product(db, product_in=product_in)


@router.put("/{id}", response_model=Product)
async def update_product(
    id: UUID,
    product_in: ProductUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_admin),
) -> Product:
    """
    Update a product. (Admin Only)
    """
    db_product = await product_service.get_product(db, id=id)
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    return await product_service.update_product(db, db_product=db_product, product_in=product_in)


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(
    id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_admin),
) -> None:
    """
    Delete a product. (Admin Only)
    """
    db_product = await product_service.get_product(db, id=id)
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    await product_service.delete_product(db, db_product=db_product)
