"""Auth Controller - Registration, Login, Token Refresh, Logout, Profile."""
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Request

from app.core.database import get_db
from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    verify_token,
)
from app.models.sqlalchemy_models import User
from app.schemas import (
    UserRegister,
    UserLogin,
    Token,
    TokenRefresh,
    TokenResponse,
    MessageResponse,
    UserResponse,
    UserUpdate,
    ChangePassword,
)
from app.core.dependencies import get_current_user, get_current_admin


router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserRegister, db=Depends(get_db)):
    """Register a new user and return tokens."""
    from sqlalchemy import select
    existing_user = await db.execute(select(User).where(User.email == user_data.email))
    if existing_user.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already registered")

    existing_username = await db.execute(select(User).where(User.username == user_data.username))
    if existing_username.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Username already taken")

    new_user = User(
        email=user_data.email,
        username=user_data.username,
        hashed_password=get_password_hash(user_data.password),
        full_name=user_data.full_name,
        is_active=True,
        is_admin=False,
    )
    db.add(new_user)
    await db.flush()
    await db.refresh(new_user)

    access_token = create_access_token({"sub": str(new_user.id), "email": new_user.email})
    refresh_token = create_refresh_token({"sub": str(new_user.id), "email": new_user.email})

    return Token(access_token=access_token, refresh_token=refresh_token, token_type="bearer")


@router.post("/register-admin", response_model=Token, status_code=status.HTTP_201_CREATED)
async def register_admin(user_data: UserRegister, db=Depends(get_db)):
    """Register a new admin user and return tokens."""
    from sqlalchemy import select
    existing_user = await db.execute(select(User).where(User.email == user_data.email))
    if existing_user.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already registered")

    existing_username = await db.execute(select(User).where(User.username == user_data.username))
    if existing_username.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Username already taken")

    new_user = User(
        email=user_data.email,
        username=user_data.username,
        hashed_password=get_password_hash(user_data.password),
        full_name=user_data.full_name,
        is_active=True,
        is_admin=True,
    )
    db.add(new_user)
    await db.flush()
    await db.refresh(new_user)

    access_token = create_access_token({"sub": str(new_user.id), "email": new_user.email})
    refresh_token = create_refresh_token({"sub": str(new_user.id), "email": new_user.email})

    from app.controllers.log_controller import log_activity
    await log_activity(
        db=db,
        action="register_admin",
        resource="/auth/register-admin",
        method="POST",
        status_code=201,
        user_id=new_user.id,
        user_email=new_user.email,
    )

    return Token(access_token=access_token, refresh_token=refresh_token, token_type="bearer")


@router.post("/login", response_model=Token)
async def login(user_data: UserLogin, request: Request, db=Depends(get_db)):
    """Authenticate user and return tokens."""
    from sqlalchemy import select
    result = await db.execute(select(User).where(User.email == user_data.email))
    user = result.scalar_one_or_none()

    if not user or not verify_password(user_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account is disabled")

    access_token = create_access_token({"sub": str(user.id), "email": user.email})
    refresh_token = create_refresh_token({"sub": str(user.id), "email": user.email})

    from app.controllers.log_controller import log_activity
    await log_activity(
        db=db,
        action="login",
        resource="/auth/login",
        method="POST",
        status_code=200,
        user_id=user.id,
        user_email=user.email,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )

    return Token(access_token=access_token, refresh_token=refresh_token, token_type="bearer")


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(token_data: TokenRefresh):
    """Refresh access token using a valid refresh token."""
    payload = verify_token(token_data.refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")

    new_access_token = create_access_token({"sub": payload["sub"], "email": payload["email"]})
    return TokenResponse(access_token=new_access_token)


@router.post("/logout", response_model=MessageResponse)
async def logout(current_user: User = Depends(get_current_user)):
    """Logout user (client should discard tokens)."""
    return MessageResponse(message="Logged out successfully")


@router.get("/profile", response_model=UserResponse)
async def get_profile(current_user: User = Depends(get_current_user)):
    """Get current user profile."""
    return current_user


@router.get("/verify", response_model=UserResponse)
async def verify_token_endpoint(current_user: User = Depends(get_current_user)):
    """Verify that the current token is valid and return user info."""
    return current_user


@router.post("/change-password", response_model=MessageResponse)
async def change_password(
    password_data: ChangePassword,
    current_user: User = Depends(get_current_user),
    db=Depends(get_db),
):
    """Change the current user's password."""
    from sqlalchemy import select

    if not verify_password(password_data.old_password, current_user.hashed_password):
        raise HTTPException(status_code=401, detail="Old password is incorrect")

    current_user.hashed_password = get_password_hash(password_data.new_password)
    await db.flush()
    await db.refresh(current_user)

    return MessageResponse(message="Password changed successfully")