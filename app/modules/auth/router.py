from datetime import datetime

from fastapi import APIRouter

from app.core.exceptions import ConflictException, UnauthorizedException
from app.core.security import create_access_token, hash_password, verify_password
from app.modules.auth.schemas import (
    LoginRequest,
    RefreshTokenRequest,
    RegisterRequest,
    TokenResponse,
)
from app.modules.users.models import User
from app.modules.users.schemas import UserResponse
from app.schemas.base import ResponseSchema

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post(
    "/register",
    response_model=ResponseSchema[UserResponse],
    status_code=201,
    summary="Register a new account",
)
async def register(data: RegisterRequest):
    """Register a new user with phone number and password."""
    # Check if phone already exists
    existing = await User.find_one(User.phone == data.phone)
    if existing:
        raise ConflictException(detail="Phone number already registered")

    user = User(
        phone=data.phone,
        hashed_password=hash_password(data.password),
        full_name=data.full_name,
        email=data.email,
    )
    await user.insert()
    return ResponseSchema(
        message="Registration successful",
        data=UserResponse.model_validate(user),
    )


@router.post(
    "/login",
    response_model=ResponseSchema[TokenResponse],
    summary="Login with phone and password",
)
async def login(data: LoginRequest):
    """Authenticate with phone number and password, returns JWT tokens."""
    user = await User.find_one(User.phone == data.phone)
    if not user or not verify_password(data.password, user.hashed_password):
        raise UnauthorizedException(detail="Invalid phone number or password")

    if not user.is_active:
        raise UnauthorizedException(detail="Account is deactivated")

    # Update last login
    user.last_login_at = datetime.utcnow()
    await user.save_with_timestamp()

    # Create tokens
    access_token = create_access_token(data={"sub": str(user.id)})
    refresh_token = create_access_token(
        data={"sub": str(user.id), "type": "refresh"},
    )

    return ResponseSchema(
        message="Login successful",
        data=TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
        ),
    )


@router.post(
    "/refresh",
    response_model=ResponseSchema[TokenResponse],
    summary="Refresh access token",
)
async def refresh_token(data: RefreshTokenRequest):
    """Refresh an expired access token using a refresh token."""
    from app.core.security import decode_access_token

    payload = decode_access_token(data.refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise UnauthorizedException(detail="Invalid refresh token")

    user_id = payload.get("sub")
    access_token = create_access_token(data={"sub": user_id})
    new_refresh = create_access_token(
        data={"sub": user_id, "type": "refresh"},
    )

    return ResponseSchema(
        message="Token refreshed",
        data=TokenResponse(
            access_token=access_token,
            refresh_token=new_refresh,
        ),
    )
