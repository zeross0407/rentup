from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from beanie import PydanticObjectId

from app.core.exceptions import UnauthorizedException
from app.core.security import decode_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
):
    """
    Dependency to extract and validate the current user from JWT token.
    Returns the User document from MongoDB.
    """
    payload = decode_access_token(token)
    if payload is None:
        raise UnauthorizedException()

    user_id: str = payload.get("sub")
    if user_id is None:
        raise UnauthorizedException()

    # Import here to avoid circular imports
    from app.modules.users.models import User

    user = await User.get(PydanticObjectId(user_id))
    if user is None:
        raise UnauthorizedException(detail="User not found")

    return user
