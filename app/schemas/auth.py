from pydantic import BaseModel, ConfigDict, Field

from app.models import Role


class LoginIn(BaseModel):
    login: str = Field(max_length=64)
    password: str = Field(max_length=128)  # обмеження, щоб не хешувати величезні рядки


class BootstrapAdminIn(BaseModel):
    login: str = Field(
        min_length=3,
        max_length=32,
        pattern=r"^[a-z0-9_-]+$",
    )
    password: str = Field(min_length=10, max_length=128)


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    login: str
    role: Role