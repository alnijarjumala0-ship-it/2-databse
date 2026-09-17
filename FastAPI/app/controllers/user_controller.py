"""User Controller - CRUD operations for users (Admin only)."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from app.core.database import get_db
from app.core.security import get_password_hash
from app.models.sqlalchemy_models import User
from app.schemas import (
    UserResponse,
    UserUpdate,
    UserToggleAdmin,
    MessageResponse,
)
from app.core.dependencies import get_current_admin


router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/all", response_model=List[UserResponse])
async def get_all_users(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_admin),
):
    """Get all users (Admin only)."""
    result = await db.execute(select(User))
    users = result.scalars().all()
    return users


@router.get("/{user_id}", response_model=UserResponse)
async def get_user_by_id(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_admin),
):
    """Get user by ID (Admin only)."""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_admin),
):
    """Update user details (Admin only)."""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    update_data = user_data.model_dump(exclude_unset=True)
    if "password" in update_data:
        update_data["hashed_password"] = get_password_hash(update_data.pop("password"))

    for key, value in update_data.items():
        setattr(user, key, value)

    await db.flush()
    await db.refresh(user)

    from app.controllers.log_controller import log_activity
    await log_activity(
        db=db,
        action="update_user",
        resource=f"/users/{user_id}",
        method="PUT",
        status_code=200,
        user_id=current_user.id,
        user_email=current_user.email,
    )

    return user


@router.delete("/{user_id}", response_model=MessageResponse)
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_admin),
):
    """Delete a user (Admin only)."""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user_id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot delete your own account")

    await db.delete(user)

    from app.controllers.log_controller import log_activity
    await log_activity(
        db=db,
        action="delete_user",
        resource=f"/users/{user_id}",
        method="DELETE",
        status_code=200,
        user_id=current_user.id,
        user_email=current_user.email,
    )

    return MessageResponse(message=f"User {user_id} deleted successfully")


@router.patch("/{user_id}/toggle-admin", response_model=UserResponse)
async def toggle_admin_status(
    user_id: int,
    toggle_data: UserToggleAdmin,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_admin),
):
    """Toggle admin status of a user (Admin only)."""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user_id == current_user.id and not toggle_data.is_admin:
        raise HTTPException(status_code=400, detail="Cannot remove your own admin privileges")

    user.is_admin = toggle_data.is_admin
    await db.flush()
    await db.refresh(user)

    from app.controllers.log_controller import log_activity
    await log_activity(
        db=db,
        action="toggle_admin",
        resource=f"/users/{user_id}/toggle-admin",
        method="PATCH",
        status_code=200,
        user_id=current_user.id,
        user_email=current_user.email,
    )

    return user