"""Deck and card schemas."""
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, HttpUrl


class APIError(BaseModel):
    """Standard API error payload."""
    type: str
    details: Optional[str] = None


class DeckCreate(BaseModel):
    """Create deck payload."""
    title: str = Field(..., min_length=1, max_length=255)
    user_id: int
    source_url: Optional[HttpUrl] = None


class DeckUpdate(BaseModel):
    """Update deck payload."""
    title: Optional[str] = Field(default=None, min_length=1, max_length=255)
    source_url: Optional[HttpUrl] = None


class DeckOut(BaseModel):
    """Deck response payload."""
    id: int
    user_id: int
    title: str
    source_url: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    card_count: Optional[int] = None


class CardCreate(BaseModel):
    """Create card payload."""
    front: str = Field(..., min_length=1)
    back: str = Field(..., min_length=1)
    difficulty: Optional[str] = None
    question_type: Optional[str] = None
    topic: Optional[str] = None


class CardUpdate(BaseModel):
    """Update card payload."""
    front: Optional[str] = Field(default=None, min_length=1)
    back: Optional[str] = Field(default=None, min_length=1)
    difficulty: Optional[str] = None
    question_type: Optional[str] = None
    topic: Optional[str] = None


class CardOut(BaseModel):
    """Card response payload."""
    id: int
    deck_id: int
    front: str
    back: str
    difficulty: Optional[str] = None
    question_type: Optional[str] = None
    topic: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class DeckResponse(BaseModel):
    """Standard response wrapper for deck endpoints."""
    success: bool
    data: Optional[DeckOut] = None
    message: str
    error: Optional[APIError] = None


class DeckListResponse(BaseModel):
    """List response for decks."""
    success: bool
    data: List[DeckOut]
    message: str
    error: Optional[APIError] = None


class CardResponse(BaseModel):
    """Standard response wrapper for card endpoints."""
    success: bool
    data: Optional[CardOut] = None
    message: str
    error: Optional[APIError] = None


class CardListResponse(BaseModel):
    """List response for cards."""
    success: bool
    data: List[CardOut]
    message: str
    error: Optional[APIError] = None
