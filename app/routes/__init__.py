"""Routes package."""
from .generate import router as generate_router
from .auth import router as auth_router

__all__ = ["generate_router", "auth_router"]
