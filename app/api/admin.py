from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_admin
from app.db.base import get_db
from app.models import Profile, Skill, SocialLink
from app.schemas.site import (
    ProfileIn,
    ProfileOut,
    SkillIn,
    SkillOut,
    SocialLinkIn,
    SocialLinkOut,
)

router = APIRouter(
    prefix="/admin",
    tags=["admin"],
    dependencies=[Depends(get_current_admin)],
)


async def _get_or_404(db: AsyncSession, model, item_id: int):
    obj = await db.get(model, item_id)
    if obj is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Не знайдено")
    return obj


def _apply(obj, data) -> None:
    for field, value in data.model_dump().items():
        setattr(obj, field, value)


# ---- Профіль ("про мене") ----

@router.put("/profile", response_model=ProfileOut)
async def update_profile(data: ProfileIn, db: AsyncSession = Depends(get_db)):
    profile = await db.get(Profile, 1)
    if profile is None:
        profile = Profile(id=1)
        db.add(profile)
    _apply(profile, data)
    await db.commit()
    await db.refresh(profile)
    return profile


# ---- Стек ----

@router.post("/skills", response_model=SkillOut, status_code=status.HTTP_201_CREATED)
async def create_skill(data: SkillIn, db: AsyncSession = Depends(get_db)):
    skill = Skill(**data.model_dump())
    db.add(skill)
    await db.commit()
    await db.refresh(skill)
    return skill


@router.put("/skills/{skill_id}", response_model=SkillOut)
async def update_skill(
    skill_id: int, data: SkillIn, db: AsyncSession = Depends(get_db)
):
    skill = await _get_or_404(db, Skill, skill_id)
    _apply(skill, data)
    await db.commit()
    await db.refresh(skill)
    return skill


@router.delete("/skills/{skill_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_skill(skill_id: int, db: AsyncSession = Depends(get_db)):
    skill = await _get_or_404(db, Skill, skill_id)
    await db.delete(skill)
    await db.commit()


# ---- Контакти ----

@router.post(
    "/contacts", response_model=SocialLinkOut, status_code=status.HTTP_201_CREATED
)
async def create_contact(data: SocialLinkIn, db: AsyncSession = Depends(get_db)):
    link = SocialLink(**data.model_dump())
    db.add(link)
    await db.commit()
    await db.refresh(link)
    return link


@router.put("/contacts/{link_id}", response_model=SocialLinkOut)
async def update_contact(
    link_id: int, data: SocialLinkIn, db: AsyncSession = Depends(get_db)
):
    link = await _get_or_404(db, SocialLink, link_id)
    _apply(link, data)
    await db.commit()
    await db.refresh(link)
    return link


@router.delete("/contacts/{link_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_contact(link_id: int, db: AsyncSession = Depends(get_db)):
    link = await _get_or_404(db, SocialLink, link_id)
    await db.delete(link)
    await db.commit()