"""FastAPI application entry point."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from fastapi.staticfiles import StaticFiles

from app.api import webhook, admin, callbacks
from app.db.database import engine, init_db
from app.config import settings
from app.utils.logger import app_logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    try:
        # Startup
        app_logger.info("Starting muuh Recruiting Chatbot...")
        app_logger.info(f"Environment: {settings.environment}")
        
        # Initialize database
        init_db()
        app_logger.info("Database initialized")
        
        yield
        
        # Shutdown
        app_logger.info("Shutting down muuh Recruiting Chatbot...")
    except Exception as e:
        app_logger.error(f"Startup/Shutdown Error: {e}")
        yield # Yield even if error to avoid total crash?


# Create FastAPI app
app = FastAPI(
    title="muuh Recruiting Chatbot",
    description="WhatsApp chatbot for automated recruiting and candidate screening",
    version="1.0.0",
    lifespan=lifespan
)

# Mount Static (CSS/JS)
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(webhook.router, tags=["webhook"])
app.include_router(admin.router, tags=["admin"])
app.include_router(callbacks.router, tags=["callbacks"])


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "muuh Recruiting Chatbot API",
        "version": "1.0.0",
        "status": "running",
        "environment": settings.environment,
        "dashboard_url": "/admin/dashboard"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "environment": settings.environment
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.environment == "development"
    )
