"""Providers — adapter cho các nguồn dữ liệu lookup nickname Liên Quân."""

from __future__ import annotations

from app.config import Settings

from .base import PlayerLookupProvider, PlayerLookupResult
from .garena_shop import GarenaShopProvider
from .mock import MockProvider

__all__ = [
    "GarenaShopProvider",
    "MockProvider",
    "PlayerLookupProvider",
    "PlayerLookupResult",
    "build_provider",
]


def build_provider(settings: Settings) -> PlayerLookupProvider:
    """Khởi tạo provider dựa trên config."""
    name = settings.lienquan_provider.lower().strip()
    if name == "mock":
        return MockProvider()
    if name == "garena_shop":
        return GarenaShopProvider(
            base_url=settings.garena_shop_base_url,
            app_id=settings.garena_shop_app_id,
            timeout=settings.garena_shop_timeout,
        )
    raise ValueError(
        f"LIENQUAN_PROVIDER không hợp lệ: {settings.lienquan_provider!r}. "
        "Giá trị hỗ trợ: mock | garena_shop"
    )
