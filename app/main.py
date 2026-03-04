from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import init_db, close_db
from app.modules.users.router import router as users_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: startup and shutdown events."""
    # Startup - Initialize MongoDB connection
    print(f"🚀 {settings.APP_NAME} is starting up...")
    await init_db()
    print("📦 MongoDB connected & Beanie initialized")
    yield
    # Shutdown - Close MongoDB connection
    await close_db()
    print(f"👋 {settings.APP_NAME} is shutting down...")


app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    description="Backend API for RentUp rental platform",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# ──── Middleware ────

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ──── Routers ────

app.include_router(
    users_router,
    prefix=settings.API_V1_PREFIX,
    tags=["Users"],
)


# ──── Health Check ────


@app.get("/", tags=["Health"])
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": "1.0.0",
    }
