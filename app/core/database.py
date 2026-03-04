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
    from app.modules.properties.models import Property
    from app.modules.packages.models import Package
    from app.modules.payments.models import Payment
    from app.modules.favorites.models import Favorite
    from app.modules.view_history.models import ViewHistory
    from app.modules.appointments.models import Appointment
    from app.modules.leads.models import Lead
    from app.modules.chat.models import Conversation, Message
    from app.modules.reports.models import Report
    from app.modules.notifications.models import Notification

    await init_beanie(
        database=database,
        document_models=[
            User,
            Property,
            Package,
            Payment,
            Favorite,
            ViewHistory,
            Appointment,
            Lead,
            Conversation,
            Message,
            Report,
            Notification,
        ],
    )


async def close_db():
    """Close MongoDB connection."""
    global client
    if client:
        client.close()
