"""FastAPI application entry point."""
import logging
from datetime import datetime
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Load environment variables from .env
env_path = Path(__file__).parent / ".env"
load_dotenv(env_path)

from app.routes import generate_router
from app.schemas import HealthResponse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="YouTube Flashcard Generator API",
    description="Generate flashcards from YouTube video transcripts",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Add CORS middleware (allow all origins for now, restrict in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(generate_router)


@app.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Health check endpoint."""
    logger.info("Health check called")
    return HealthResponse(
        status="ok",
        timestamp=datetime.now()
    )


@app.get("/", tags=["root"])
async def root():
    """Root endpoint with API info."""
    return {
        "message": "YouTube Flashcard Generator API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
"""
FastAPI application initialization and configuration.
Main entry point for the flashcard generator API.
"""
import logging
from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Load environment variables from .env file
load_dotenv(Path(__file__).parent / '.env')

from app.routes import router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="YouTube Flashcard Generator API",
    description="Generate flashcards from YouTube videos using AI and zero-shot classification",
    version="1.0.0",
)

# Add CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update to specific domains in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(router)


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "service": "YouTube Flashcard Generator",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc",
        "health": "/api/v1/health"
    }


@app.on_event("startup")
async def startup_event():
    """Called when API starts up."""
    logger.info("Starting YouTube Flashcard Generator API...")


@app.on_event("shutdown")
async def shutdown_event():
    """Called when API shuts down."""
    logger.info("Shutting down YouTube Flashcard Generator API...")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
