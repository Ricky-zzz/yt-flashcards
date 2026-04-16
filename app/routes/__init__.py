"""Routes package."""
from .generate import router as generate_router
from .auth import router as auth_router
from .decks import router as decks_router
from .reviews import router as reviews_router

__all__ = ["generate_router", "auth_router", "decks_router", "reviews_router"]
