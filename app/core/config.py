from pathlib import Path

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parent.parent / ".env",
        extra="ignore",
    )

    ENVIRONMENT: str = "dev"  # "dev" або "prod"
    DATABASE_URL: str
    SECRET_KEY: str
    BOOTSTRAP_ADMIN_SECRET: SecretStr | None = Field(default=None, min_length=32)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    FRONTEND_ORIGIN: str = "http://localhost:3000"
    COOKIE_DOMAIN: str | None = None  # у проді ".th1rd.net"


settings = Settings()