"""Interface chuẩn cho provider lookup nickname."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class PlayerLookupResult:
    """Kết quả thô từ provider, đã chuẩn hoá."""

    player_id: str
    nickname: str | None
    found: bool
    source: str


class PlayerLookupProvider(ABC):
    """Provider lookup nickname theo player ID.

    Mọi provider cần kế thừa lớp này và implement `lookup_nickname`.
    """

    name: str

    @abstractmethod
    async def lookup_nickname(self, player_id: str) -> PlayerLookupResult:
        """Tra cứu nickname theo player_id.

        Return:
            PlayerLookupResult — `found=False` và `nickname=None` nếu không tìm thấy
            hoặc input không hợp lệ. KHÔNG raise exception cho trường hợp not-found;
            chỉ raise khi có lỗi network/server thực sự.
        """

    async def aclose(self) -> None:  # noqa: B027 — optional override
        """Đóng tài nguyên (HTTP client, ...). Mặc định no-op."""
