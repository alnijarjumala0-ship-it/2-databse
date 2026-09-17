# """Application settings loaded from environment variables."""
# from pydantic_settings import BaseSettings
# from pydantic import Field, field_validator
# from typing import Optional, Any


# class Settings(BaseSettings):
#     """Application configuration settings."""

#     # Database
#     postgres_user: str = "postgres"
#     postgres_password: str = "postgres"
#     postgres_db: str = "fastapi_db"
#     postgres_host: str = "db"
#     postgres_port: int = 5432
#     database_url: str = "postgresql+asyncpg://postgres:postgres@db:5432/fastapi_db"

#     # MongoDB
#     mongo_url: str = "mongodb://localhost:27017"
#     mongo_db: str = "fastapi_logs"

#     # Security
#     secret_key: str = "your-secret-key-change-in-production"
#     algorithm: str = "HS256"
#     access_token_expire_minutes: int = 30
#     refresh_token_expire_minutes: int = 10080

#     # App
#     app_name: str = "FastAPI MVC"
#     app_version: str = "1.0.0"
#     debug: bool = True
#     host: str = "0.0.0.0"
#     port: int = 8000

#     # Admin
#     admin_email: str = "admin@example.com"
#     admin_password: str = "admin123"
#     admin_secret_key: str = "super-secret-admin-key"

#     class Config:
#         env_file = ".env"
#         env_file_encoding = "utf-8"
#         case_sensitive = False

#     @field_validator("debug", mode="before")
#     @classmethod
#     def parse_debug(cls, v: Any) -> bool:
#         if isinstance(v, bool):
#             return v
#         if isinstance(v, str):
#             return v.lower() in ("true", "1", "yes", "on", "debug", "development")
#         return bool(v)


# settings = Settings()

"""Application settings loaded from environment variables."""
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator
from typing import Any


class Settings(BaseSettings):
    """Application configuration settings."""

    # Database
    postgres_user: str = "postgres"
    postgres_password: str = "postgres"
    postgres_db: str = "fastapi_db"
    postgres_host: str = "db"
    postgres_port: int = 5432
    postgres_uri: str = "postgresql://postgres:postgres@localhost:5432/fastapi_db"
    database_url: str = "postgresql+asyncpg://postgres:postgres@db:5432/fastapi_db"

    # MongoDB
    mongo_uri: str = "mongodb://localhost:27017"
    mongo_db: str = "fastapi_logs"

    # Security
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_minutes: int = 10080

    # App
    app_name: str = "FastAPI MVC"
    app_version: str = "1.0.0"
    debug: bool = True
    host: str = "0.0.0.0"
    port: int = 8000

    # Admin
    admin_email: str = "admin@example.com"
    admin_password: str = "admin123"
    admin_secret_key: str = "super-secret-admin-key"

    # Settings configuration
    model_config = SettingsConfigDict(
        env_file=str(Path(__file__).resolve().parent.parent.parent / ".env"),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @field_validator("debug", mode="before")
    @classmethod
    def parse_debug(cls, v: Any) -> bool:
        if isinstance(v, bool):
            return v
        if isinstance(v, str):
            return v.lower() in ("true", "1", "yes", "on", "debug", "development")
        return bool(v)


settings = Settings()