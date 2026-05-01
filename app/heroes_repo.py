"""Truy cập dataset tướng từ file JSON đi kèm."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

from app.models import Hero, HeroSummary

_DATA_FILE = Path(__file__).parent / "data" / "heroes.json"


@lru_cache(maxsize=1)
def _load_heroes() -> list[Hero]:
    """Đọc file JSON, parse thành list Hero. Cache để chỉ đọc một lần."""
    with _DATA_FILE.open("r", encoding="utf-8") as f:
        raw = json.load(f)
    return [Hero(**item) for item in raw]


def list_heroes(role: str | None = None) -> list[HeroSummary]:
    """Trả về danh sách rút gọn của tướng, có thể lọc theo role."""
    heroes = _load_heroes()
    if role:
        role_upper = role.upper()
        heroes = [h for h in heroes if h.role.upper() == role_upper]
    return [
        HeroSummary(id=h.id, name=h.name, role=h.role, avatar_url=h.avatar_url)
        for h in heroes
    ]


def get_hero(hero_id: str) -> Hero | None:
    """Lấy chi tiết một tướng theo id (case-insensitive)."""
    target = hero_id.lower().strip()
    for hero in _load_heroes():
        if hero.id.lower() == target:
            return hero
    return None


def hero_count() -> int:
    """Số lượng tướng trong dataset."""
    return len(_load_heroes())
