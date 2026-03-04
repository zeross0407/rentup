from fastapi import APIRouter, Depends

from app.core.dependencies import get_current_user
from app.modules.users.models import User
from app.modules.users.schemas import (
    LoginResponse,
    UserCreate,
    UserLogin,
    UserResponse,
)
from app.modules.users.service import UserService
from app.schemas.base import ResponseSchema

router = APIRouter()


# ──── Auth Endpoints ────


@router.post(
    "/auth/register",
    response_model=ResponseSchema[UserResponse],
    status_code=201,
    summary="Register a new user",
)
async def register(data: UserCreate):
    """Register a new user account."""
    service = UserService()
    user = await service.register(data)
    return ResponseSchema(
        message="User registered successfully",
        data=user,
    )


@router.post(
    "/auth/login",
    response_model=ResponseSchema[LoginResponse],
    summary="Login user",
)
async def login(data: UserLogin):
    """Authenticate user and return JWT token."""
    service = UserService()
    result = await service.authenticate(data.email, data.password)
    return ResponseSchema(
        message="Login successful",
        data=result,
    )


# ──── User Endpoints ────


@router.get(
    "/users/me",
    response_model=ResponseSchema[UserResponse],
    summary="Get current user profile",
)
async def get_me(
    current_user: User = Depends(get_current_user),
):
    """Get the profile of the currently authenticated user."""
    service = UserService()
    user = await service.get_profile(current_user)
    return ResponseSchema(data=user)
