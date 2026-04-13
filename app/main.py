"""FastAPI application entry point."""
import logging
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes import auth_router, generate_router
from app.schemas import HealthResponse

# Load environment variables from .env
env_path = Path(__file__).resolve().parents[1] / ".env"
load_dotenv(env_path)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="YouTube Flashcard Generator API",
    description="Generate flashcards from YouTube video transcripts",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(generate_router)
app.include_router(auth_router)


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
