from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import init_db, close_db

# Import all routers
from app.modules.auth.router import router as auth_router
from app.modules.users.router import router as users_router
from app.modules.properties.router import router as properties_router
from app.modules.search.router import router as search_router
from app.modules.packages.router import router as packages_router
from app.modules.payments.router import router as payments_router
from app.modules.favorites.router import router as favorites_router
from app.modules.view_history.router import router as view_history_router
from app.modules.appointments.router import router as appointments_router
from app.modules.leads.router import router as leads_router
from app.modules.chat.router import router as chat_router
from app.modules.reports.router import router as reports_router
from app.modules.notifications.router import router as notifications_router


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

prefix = settings.API_V1_PREFIX

app.include_router(auth_router, prefix=prefix, tags=["Auth"])
app.include_router(users_router, prefix=prefix, tags=["Users"])
app.include_router(properties_router, prefix=prefix, tags=["Properties"])
app.include_router(search_router, prefix=prefix, tags=["Search"])
app.include_router(packages_router, prefix=prefix, tags=["Packages"])
app.include_router(payments_router, prefix=prefix, tags=["Payments"])
app.include_router(favorites_router, prefix=prefix, tags=["Favorites"])
app.include_router(view_history_router, prefix=prefix, tags=["View History"])
app.include_router(appointments_router, prefix=prefix, tags=["Appointments"])
app.include_router(leads_router, prefix=prefix, tags=["Leads"])
app.include_router(chat_router, prefix=prefix, tags=["Chat"])
app.include_router(reports_router, prefix=prefix, tags=["Reports"])
app.include_router(notifications_router, prefix=prefix, tags=["Notifications"])


# ──── Health Check ────


@app.get("/", tags=["Health"])
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": "1.0.0",
    }
