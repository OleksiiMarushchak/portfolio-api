import asyncio
import getpass
import re

from sqlalchemy import select

from app.db.base import AsyncSessionLocal, engine
from app.models import Role, User
from app.security import hash_password

LOGIN_RE = re.compile(r"^[a-z0-9_-]{3,32}$")


async def main() -> None:
    login = input("Логін адміна: ").strip().lower()
    if not LOGIN_RE.fullmatch(login):
        raise SystemExit("Логін: 3-32 символи, лише a-z, 0-9, _ або -")

    password = getpass.getpass("Пароль (мін. 10 символів): ")
    if len(password) < 10:
        raise SystemExit("Пароль закороткий")
    if password != getpass.getpass("Повторіть пароль: "):
        raise SystemExit("Паролі не збігаються")

    async with AsyncSessionLocal() as db:
        if await db.scalar(select(User).where(User.login == login)):
            raise SystemExit("Такий логін уже існує")
        db.add(User(login=login, password_hash=hash_password(password), role=Role.admin))
        await db.commit()

    await engine.dispose()
    print("Адміна створено.")


if __name__ == "__main__":
    asyncio.run(main())