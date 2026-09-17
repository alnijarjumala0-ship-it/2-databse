"""Pydantic models for MongoDB documents."""
from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class ActivityLog(BaseModel):
    """Activity log document for MongoDB."""

    id: Optional[str] = Field(None, alias="_id")
    user_id: Optional[int] = None
    user_email: Optional[str] = None
    action: str
    resource: str
    method: str
    status_code: int
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    details: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True


class MongoSystemHealth(BaseModel):
    """MongoDB system health status."""

    status: str
    database: str
    server_info: Dict[str, Any]
    collections: int
    document_count: int
    timestamp: datetime = Field(default_factory=datetime.utcnow)