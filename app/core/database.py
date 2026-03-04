from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie

from app.core.config import settings

# MongoDB client instance
client: AsyncIOMotorClient = None


async def init_db():
    """Initialize MongoDB connection and Beanie ODM."""
    global client

    client = AsyncIOMotorClient(
        settings.MONGODB_URL,
        serverSelectionTimeoutMS=5000,
    )

    # Verify connection
    try:
        await client.admin.command("ping")
        print("✅ MongoDB connection successful")
    except Exception as e:
        print(f"⚠️  MongoDB connection failed: {e}")
        raise

    database = client[settings.MONGODB_DB_NAME]

    # Import all document models for Beanie initialization
    from app.modules.users.models import User

    await init_beanie(
        database=database,
        document_models=[
            User,
            # Add new document models here
        ],
    )


async def close_db():
    """Close MongoDB connection."""
    global client
    if client:
        client.close()
