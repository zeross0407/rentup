from typing import Optional

from beanie import PydanticObjectId

from app.modules.users.models import User


class UserRepository:
    """Repository for User database operations (Beanie/MongoDB)."""

    async def get_by_id(self, user_id: PydanticObjectId) -> Optional[User]:
        """Get a user by their ID."""
        return await User.get(user_id)

    async def get_by_email(self, email: str) -> Optional[User]:
        """Get a user by their email address."""
        return await User.find_one(User.email == email)

    async def create(self, user: User) -> User:
        """Create a new user in the database."""
        await user.insert()
        return user

    async def update(self, user: User, **kwargs) -> User:
        """Update user fields."""
        for key, value in kwargs.items():
            if hasattr(user, key) and value is not None:
                setattr(user, key, value)
        await user.save_with_timestamp()
        return user
