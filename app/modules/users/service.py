from app.core.exceptions import ConflictException, UnauthorizedException
from app.core.security import create_access_token, hash_password, verify_password
from app.modules.users.models import User
from app.modules.users.repository import UserRepository
from app.modules.users.schemas import LoginResponse, UserCreate, UserResponse


class UserService:
    """Service layer for User business logic."""

    def __init__(self):
        self.repo = UserRepository()

    async def register(self, data: UserCreate) -> UserResponse:
        """Register a new user."""
        # Check if email already exists
        existing = await self.repo.get_by_email(data.email)
        if existing:
            raise ConflictException(detail="Email already registered")

        # Create user
        user = User(
            email=data.email,
            hashed_password=hash_password(data.password),
            full_name=data.full_name,
            phone=data.phone,
        )
        user = await self.repo.create(user)
        return UserResponse.model_validate(user)

    async def authenticate(self, email: str, password: str) -> LoginResponse:
        """Authenticate user and return JWT token."""
        user = await self.repo.get_by_email(email)
        if not user or not verify_password(password, user.hashed_password):
            raise UnauthorizedException(detail="Invalid email or password")

        if not user.is_active:
            raise UnauthorizedException(detail="Account is deactivated")

        # Create JWT token
        access_token = create_access_token(data={"sub": str(user.id)})

        return LoginResponse(
            access_token=access_token,
            user=UserResponse.model_validate(user),
        )

    async def get_profile(self, user: User) -> UserResponse:
        """Get user profile."""
        return UserResponse.model_validate(user)
