"""
Connexion MongoDB via Motor (driver async).
"""

from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings

_client: AsyncIOMotorClient | None = None


def get_client() -> AsyncIOMotorClient:
    global _client
    if _client is None:
        _client = AsyncIOMotorClient(settings.MONGODB_URL)
    return _client


def get_db():
    return get_client()[settings.MONGODB_DB]


async def close_connection():
    global _client
    if _client:
        _client.close()
        _client = None
