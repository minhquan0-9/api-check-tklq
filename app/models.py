"""Pydantic models cho request/response."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class NicknameLookupResponse(BaseModel):
    """Kết quả tra cứu nickname theo player ID."""

    player_id: str = Field(..., description="Open ID người chơi đã tra cứu")
    nickname: str | None = Field(None, description="Nickname trong game (None nếu không tìm thấy)")
    found: bool = Field(..., description="True nếu tìm thấy tài khoản")
    source: str = Field(..., description="Nguồn dữ liệu (mock | garena_shop | ...)")
    looked_up_at: datetime = Field(..., description="Thời điểm tra cứu (UTC)")


class HeroSkill(BaseModel):
    """Một kỹ năng (skill) của tướng."""

    slot: str = Field(..., description="Vị trí skill: passive, q, w, e, r")
    name: str = Field(..., description="Tên kỹ năng")
    description: str | None = None


class HeroSkin(BaseModel):
    """Một skin/trang phục của tướng."""

    id: str
    name: str
    rarity: str | None = Field(None, description="Mức độ hiếm: normal, epic, legend, ...")
    image_url: str | None = None


class Hero(BaseModel):
    """Thông tin một tướng trong Liên Quân Mobile."""

    id: str = Field(..., description="ID tướng")
    name: str = Field(..., description="Tên tướng")
    title: str | None = Field(None, description="Danh hiệu tướng")
    role: str = Field(..., description="Vai trò: TANK, WARRIOR, ASSASSIN, MAGE, MARKSMAN, SUPPORT")
    lane: str | None = Field(None, description="Đường đánh: jungle, mid, ad, sp, abyssal")
    avatar_url: str | None = None
    skills: list[HeroSkill] = Field(default_factory=list)
    skins: list[HeroSkin] = Field(default_factory=list)


class HeroSummary(BaseModel):
    """Bản rút gọn của Hero, dùng cho danh sách."""

    id: str
    name: str
    role: str
    avatar_url: str | None = None


class PlayerRank(BaseModel):
    """Thông tin rank của người chơi."""

    tier: str = Field(..., description="Bậc xếp hạng: bronze, silver, gold, platinum, diamond, ...")
    division: int | None = Field(None, description="Mức trong bậc, ví dụ Diamond III thì là 3")
    stars: int = Field(0, description="Sao hiện có")
    points: int = Field(0, description="Điểm tích luỹ trong bậc")
    season: str | None = Field(None, description="Mùa giải, ví dụ S1-2025")


class PlayerOwnedHero(BaseModel):
    """Một tướng người chơi sở hữu."""

    hero_id: str
    hero_name: str
    level: int = 1
    skins_owned: list[str] = Field(default_factory=list)


class PlayerProfile(BaseModel):
    """Hồ sơ chi tiết của người chơi (stub — cần data source riêng để fill thực tế)."""

    player_id: str
    nickname: str | None
    level: int | None = None
    rank: PlayerRank | None = None
    main_role: str | None = None
    main_heroes: list[str] = Field(default_factory=list)
    owned_heroes_count: int | None = None
    owned_skins_count: int | None = None
    note: str = Field(
        "Dữ liệu chi tiết (rank, tướng, skin) hiện trả về stub — "
        "Liên Quân Mobile không có public API. Cắm data source của bạn trong "
        "app/providers để có dữ liệu thật.",
        description="Ghi chú về nguồn dữ liệu",
    )


class ErrorResponse(BaseModel):
    """Response lỗi chung."""

    error: str
    detail: str | None = None
