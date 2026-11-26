from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from app.core.config import settings

database_url = settings.DATABASE_URL
if database_url.startswith("postgres://"):
    database_url = "postgresql://" + database_url.removeprefix("postgres://")
if database_url.startswith("postgresql://"):
    database_url = "postgresql+asyncpg://" + database_url.removeprefix(
        "postgresql://"
    )

if "postgresql+asyncpg://" in database_url:
    parts = urlsplit(database_url)
    query = [
        ("ssl", value)
        if key == "sslmode"
        else (key, value)
        for key, value in parse_qsl(parts.query, keep_blank_values=True)
        if key not in {"channel_binding"}
    ]
    database_url = urlunsplit(
        (parts.scheme, parts.netloc, parts.path, urlencode(query), parts.fragment)
    )

engine = create_async_engine(
    database_url,
    pool_size=5,
    max_overflow=10,
    pool_timeout=15,
    pool_recycle=900,
    echo=settings.ENVIRONMENT == "dev",
    pool_pre_ping=True,
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

Base = declarative_base()


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session