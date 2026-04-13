"""Auth schemas for register/login endpoints."""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    """Request payload for user registration."""
    email: EmailStr
    password: str = Field(..., min_length=6)
    full_name: Optional[str] = None


class LoginRequest(BaseModel):
    """Request payload for user login."""
    email: EmailStr
    password: str


class UserOut(BaseModel):
    """Public user payload."""
    id: int
    email: EmailStr
    full_name: Optional[str] = None
    created_at: datetime


class AuthResponseData(BaseModel):
    """Auth response data payload."""
    user: UserOut


class AuthResponse(BaseModel):
    """Standard response wrapper for auth endpoints."""
    success: bool
    data: Optional[AuthResponseData] = None
    message: str
    error: Optional[dict] = None
