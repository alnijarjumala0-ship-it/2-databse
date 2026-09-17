"""Mongo Log/Analytics Controller - Activity logging and system health."""
import asyncio
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import Optional, List

from app.core.database import get_db
from app.core.mongo import get_mongo
from app.core.settings import settings
from app.models.pydantic_models import ActivityLog, MongoSystemHealth
from app.schemas import (
    ActivityLogCreate,
    ActivityLogResponse,
    LogFilter,
    MessageResponse,
)
from app.core.dependencies import get_current_admin


router = APIRouter(prefix="/logs", tags=["Mongo Logs"])


async def log_activity(
    db: AsyncSession,
    action: str,
    resource: str,
    method: str,
    status_code: int,
    user_id: Optional[int] = None,
    user_email: Optional[str] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
    details: Optional[dict] = None,
):
    """Log an activity to MongoDB (non-blocking, fails fast)."""
    try:
        mongo_db = await get_mongo()
        log_doc = ActivityLog(
            user_id=user_id,
            user_email=user_email,
            action=action,
            resource=resource,
            method=method,
            status_code=status_code,
            ip_address=ip_address,
            user_agent=user_agent,
            details=details,
        )
        await asyncio.wait_for(
            mongo_db.activity_logs.insert_one(log_doc.model_dump(by_alias=True)),
            timeout=3.0,
        )
    except asyncio.TimeoutError:
        pass
    except Exception as e:
        print(f"Failed to log activity: {e}")


@router.post("/create", response_model=ActivityLogResponse, status_code=status.HTTP_201_CREATED)
async def create_log(
    log_data: ActivityLogCreate,
    mongo_db: AsyncIOMotorDatabase = Depends(get_mongo),
    current_user=Depends(get_current_admin),
):
    """Create a new activity log (Admin only)."""
    log_doc = ActivityLog(
        user_id=current_user.id,
        user_email=current_user.email,
        action=log_data.action,
        resource=log_data.resource,
        method=log_data.method,
        status_code=log_data.status_code,
        ip_address=log_data.ip_address,
        user_agent=log_data.user_agent,
        details=log_data.details,
    )
    result = await mongo_db.activity_logs.insert_one(log_doc.model_dump(by_alias=True))
    log_doc.id = str(result.inserted_id)
    return log_doc


@router.get("/view", response_model=List[ActivityLogResponse])
async def view_logs(
    action: Optional[str] = Query(None),
    resource: Optional[str] = Query(None),
    user_id: Optional[int] = Query(None),
    limit: int = Query(100, le=500),
    mongo_db: AsyncIOMotorDatabase = Depends(get_mongo),
    current_user=Depends(get_current_admin),
):
    """View activity logs with optional filtering (Admin only)."""
    query = {}
    if action:
        query["action"] = action
    if resource:
        query["resource"] = resource
    if user_id:
        query["user_id"] = user_id

    cursor = mongo_db.activity_logs.find(query).sort("timestamp", -1).limit(limit)
    logs = []
    async for doc in cursor:
        doc["id"] = str(doc.pop("_id"))
        logs.append(ActivityLogResponse(**doc))
    return logs


@router.get("/filter/user/{user_id}", response_model=List[ActivityLogResponse])
async def filter_logs_by_user(
    user_id: int,
    limit: int = Query(100, le=500),
    mongo_db: AsyncIOMotorDatabase = Depends(get_mongo),
    current_user=Depends(get_current_admin),
):
    """Filter logs by user ID (Admin only)."""
    cursor = mongo_db.activity_logs.find({"user_id": user_id}).sort("timestamp", -1).limit(limit)
    logs = []
    async for doc in cursor:
        doc["id"] = str(doc.pop("_id"))
        logs.append(ActivityLogResponse(**doc))
    return logs


@router.get("/health", response_model=MongoSystemHealth)
async def mongo_health_check(
    mongo_db: AsyncIOMotorDatabase = Depends(get_mongo),
    current_user=Depends(get_current_admin),
):
    """Check MongoDB system health (Admin only)."""
    try:
        server_info = await mongo_db.client.server_info()
        collections = await mongo_db.list_collection_names()
        doc_count = await mongo_db.activity_logs.count_documents({})

        return MongoSystemHealth(
            status="healthy",
            database=settings.mongo_db,
            server_info=server_info,
            collections=len(collections),
            document_count=doc_count,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"MongoDB health check failed: {str(e)}",
        )


@router.delete("/clear-old", response_model=MessageResponse)
async def clear_old_logs(
    days: int = Query(90, ge=1, le=365),
    mongo_db: AsyncIOMotorDatabase = Depends(get_mongo),
    current_user=Depends(get_current_admin),
):
    """Clear activity logs older than specified days (Admin only)."""
    from datetime import datetime, timezone
    cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
    result = await mongo_db.activity_logs.delete_many(
        {"timestamp": {"$lt": cutoff_date}}
    )
    return MessageResponse(message=f"Cleared {result.deleted_count} old logs")