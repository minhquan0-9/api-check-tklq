"""Endpoint cho danh sách tướng (data thật, đi kèm app)."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Path, Query

from app.heroes_repo import get_hero, list_heroes
from app.models import Hero, HeroSummary

router = APIRouter(prefix="/api/heroes", tags=["heroes"])


@router.get(
    "",
    response_model=list[HeroSummary],
    summary="Danh sách tướng (có thể lọc theo role)",
)
async def get_all_heroes(
    role: str | None = Query(
        None,
        description="Lọc theo role: TANK, WARRIOR, ASSASSIN, MAGE, MARKSMAN, SUPPORT",
    ),
) -> list[HeroSummary]:
    return list_heroes(role=role)


@router.get(
    "/{hero_id}",
    response_model=Hero,
    summary="Chi tiết một tướng",
)
async def get_hero_detail(
    hero_id: str = Path(..., min_length=1, max_length=64),
) -> Hero:
    hero = get_hero(hero_id)
    if hero is None:
        raise HTTPException(
            status_code=404,
            detail=f"Không tìm thấy tướng với id {hero_id!r}",
        )
    return hero
