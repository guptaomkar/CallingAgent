# ============================================================
# AI Calling Agent — FastAPI Application Entry Point
# File: app/main.py
# ============================================================

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.database import init_db, close_db

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown events."""
    logger.info(f"🚀 Starting {settings.app_name} ({settings.app_env})")

    # Initialize database tables (dev mode)
    if not settings.is_production:
        await init_db()
        logger.info("✅ Database tables initialized")

    logger.info("✅ Application ready")
    yield

    # Shutdown
    logger.info("🛑 Shutting down...")
    await close_db()
    logger.info("✅ Database connections closed")


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    description=(
        "AI-Powered Autonomous Voice Calling Agent for Sales & Service Promotion. "
        "Manages campaigns, contacts, outbound calls, and generates structured reports."
    ),
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Health Check ---
@app.get("/health", tags=["Health"])
async def health_check():
    """Application health check endpoint."""
    return {
        "status": "healthy",
        "app": settings.app_name,
        "version": "1.0.0",
        "environment": settings.app_env,
    }


@app.get("/", tags=["Health"])
async def root():
    """Root endpoint — redirect to docs."""
    return {
        "message": f"Welcome to {settings.app_name}",
        "docs": "/docs",
        "health": "/health",
    }


# --- Include API routers ---
from app.api.campaigns import router as campaigns_router
from app.api.contacts import router as contacts_router
from app.api.calls import router as calls_router
from app.api.reports import router as reports_router
from app.api.webhooks import router as webhooks_router

app.include_router(campaigns_router, prefix="/api/v1")
app.include_router(contacts_router, prefix="/api/v1")
app.include_router(calls_router, prefix="/api/v1")
app.include_router(reports_router, prefix="/api/v1")
app.include_router(webhooks_router, prefix="/api/v1")
