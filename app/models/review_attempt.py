"""Review attempt database model."""
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, Text
from sqlalchemy.orm import relationship

from app.db import Base


class ReviewAttempt(Base):
    """Review attempt model."""

    __tablename__ = "review_attempts"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(
        Integer, ForeignKey("review_sessions.id"), nullable=False, index=True
    )
    card_id = Column(Integer, ForeignKey("cards.id"), nullable=False, index=True)
    user_answer = Column(Text, nullable=True)
    is_correct = Column(Boolean, nullable=False, default=False)
    answered_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    session = relationship("ReviewSession", back_populates="attempts")
    card = relationship("Card", back_populates="review_attempts")
