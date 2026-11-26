import asyncio
import sys

import app.models  # noqa: F401  (реєструє моделі в Base.metadata)
from app.core.config import settings
from app.db.base import Base, engine


async def main(reset: bool) -> None:
    async with engine.begin() as conn:
        if reset:
            if settings.ENVIRONMENT != "dev":
                sys.exit("Reset дозволений лише при ENVIRONMENT=dev")
            await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    await engine.dispose()
    print("Готово.")


if __name__ == "__main__":
    asyncio.run(main(reset="--reset" in sys.argv))