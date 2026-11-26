from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import get_db
from app.models import Profile, Skill, SocialLink
from app.schemas.site import ProfileOut, SkillOut, SocialLinkOut

router = APIRouter(tags=["public"])


@router.get("/profile", response_model=ProfileOut)
async def get_profile(db: AsyncSession = Depends(get_db)):
    profile = await db.get(Profile, 1)
    if profile is None:
        raise HTTPException(404, "Профіль ще не заповнено")
    return profile


@router.get("/skills", response_model=list[SkillOut])
async def list_skills(db: AsyncSession = Depends(get_db)):
    result = await db.scalars(select(Skill).order_by(Skill.position, Skill.id))
    return result.all()


@router.get("/contacts", response_model=list[SocialLinkOut])
async def list_contacts(db: AsyncSession = Depends(get_db)):
    result = await db.scalars(
        select(SocialLink).order_by(SocialLink.position, SocialLink.id)
    )
    return result.all()