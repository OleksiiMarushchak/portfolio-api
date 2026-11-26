import jwt
from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import get_db
from app.models import Role, User
from app.security import COOKIE_NAME, decode_access_token


def _unauthorized() -> HTTPException:
    return HTTPException(status.HTTP_401_UNAUTHORIZED, "Потрібна авторизація")


async def get_current_user(
    request: Request, db: AsyncSession = Depends(get_db)
) -> User:
    token = request.cookies.get(COOKIE_NAME)
    if not token:
        raise _unauthorized()
    try:
        user_id = int(decode_access_token(token)["sub"])
    except (jwt.PyJWTError, ValueError):
        raise _unauthorized()
    user = await db.get(User, user_id)
    if user is None:
        raise _unauthorized()
    return user


async def get_current_admin(user: User = Depends(get_current_user)) -> User:
    if user.role != Role.admin:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Недостатньо прав")
    return user