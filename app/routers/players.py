"""Endpoint tra cứu thông tin người chơi."""

from __future__ import annotations

from datetime import UTC, datetime

import httpx
from fastapi import APIRouter, HTTPException, Path, Request

from app.models import (
    NicknameLookupResponse,
    PlayerOwnedHero,
    PlayerProfile,
    PlayerRank,
)
from app.providers.base import PlayerLookupProvider

router = APIRouter(prefix="/api/players", tags=["players"])


def _get_provider(request: Request) -> PlayerLookupProvider:
    return request.app.state.player_provider


PLAYER_ID = Path(
    ...,
    min_length=4,
    max_length=64,
    pattern=r"^[A-Za-z0-9_-]+$",
    description="Open ID Liên Quân Mobile (số, có thể chứa _ hoặc -)",
)


@router.get(
    "/{player_id}/nickname",
    response_model=NicknameLookupResponse,
    summary="Tra cứu nickname theo Open ID",
)
async def lookup_nickname(
    request: Request,
    player_id: str = PLAYER_ID,
) -> NicknameLookupResponse:
    """Tra cứu nickname công khai của người chơi theo Open ID.

    Provider được chọn qua biến môi trường ``LIENQUAN_PROVIDER``.
    """
    provider = _get_provider(request)
    try:
        result = await provider.lookup_nickname(player_id)
    except httpx.HTTPError as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Không gọi được nguồn dữ liệu nickname: {exc}",
        ) from exc

    if not result.found:
        raise HTTPException(
            status_code=404,
            detail=f"Không tìm thấy tài khoản với ID {player_id!r}",
        )

    return NicknameLookupResponse(
        player_id=result.player_id,
        nickname=result.nickname,
        found=result.found,
        source=result.source,
        looked_up_at=datetime.now(UTC),
    )


@router.get(
    "/{player_id}/profile",
    response_model=PlayerProfile,
    summary="Hồ sơ chi tiết người chơi (stub)",
)
async def player_profile(
    request: Request,
    player_id: str = PLAYER_ID,
) -> PlayerProfile:
    """Trả về schema hồ sơ người chơi.

    **Lưu ý:** Liên Quân Mobile không có public API cho rank/level/skin.
    Endpoint này trả về dữ liệu stub đã được sinh deterministic từ Open ID
    để bạn cắm data source thật của riêng mình. Xem README phần "Cắm data source".
    """
    provider = _get_provider(request)
    try:
        result = await provider.lookup_nickname(player_id)
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    if not result.found:
        raise HTTPException(
            status_code=404,
            detail=f"Không tìm thấy tài khoản với ID {player_id!r}",
        )

    seed = sum(ord(c) for c in result.player_id)
    tiers = ["Bạc", "Vàng", "Bạch Kim", "Kim Cương", "Tinh Anh", "Cao Thủ"]
    roles = ["jungle", "mid", "ad", "sp", "ad-top"]

    return PlayerProfile(
        player_id=result.player_id,
        nickname=result.nickname,
        level=20 + (seed % 40),
        rank=PlayerRank(
            tier=tiers[seed % len(tiers)],
            division=1 + (seed % 5),
            stars=seed % 10,
            points=(seed * 7) % 100,
            season="S1-2026",
        ),
        main_role=roles[seed % len(roles)],
        main_heroes=[],
        owned_heroes_count=30 + (seed % 50),
        owned_skins_count=5 + (seed % 30),
    )


@router.get(
    "/{player_id}/heroes",
    response_model=list[PlayerOwnedHero],
    summary="Danh sách tướng người chơi sở hữu (stub)",
)
async def player_heroes(
    request: Request,
    player_id: str = PLAYER_ID,
) -> list[PlayerOwnedHero]:
    """Danh sách tướng người chơi sở hữu — stub.

    Hiện trả về danh sách rỗng kèm 404 nếu không tìm thấy player.
    Khi có data source riêng (DB, API nội bộ), implement trong app/providers
    rồi thay thế ở đây.
    """
    provider = _get_provider(request)
    try:
        result = await provider.lookup_nickname(player_id)
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    if not result.found:
        raise HTTPException(
            status_code=404,
            detail=f"Không tìm thấy tài khoản với ID {player_id!r}",
        )
    return []
