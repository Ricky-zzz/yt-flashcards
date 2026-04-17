"""Card database model."""
from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.db import Base


class Card(Base):
    """Card model."""

    __tablename__ = "cards"

    id = Column(Integer, primary_key=True, index=True)
    deck_id = Column(Integer, ForeignKey("decks.id"), nullable=False, index=True)
    front = Column(Text, nullable=False)
    back = Column(Text, nullable=False)
    difficulty = Column(String(50), nullable=True)
    question_type = Column(String(50), nullable=True)
    topic = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, nullable=False, onupdate=datetime.utcnow
    )

    deck = relationship("Deck", back_populates="cards")
    review_attempts = relationship(
        "ReviewAttempt", back_populates="card", cascade="all, delete-orphan"
    )
