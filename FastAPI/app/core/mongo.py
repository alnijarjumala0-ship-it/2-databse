"""MongoDB connection setup using Motor."""
from motor.motor_asyncio import AsyncIOMotorClient

from app.core.settings import settings


class MongoDB:
    """MongoDB connection manager."""

    def __init__(self):
        self.client: AsyncIOMotorClient = None
        self.db = None

    def connect(self):
        """Connect to MongoDB."""
        self.client = AsyncIOMotorClient(
            settings.mongo_uri,
            serverSelectionTimeoutMS=5000,
            socketTimeoutMS=5000,
            connectTimeoutMS=5000,
        )
        self.db = self.client[settings.mongo_db]
        return self.db

    def close(self):
        """Close MongoDB connection."""
        if self.client:
            self.client.close()


mongodb = MongoDB()


async def get_mongo():
    """Dependency for getting MongoDB database."""
    if mongodb.db is None:
        mongodb.connect()
    return mongodb.db