"""Review session endpoints."""
import logging
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.review_session import ReviewSession
from app.models.review_attempt import ReviewAttempt
from app.models.deck import Deck
from app.schemas.review import (
    ReviewSessionCreate,
    ReviewSessionOut,
    ReviewAttemptCreate,
    ReviewAttemptOut,
    ReviewSessionResponse,
    ReviewSessionListResponse,
    ReviewAttemptResponse,
    ReviewAttemptListResponse,
)
from app.schemas.deck import APIError

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1", tags=["reviews"])


@router.post("/reviews/sessions", response_model=ReviewSessionResponse)
def start_review_session(
    request: ReviewSessionCreate,
    db: Session = Depends(get_db),
) -> ReviewSessionResponse:
    """Start a review session for a deck."""
    deck = db.query(Deck).filter(Deck.id == request.deck_id).first()
    if not deck:
        return ReviewSessionResponse(
            success=False,
            data=None,
            message="Deck not found",
            error=APIError(type="DeckNotFound", details="Deck does not exist"),
        )

    session = ReviewSession(deck_id=request.deck_id, user_id=request.user_id)
    db.add(session)
    db.commit()
    db.refresh(session)

    return ReviewSessionResponse(
        success=True,
        data=_session_out(session),
        message="Review session started",
        error=None,
    )


@router.get("/reviews/sessions", response_model=ReviewSessionListResponse)
def list_review_sessions(
    user_id: Optional[int] = None,
    deck_id: Optional[int] = None,
    db: Session = Depends(get_db),
) -> ReviewSessionListResponse:
    """List review sessions, optionally filtered by user and deck."""
    query = db.query(ReviewSession)
    if user_id is not None:
        query = query.filter(ReviewSession.user_id == user_id)
    if deck_id is not None:
        query = query.filter(ReviewSession.deck_id == deck_id)

    sessions = query.order_by(ReviewSession.started_at.desc()).all()
    data = [_session_out(session) for session in sessions]

    return ReviewSessionListResponse(
        success=True,
        data=data,
        message="Review sessions loaded",
        error=None,
    )


@router.post("/reviews/sessions/{session_id}/finish", response_model=ReviewSessionResponse)
def finish_review_session(
    session_id: int,
    score: int,
    db: Session = Depends(get_db),
) -> ReviewSessionResponse:
    """Finish a review session and store the score."""
    session = db.query(ReviewSession).filter(ReviewSession.id == session_id).first()
    if not session:
        return ReviewSessionResponse(
            success=False,
            data=None,
            message="Review session not found",
            error=APIError(type="ReviewSessionNotFound", details="Session does not exist"),
        )

    session.score = score
    session.finished_at = datetime.utcnow()
    db.commit()
    db.refresh(session)

    return ReviewSessionResponse(
        success=True,
        data=_session_out(session),
        message="Review session finished",
        error=None,
    )


@router.post("/reviews/attempts", response_model=ReviewAttemptResponse)
def submit_attempt(
    request: ReviewAttemptCreate,
    db: Session = Depends(get_db),
) -> ReviewAttemptResponse:
    """Record a review attempt for a card."""
    attempt = ReviewAttempt(
        session_id=request.session_id,
        card_id=request.card_id,
        user_answer=request.user_answer,
        is_correct=request.is_correct,
    )
    db.add(attempt)
    db.commit()
    db.refresh(attempt)

    return ReviewAttemptResponse(
        success=True,
        data=_attempt_out(attempt),
        message="Attempt recorded",
        error=None,
    )


@router.get("/reviews/sessions/{session_id}/attempts", response_model=ReviewAttemptListResponse)
def list_attempts(
    session_id: int,
    db: Session = Depends(get_db),
) -> ReviewAttemptListResponse:
    """List attempts for a review session."""
    attempts = (
        db.query(ReviewAttempt)
        .filter(ReviewAttempt.session_id == session_id)
        .order_by(ReviewAttempt.answered_at.asc())
        .all()
    )
    data = [_attempt_out(attempt) for attempt in attempts]

    return ReviewAttemptListResponse(
        success=True,
        data=data,
        message="Attempts loaded",
        error=None,
    )


def _session_out(session: ReviewSession) -> ReviewSessionOut:
    return ReviewSessionOut(
        id=session.id,
        deck_id=session.deck_id,
        user_id=session.user_id,
        started_at=session.started_at,
        finished_at=session.finished_at,
        score=session.score,
    )


def _attempt_out(attempt: ReviewAttempt) -> ReviewAttemptOut:
    return ReviewAttemptOut(
        id=attempt.id,
        session_id=attempt.session_id,
        card_id=attempt.card_id,
        user_answer=attempt.user_answer,
        is_correct=attempt.is_correct,
        answered_at=attempt.answered_at,
    )
