import asyncio
import secrets

from fastapi import APIRouter, Depends, Header, HTTPException, Request, Response, status
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.config import settings
from app.core.limiter import limiter
from app.db.base import get_db
from app.models import Role, User
from app.schemas.auth import BootstrapAdminIn, LoginIn, UserOut
from app.security import (
    COOKIE_NAME,
    DUMMY_HASH,
    create_access_token,
    hash_password,
    verify_password,
)

router = APIRouter(prefix="/auth", tags=["auth"])

_BOOTSTRAP_LOCK_KEY = 731902641175203


@router.post(
    "/bootstrap",
    response_model=UserOut,
    status_code=status.HTTP_201_CREATED,
)
@limiter.limit("5/minute")
async def bootstrap_admin(
    request: Request,
    data: BootstrapAdminIn,
    db: AsyncSession = Depends(get_db),
    bootstrap_secret: str | None = Header(default=None, alias="X-Bootstrap-Secret"),
):
    configured_secret = settings.BOOTSTRAP_ADMIN_SECRET
    if configured_secret is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Не знайдено")
    if bootstrap_secret is None or not secrets.compare_digest(
        bootstrap_secret,
        configured_secret.get_secret_value(),
    ):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Невірний секрет")

    await db.execute(
        text("SELECT pg_advisory_xact_lock(:key)"),
        {"key": _BOOTSTRAP_LOCK_KEY},
    )
    existing_user_id = await db.scalar(select(User.id).limit(1))
    if existing_user_id is not None:
        raise HTTPException(
            status.HTTP_409_CONFLICT,
            "Початкового адміністратора вже створено",
        )

    user = User(
        login=data.login,
        password_hash=await asyncio.to_thread(hash_password, data.password),
        role=Role.admin,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


@router.post("/login", response_model=UserOut)
@limiter.limit("5/minute")
async def login(
    request: Request,
    response: Response,
    data: LoginIn,
    db: AsyncSession = Depends(get_db),
):
    login_name = data.login.strip().lower()
    user = await db.scalar(select(User).where(User.login == login_name))

    hash_to_check = user.password_hash if user and user.password_hash else DUMMY_HASH
    # argon2 важкий для процесора, тому виносимо з event loop у потік
    password_ok = await asyncio.to_thread(
        verify_password, data.password, hash_to_check
    )
    if user is None or not user.password_hash or not password_ok:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Невірний логін або пароль")

    response.set_cookie(
        key=COOKIE_NAME,
        value=create_access_token(user.id),
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        httponly=True,
        secure=settings.ENVIRONMENT != "dev",
        samesite="lax",
        domain=settings.COOKIE_DOMAIN,
        path="/",
    )
    return user


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(response: Response):
    response.delete_cookie(
        COOKIE_NAME,
        domain=settings.COOKIE_DOMAIN,
        path="/",
        secure=settings.ENVIRONMENT != "dev",
        httponly=True,
        samesite="lax",
    )


@router.get("/me", response_model=UserOut)
async def me(user: User = Depends(get_current_user)):
    return user