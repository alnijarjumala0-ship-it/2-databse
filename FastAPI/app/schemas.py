"""Pydantic schemas for API request/response validation."""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


# ---------- Auth Schemas ----------
class UserRegister(BaseModel):
    email: str
    username: str
    password: str
    full_name: Optional[str] = None


class UserLogin(BaseModel):
    email: str
    password: str


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenRefresh(BaseModel):
    refresh_token: str


class ChangePassword(BaseModel):
    old_password: str
    new_password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class MessageResponse(BaseModel):
    message: str


# ---------- User Schemas ----------
class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    full_name: Optional[str] = None
    is_active: bool
    is_admin: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class UserUpdate(BaseModel):
    email: Optional[str] = None
    username: Optional[str] = None
    full_name: Optional[str] = None
    password: Optional[str] = None


class UserToggleAdmin(BaseModel):
    is_admin: bool


# ---------- Product Schemas ----------
class ProductResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    price: float
    stock: int
    category: Optional[str] = None
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class ProductCreate(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    stock: int = 0
    category: Optional[str] = None


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    stock: Optional[int] = None
    category: Optional[str] = None
    is_active: Optional[bool] = None


# ---------- Mongo Log Schemas ----------
class ActivityLogCreate(BaseModel):
    action: str
    resource: str
    method: str
    status_code: int
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    details: Optional[Dict[str, Any]] = None


class ActivityLogResponse(BaseModel):
    id: Optional[str] = None
    user_id: Optional[int] = None
    user_email: Optional[str] = None
    action: str
    resource: str
    method: str
    status_code: int
    ip_address: Optional[str] = None
    timestamp: datetime

    model_config = {"from_attributes": True, "populate_by_name": True}


class LogFilter(BaseModel):
    action: Optional[str] = None
    resource: Optional[str] = None
    user_id: Optional[int] = None
    limit: int = 100


class MongoSystemHealth(BaseModel):
    status: str
    database: str
    server_info: Dict[str, Any]
    collections: int
    document_count: int
    timestamp: datetime = Field(default_factory=datetime.utcnow)