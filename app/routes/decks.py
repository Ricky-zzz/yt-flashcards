"""Deck and card endpoints."""
import logging
from typing import List, Optional

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.deck import Deck
from app.models.card import Card
from app.schemas.deck import (
    APIError,
    DeckCreate,
    DeckUpdate,
    DeckOut,
    DeckResponse,
    DeckListResponse,
    CardCreate,
    CardUpdate,
    CardOut,
    CardResponse,
    CardListResponse,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1", tags=["decks"])


@router.post("/decks", response_model=DeckResponse)
def create_deck(request: DeckCreate, db: Session = Depends(get_db)) -> DeckResponse:
    """Create a new deck."""
    deck = Deck(
        user_id=request.user_id,
        title=request.title,
        source_url=str(request.source_url) if request.source_url else None,
    )
    db.add(deck)
    db.commit()
    db.refresh(deck)

    logger.info("Created deck %s for user %s", deck.id, deck.user_id)

    return DeckResponse(
        success=True,
        data=_deck_out(deck),
        message="Deck created",
        error=None,
    )


@router.get("/decks", response_model=DeckListResponse)
def list_decks(user_id: Optional[int] = None, db: Session = Depends(get_db)) -> DeckListResponse:
    """List decks, optionally filtered by user."""
    query = db.query(Deck)
    if user_id is not None:
        query = query.filter(Deck.user_id == user_id)

    decks = query.order_by(Deck.created_at.desc()).all()
    data = [_deck_out(deck, include_count=True) for deck in decks]

    return DeckListResponse(
        success=True,
        data=data,
        message="Decks loaded",
        error=None,
    )


@router.get("/decks/{deck_id}", response_model=DeckResponse)
def get_deck(deck_id: int, db: Session = Depends(get_db)) -> DeckResponse:
    """Get a single deck."""
    deck = db.query(Deck).filter(Deck.id == deck_id).first()
    if not deck:
        return DeckResponse(
            success=False,
            data=None,
            message="Deck not found",
            error=APIError(type="DeckNotFound", details="Deck does not exist"),
        )

    return DeckResponse(
        success=True,
        data=_deck_out(deck, include_count=True),
        message="Deck loaded",
        error=None,
    )


@router.put("/decks/{deck_id}", response_model=DeckResponse)
def update_deck(deck_id: int, request: DeckUpdate, db: Session = Depends(get_db)) -> DeckResponse:
    """Update a deck."""
    deck = db.query(Deck).filter(Deck.id == deck_id).first()
    if not deck:
        return DeckResponse(
            success=False,
            data=None,
            message="Deck not found",
            error=APIError(type="DeckNotFound", details="Deck does not exist"),
        )

    if request.title is not None:
        deck.title = request.title
    if request.source_url is not None:
        deck.source_url = str(request.source_url)

    db.commit()
    db.refresh(deck)

    return DeckResponse(
        success=True,
        data=_deck_out(deck, include_count=True),
        message="Deck updated",
        error=None,
    )


@router.delete("/decks/{deck_id}", response_model=DeckResponse)
def delete_deck(deck_id: int, db: Session = Depends(get_db)) -> DeckResponse:
    """Delete a deck and its cards."""
    deck = db.query(Deck).filter(Deck.id == deck_id).first()
    if not deck:
        return DeckResponse(
            success=False,
            data=None,
            message="Deck not found",
            error=APIError(type="DeckNotFound", details="Deck does not exist"),
        )

    db.delete(deck)
    db.commit()

    return DeckResponse(
        success=True,
        data=None,
        message="Deck deleted",
        error=None,
    )


@router.get("/decks/{deck_id}/cards", response_model=CardListResponse)
def list_cards(deck_id: int, db: Session = Depends(get_db)) -> CardListResponse:
    """List cards for a deck."""
    cards = (
        db.query(Card)
        .filter(Card.deck_id == deck_id)
        .order_by(Card.created_at.asc())
        .all()
    )
    data = [_card_out(card) for card in cards]

    return CardListResponse(
        success=True,
        data=data,
        message="Cards loaded",
        error=None,
    )


@router.post("/decks/{deck_id}/cards", response_model=CardResponse)
def create_card(deck_id: int, request: CardCreate, db: Session = Depends(get_db)) -> CardResponse:
    """Create a card in a deck."""
    deck = db.query(Deck).filter(Deck.id == deck_id).first()
    if not deck:
        return CardResponse(
            success=False,
            data=None,
            message="Deck not found",
            error=APIError(type="DeckNotFound", details="Deck does not exist"),
        )

    card = Card(
        deck_id=deck_id,
        front=request.front,
        back=request.back,
        difficulty=request.difficulty,
        question_type=request.question_type,
        topic=request.topic,
    )
    db.add(card)
    db.commit()
    db.refresh(card)

    return CardResponse(
        success=True,
        data=_card_out(card),
        message="Card created",
        error=None,
    )


@router.put("/cards/{card_id}", response_model=CardResponse)
def update_card(card_id: int, request: CardUpdate, db: Session = Depends(get_db)) -> CardResponse:
    """Update a card."""
    card = db.query(Card).filter(Card.id == card_id).first()
    if not card:
        return CardResponse(
            success=False,
            data=None,
            message="Card not found",
            error=APIError(type="CardNotFound", details="Card does not exist"),
        )

    if request.front is not None:
        card.front = request.front
    if request.back is not None:
        card.back = request.back
    if request.difficulty is not None:
        card.difficulty = request.difficulty
    if request.question_type is not None:
        card.question_type = request.question_type
    if request.topic is not None:
        card.topic = request.topic

    db.commit()
    db.refresh(card)

    return CardResponse(
        success=True,
        data=_card_out(card),
        message="Card updated",
        error=None,
    )


@router.delete("/cards/{card_id}", response_model=CardResponse)
def delete_card(card_id: int, db: Session = Depends(get_db)) -> CardResponse:
    """Delete a card."""
    card = db.query(Card).filter(Card.id == card_id).first()
    if not card:
        return CardResponse(
            success=False,
            data=None,
            message="Card not found",
            error=APIError(type="CardNotFound", details="Card does not exist"),
        )

    db.delete(card)
    db.commit()

    return CardResponse(
        success=True,
        data=None,
        message="Card deleted",
        error=None,
    )


def _deck_out(deck: Deck, include_count: bool = False) -> DeckOut:
    card_count = len(deck.cards) if include_count else None
    return DeckOut(
        id=deck.id,
        user_id=deck.user_id,
        title=deck.title,
        source_url=deck.source_url,
        created_at=deck.created_at,
        updated_at=deck.updated_at,
        card_count=card_count,
    )


def _card_out(card: Card) -> CardOut:
    return CardOut(
        id=card.id,
        deck_id=card.deck_id,
        front=card.front,
        back=card.back,
        difficulty=card.difficulty,
        question_type=card.question_type,
        topic=card.topic,
        created_at=card.created_at,
        updated_at=card.updated_at,
    )
