"""Review schemas."""
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel

from app.schemas.deck import APIError


class ReviewSessionCreate(BaseModel):
    """Start review session payload."""
    deck_id: int
    user_id: int


class ReviewSessionOut(BaseModel):
    """Review session response payload."""
    id: int
    deck_id: int
    user_id: int
    started_at: datetime
    finished_at: Optional[datetime] = None
    score: Optional[int] = None


class ReviewAttemptCreate(BaseModel):
    """Submit review attempt payload."""
    session_id: int
    card_id: int
    user_answer: Optional[str] = None
    is_correct: bool


class ReviewAttemptOut(BaseModel):
    """Review attempt response payload."""
    id: int
    session_id: int
    card_id: int
    user_answer: Optional[str] = None
    is_correct: bool
    answered_at: datetime


class ReviewSessionResponse(BaseModel):
    """Standard response wrapper for review session endpoints."""
    success: bool
    data: Optional[ReviewSessionOut] = None
    message: str
    error: Optional[APIError] = None


class ReviewSessionListResponse(BaseModel):
    """List response for review sessions."""
    success: bool
    data: List[ReviewSessionOut]
    message: str
    error: Optional[APIError] = None


class ReviewAttemptResponse(BaseModel):
    """Standard response wrapper for review attempt endpoints."""
    success: bool
    data: Optional[ReviewAttemptOut] = None
    message: str
    error: Optional[APIError] = None


class ReviewAttemptListResponse(BaseModel):
    """List response for review attempts."""
    success: bool
    data: List[ReviewAttemptOut]
    message: str
    error: Optional[APIError] = None
