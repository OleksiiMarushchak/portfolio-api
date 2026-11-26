from typing import Annotated

from pydantic import (
    AfterValidator,
    BaseModel,
    ConfigDict,
    Field,
    HttpUrl,
    StringConstraints,
    TypeAdapter,
)

from app.models import SkillCategory

_http_url = TypeAdapter(HttpUrl)


def _check_http_url(value: str) -> str:
    _http_url.validate_python(value)  # дозволяє лише http(s), без javascript: тощо
    return value


UrlStr = Annotated[
    str,
    StringConstraints(strip_whitespace=True, max_length=500),
    AfterValidator(_check_http_url),
]


def _text(max_length: int, min_length: int = 0):
    return Annotated[
        str,
        StringConstraints(
            strip_whitespace=True, min_length=min_length, max_length=max_length
        ),
    ]


class ProfileIn(BaseModel):
    full_name: _text(100, min_length=1)
    headline: _text(200) | None = None
    bio: str | None = Field(default=None, max_length=2000)
    about: str | None = Field(default=None, max_length=20000)  # markdown
    photo_url: UrlStr | None = None


class ProfileOut(ProfileIn):
    model_config = ConfigDict(from_attributes=True)


class SkillIn(BaseModel):
    name: _text(50, min_length=1)
    category: SkillCategory
    level: int | None = Field(default=None, ge=1, le=5)
    position: int = Field(default=0, ge=0)


class SkillOut(SkillIn):
    model_config = ConfigDict(from_attributes=True)

    id: int


class SocialLinkIn(BaseModel):
    kind: _text(32, min_length=1)  # "linkedin", "telegram", "instagram", ...
    label: _text(50, min_length=1)
    url: UrlStr
    position: int = Field(default=0, ge=0)


class SocialLinkOut(SocialLinkIn):
    model_config = ConfigDict(from_attributes=True)

    id: int