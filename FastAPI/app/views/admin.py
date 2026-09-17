"""Admin Dashboard UI setup using SQLAdmin with secure login."""
from fastapi import FastAPI
from sqladmin import Admin, ModelView
from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request
from sqlalchemy import select

from app.core.database import engine, async_session_factory
from app.core.settings import settings
from app.core.security import verify_password
from app.models.sqlalchemy_models import User, Product


class AdminAuthBackend(AuthenticationBackend):
    """Authentication backend validating admins against the User table."""

    def __init__(self, secret_key: str):
        super().__init__(secret_key)

    async def login(self, request: Request):
        form = await request.form()
        username = form.get("username")
        password = form.get("password")

        from sqlalchemy.ext.asyncio import AsyncSession

        try:
            async with async_session_factory() as db:
                result = await db.execute(
                    select(User).where(
                        ((User.email == username) | (User.username == username))
                        & User.is_admin.is_(True)
                        & User.is_active.is_(True)
                    )
                )
                user = result.scalar_one_or_none()
                if user and verify_password(password, user.hashed_password):
                    request.session["token"] = f"admin:{user.id}"
                    return True
        except Exception:
            pass

        return False

    async def logout(self, request: Request):
        request.session.clear()
        return True

    async def authenticate(self, request: Request):
        token = request.session.get("token")
        if not token:
            return False
        return True


class UserAdminView(ModelView, model=User):
    """Admin view for User model."""

    list_display = ["id", "email", "username", "full_name", "is_active", "is_admin"]
    list_search = ["email", "username", "full_name"]
    page_size = 50
    page_size_options = [10, 25, 50, 100]


class ProductAdminView(ModelView, model=Product):
    """Admin view for Product model."""

    list_display = ["id", "name", "price", "stock", "category", "is_active"]
    list_search = ["name", "category"]
    page_size = 50
    page_size_options = [10, 25, 50, 100]


def setup_admin(app: FastAPI):
    """Set up SQLAdmin for the FastAPI application."""
    auth_backend = AdminAuthBackend(secret_key=settings.admin_secret_key)
    admin = Admin(
        app,
        engine,
        authentication_backend=auth_backend,
        base_url="/admin",
        title="FastAPI Admin Dashboard",
    )

    admin.add_view(UserAdminView)
    admin.add_view(ProductAdminView)

    return admin