"""Review session database model."""
from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer
from sqlalchemy.orm import relationship

from app.db import Base


class ReviewSession(Base):
    """Review session model."""

    __tablename__ = "review_sessions"

    id = Column(Integer, primary_key=True, index=True)
    deck_id = Column(Integer, ForeignKey("decks.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    started_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    finished_at = Column(DateTime, nullable=True)
    score = Column(Integer, nullable=True)

    deck = relationship("Deck", back_populates="review_sessions")
    user = relationship("User", back_populates="review_sessions")
    attempts = relationship(
        "ReviewAttempt", back_populates="session", cascade="all, delete-orphan"
    )
