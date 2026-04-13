"""Authentication endpoints."""
import logging

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.user import User
from app.schemas.auth import AuthResponse, AuthResponseData, LoginRequest, RegisterRequest, UserOut
from app.utils.security import hash_password, verify_password

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


@router.post("/register", response_model=AuthResponse)
def register_user(request: RegisterRequest, db: Session = Depends(get_db)) -> AuthResponse:
    """Register a new user account."""
    existing_user = db.query(User).filter(User.email == request.email).first()
    if existing_user:
        return AuthResponse(
            success=False,
            data=None,
            message="Email already registered",
            error={"type": "UserAlreadyExists", "details": "Email is already in use"}
        )

    user = User(
        email=request.email,
        hashed_password=hash_password(request.password),
        full_name=request.full_name
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    logger.info("Registered user %s", user.email)

    return AuthResponse(
        success=True,
        data=AuthResponseData(
            user=UserOut(
                id=user.id,
                email=user.email,
                full_name=user.full_name,
                created_at=user.created_at
            )
        ),
        message="Registration successful",
        error=None
    )


@router.post("/login", response_model=AuthResponse)
def login_user(request: LoginRequest, db: Session = Depends(get_db)) -> AuthResponse:
    """Authenticate an existing user."""
    user = db.query(User).filter(User.email == request.email).first()
    if not user or not verify_password(request.password, user.hashed_password):
        return AuthResponse(
            success=False,
            data=None,
            message="Invalid credentials",
            error={"type": "InvalidCredentials", "details": "Email or password is incorrect"}
        )

    return AuthResponse(
        success=True,
        data=AuthResponseData(
            user=UserOut(
                id=user.id,
                email=user.email,
                full_name=user.full_name,
                created_at=user.created_at
            )
        ),
        message="Login successful",
        error=None
    )
