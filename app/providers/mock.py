"""Mock provider — trả về dữ liệu deterministic, không gọi network."""

from __future__ import annotations

import hashlib

from .base import PlayerLookupProvider, PlayerLookupResult

_MOCK_NICKS = [
    "RongLuaChua",
    "KhanhDuTuong",
    "VoCucKiem",
    "MinhNguyetDao",
    "ThienAmKhuc",
    "VuTruVoCuc",
    "ThachSanh",
    "BachDangGiang",
    "TamSinhTamThe",
    "PhuongHoangLua",
]


def _generate_nickname(player_id: str) -> str:
    """Sinh nickname giả lập deterministic từ player_id."""
    digest = hashlib.sha256(player_id.encode("utf-8")).digest()
    base = _MOCK_NICKS[digest[0] % len(_MOCK_NICKS)]
    suffix = digest[1] % 1000
    return f"{base}{suffix:03d}"


class MockProvider(PlayerLookupProvider):
    """Provider giả lập, trả về nickname deterministic.

    - Player ID có ít nhất 6 ký tự số → coi là tồn tại.
    - Player ID quá ngắn / chứa ký tự không phải số → not found.
    """

    name = "mock"

    async def lookup_nickname(self, player_id: str) -> PlayerLookupResult:
        cleaned = player_id.strip()
        is_valid = cleaned.isdigit() and len(cleaned) >= 6
        if not is_valid:
            return PlayerLookupResult(
                player_id=cleaned,
                nickname=None,
                found=False,
                source=self.name,
            )
        return PlayerLookupResult(
            player_id=cleaned,
            nickname=_generate_nickname(cleaned),
            found=True,
            source=self.name,
        )
