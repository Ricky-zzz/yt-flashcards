"""Pydantic schemas for request/response validation."""
from pydantic import BaseModel, Field, model_validator
from typing import List, Optional, Dict, Any
from datetime import datetime


class GenerateRequest(BaseModel):
    """Request schema for /api/v1/generate endpoint."""
    youtube_url: Optional[str] = Field(default=None, description="YouTube URL")
    transcript_text: Optional[str] = Field(default=None, description="Pasted transcript text")
    num_pairs: int = Field(default=5, ge=1, le=50, description="Number of Q&A pairs per chunk")
    max_chunks: Optional[int] = Field(default=None, description="Max chunks to process (None = all)")

    @model_validator(mode="after")
    def check_input(self):
        if not self.youtube_url and not self.transcript_text:
            raise ValueError("Either youtube_url or transcript_text must be provided")
        return self

    class Config:
        json_schema_extra = {
            "example": {
                "youtube_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                "transcript_text": None,
                "num_pairs": 5,
                "max_chunks": 10
            }
        }


class FlashcardObject(BaseModel):
    """Individual flashcard object."""
    question: str
    answer: str
    chunk_index: int
    difficulty: Optional[str] = "medium"
    question_type: Optional[str] = "definition"
    topic: Optional[str] = "general"


class GenerateMetadata(BaseModel):
    """Metadata about generation process."""
    video_title: str
    total_cards: int
    processing_time: float
    chunks_processed: int
    classification_skipped: bool = False
    model_used: str = "gemini-1.5-flash-latest"


class GenerateResponseData(BaseModel):
    """Data payload for successful generate response."""
    flashcards: List[FlashcardObject]
    metadata: GenerateMetadata


class ErrorDetail(BaseModel):
    """Error detail object."""
    type: str
    details: Optional[str] = None


class GenerateResponse(BaseModel):
    """Standard response wrapper for /api/v1/generate."""
    success: bool
    data: Optional[GenerateResponseData] = None
    message: str
    error: Optional[ErrorDetail] = None

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "data": {
                    "flashcards": [
                        {
                            "question": "What is photosynthesis?",
                            "answer": "Process by which plants convert light energy into chemical energy.",
                            "chunk_index": 0,
                            "difficulty": "medium",
                            "question_type": "definition",
                            "topic": "biology"
                        }
                    ],
                    "metadata": {
                        "video_title": "Introduction to Photosynthesis",
                        "total_cards": 5,
                        "processing_time": 28.5,
                        "chunks_processed": 1,
                        "model_used": "gemini-1.5-flash-latest"
                    }
                },
                "message": "Flashcards generated successfully",
                "error": None
            }
        }


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    timestamp: datetime
