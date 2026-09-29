"""Product/Item Controller - CRUD operations for products."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from app.core.database import get_db
from app.models.sqlalchemy_models import Product
from app.schemas import (
    ProductResponse,
    ProductCreate,
    ProductUpdate,
    MessageResponse,
)
from app.core.dependencies import get_current_admin
from app.controllers.log_controller import log_activity
from app.models.sqlalchemy_models import User


router = APIRouter(prefix="/products", tags=["Products"])


@router.get("/list", response_model=List[ProductResponse])
async def list_products(db: AsyncSession = Depends(get_db)):
    """List all active products (Public)."""
    result = await db.execute(select(Product).where(Product.is_active == True))
    products = result.scalars().all()
    return products


@router.post("/create", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(
    product_data: ProductCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    """Create a new product (Admin only)."""
    new_product = Product(
        name=product_data.name,
        description=product_data.description,
        price=product_data.price,
        stock=product_data.stock,
        category=product_data.category,
        is_active=True,
    )
    db.add(new_product)
    await db.flush()
    await db.refresh(new_product)

    await log_activity(
        db=db,
        user_id=current_user.id,
        user_email=current_user.email,
        action="create_product",
        resource="/products/create",
        method="POST",
        status_code=201,
    )

    return new_product


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product_details(
    product_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Get product details by ID (Public)."""
    result = await db.execute(select(Product).where(Product.id == product_id))
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.put("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: int,
    product_data: ProductUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    """Update a product (Admin only)."""
    result = await db.execute(select(Product).where(Product.id == product_id))
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    update_data = product_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(product, key, value)

    await db.flush()
    await db.refresh(product)

    await log_activity(
        db=db,
        user_id=current_user.id,
        user_email=current_user.email,
        action="update_product",
        resource=f"/products/{product_id}",
        method="PUT",
        status_code=200,
    )

    return product


@router.delete("/{product_id}", response_model=MessageResponse)
async def delete_product(
    product_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    """Delete a product (Admin only)."""
    result = await db.execute(select(Product).where(Product.id == product_id))
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    await db.delete(product)

    await log_activity(
        db=db,
        user_id=current_user.id,
        user_email=current_user.email,
        action="delete_product",
        resource=f"/products/{product_id}",
        method="DELETE",
        status_code=200,
    )

    return MessageResponse(message=f"Product {product_id} deleted successfully")