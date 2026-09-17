# """Main FastAPI application entry point."""
# import sys
# from pathlib import Path

# sys.path.insert(0, str(Path(__file__).resolve().parent))

# from fastapi import FastAPI
# from fastapi.middleware.cors import CORSMiddleware
# from fastapi.staticfiles import StaticFiles

# from app.core.settings import settings
# from app.core.database import init_db
# from app.core.mongo import mongodb
# from app.controllers.auth_controller import router as auth_router
# from app.controllers.user_controller import router as user_router
# from app.controllers.product_controller import router as product_router
# from app.controllers.log_controller import router as log_router
# from app.views.admin import setup_admin
# from app.views.ui import router as ui_router


# app = FastAPI(
#     title=settings.app_name,
#     version=settings.app_version,
#     debug=settings.debug,
# )

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# static_dir = Path(__file__).parent / "app" / "static"
# static_dir.mkdir(exist_ok=True)
# app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# app.include_router(auth_router)
# app.include_router(user_router)
# app.include_router(product_router)
# app.include_router(log_router)
# app.include_router(ui_router)
# setup_admin(app)


# @app.on_event("startup")
# async def on_startup():
#     try:
#         await init_db()
#     except Exception as exc:
#         print(f"[startup] PostgreSQL init skipped: {exc}")
#     try:
#         mongodb.connect()
#     except Exception as exc:
#         print(f"[startup] MongoDB connect skipped: {exc}")


# @app.on_event("shutdown")
# async def on_shutdown():
#     mongodb.close()


# @app.get("/health")
# async def health_check():
#     return {"status": "healthy", "version": settings.app_version}


# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run("main:app", host=settings.host, port=settings.port, reload=settings.debug)

"""Main FastAPI application entry point."""
import sys
from pathlib import Path
from contextlib import asynccontextmanager

sys.path.insert(0, str(Path(__file__).resolve().parent))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from sqlalchemy import text

# Import engine directly instead of AsyncSessionLocal
from app.core.settings import settings
from app.core.database import init_db, engine, async_session_factory
from app.core.security import get_password_hash, verify_password
from app.core.mongo import mongodb
from app.models.sqlalchemy_models import User
from app.controllers.auth_controller import router as auth_router
from app.controllers.user_controller import router as user_router
from app.controllers.product_controller import router as product_router
from app.controllers.log_controller import router as log_router
from app.views.admin import setup_admin
from app.views.ui import router as ui_router


# ==========================================
# 1. Lifespan Manager (Startup/Shutdown)
# ==========================================
@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- Startup Logic ---
    try:
        await init_db()
        from sqlalchemy import select, or_
        from sqlalchemy.exc import IntegrityError

        async with async_session_factory() as db:
            result = await db.execute(
                select(User).where(
                    or_(User.username == "admin", User.email == settings.admin_email)
                )
            )
            existing = result.scalars().unique().all()

            if existing:
                admin_user = existing[0]
                admin_user.is_admin = True
                admin_user.is_active = True
                if admin_user.email != settings.admin_email:
                    admin_user.email = settings.admin_email
                if not verify_password(settings.admin_password, admin_user.hashed_password):
                    admin_user.hashed_password = get_password_hash(settings.admin_password)
                await db.commit()
                print(f"[startup] Admin user ensured: {settings.admin_email}")
                if len(existing) > 1:
                    for extra in existing[1:]:
                        extra.is_admin = True
                        extra.is_active = True
                        if not verify_password(settings.admin_password, extra.hashed_password):
                            extra.hashed_password = get_password_hash(settings.admin_password)
                    await db.commit()
            else:
                admin_user = User(
                    email=settings.admin_email,
                    username="admin",
                    hashed_password=get_password_hash(settings.admin_password),
                    full_name="Administrator",
                    is_active=True,
                    is_admin=True,
                )
                db.add(admin_user)
                try:
                    await db.commit()
                    print(f"[startup] Default admin user created: {settings.admin_email}")
                except IntegrityError:
                    await db.rollback()
                    print(f"[startup] Admin user already exists (race condition), skipping creation")
    except Exception as exc:
        print(f"[startup] PostgreSQL init or admin setup skipped: {exc}")
        
    try:
        mongodb.connect()
    except Exception as exc:
        print(f"[startup] MongoDB connect skipped: {exc}")

    yield

    # --- Shutdown Logic ---
    mongodb.close()


# ==========================================
# 2. App Initialization
# ==========================================
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    debug=settings.debug,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    SessionMiddleware,
    secret_key=settings.admin_secret_key,
)

# ==========================================
# 3. Static Files & Routing
# ==========================================
static_dir = Path(__file__).parent / "app" / "static"
static_dir.mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

app.include_router(auth_router)
app.include_router(user_router)
app.include_router(product_router)
app.include_router(log_router)
app.include_router(ui_router)
setup_admin(app)


# ==========================================
# 4. Endpoints
# ==========================================
@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": settings.app_version}


@app.get("/db-check")
async def check_databases():
    status = {"postgres": "disconnected", "mongodb": "disconnected"}
    
    # Test PostgreSQL via engine connection
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
            status["postgres"] = "connected"
    except Exception as e:
        status["postgres"] = f"error: {str(e)}"

    # Test MongoDB
    try:
        await mongodb.client.admin.command('ping')
        status["mongodb"] = "connected"
    except Exception as e:
        status["mongodb"] = f"error: {str(e)}"

    return status


# ==========================================
# 5. Application Execution
# ==========================================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host=settings.host, port=settings.port, reload=settings.debug)