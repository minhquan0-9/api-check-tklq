"""Provider gọi Garena Shop để xác minh & lấy nickname theo Open ID Liên Quân.

Lưu ý quan trọng:
    - Endpoint shop.garena.vn thường giới hạn IP Việt Nam. Khi chạy ngoài Việt Nam
      bạn cần proxy hoặc deploy server tại VN.
    - Garena không công bố API chính thức. Cấu trúc request/response dưới đây dựa
      trên flow tra cứu nạp thẻ công khai và có thể thay đổi theo thời gian. Nếu
      Garena đổi schema, sửa lại class này (chỉ một chỗ).
"""

from __future__ import annotations

import logging

import httpx

from .base import PlayerLookupProvider, PlayerLookupResult

logger = logging.getLogger(__name__)


class GarenaShopProvider(PlayerLookupProvider):
    """Tra cứu nickname Liên Quân qua trang nạp thẻ Garena Shop.

    Args:
        base_url: gốc URL của shop, mặc định ``https://shop.garena.vn``.
        app_id: ID ứng dụng Liên Quân trong hệ thống Garena (thường là ``100067``).
        timeout: timeout mỗi request (giây).
    """

    name = "garena_shop"

    def __init__(
        self,
        base_url: str = "https://shop.garena.vn",
        app_id: str = "100067",
        timeout: float = 10.0,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._app_id = app_id
        self._client = httpx.AsyncClient(
            timeout=timeout,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/120.0 Safari/537.36"
                ),
                "Accept": "application/json, text/plain, */*",
                "Accept-Language": "vi-VN,vi;q=0.9,en;q=0.8",
                "Referer": f"{self._base_url}/",
                "Origin": self._base_url,
            },
            follow_redirects=True,
        )

    async def aclose(self) -> None:
        await self._client.aclose()

    async def lookup_nickname(self, player_id: str) -> PlayerLookupResult:
        cleaned = player_id.strip()
        if not cleaned.isdigit():
            return PlayerLookupResult(
                player_id=cleaned, nickname=None, found=False, source=self.name
            )

        # Endpoint nội bộ Garena dùng để check nickname trước khi nạp.
        # Đây là endpoint không công khai — nếu Garena thay đổi, cần cập nhật ở đây.
        url = f"{self._base_url}/api/shop/inv_check"
        params = {
            "app_id": self._app_id,
            "user_id": cleaned,
            "server_id": "0",
        }

        try:
            resp = await self._client.get(url, params=params)
        except httpx.HTTPError as exc:
            logger.warning("Garena shop request thất bại cho id=%s: %s", cleaned, exc)
            raise

        if resp.status_code == 404:
            return PlayerLookupResult(
                player_id=cleaned, nickname=None, found=False, source=self.name
            )
        resp.raise_for_status()

        try:
            payload = resp.json()
        except ValueError:
            logger.warning("Phản hồi Garena không phải JSON: %r", resp.text[:200])
            return PlayerLookupResult(
                player_id=cleaned, nickname=None, found=False, source=self.name
            )

        nickname = self._extract_nickname(payload)
        return PlayerLookupResult(
            player_id=cleaned,
            nickname=nickname,
            found=nickname is not None,
            source=self.name,
        )

    @staticmethod
    def _extract_nickname(payload: object) -> str | None:
        """Lấy nickname từ payload trả về.

        Thử nhiều key khác nhau vì Garena không có schema cố định công khai.
        """
        if not isinstance(payload, dict):
            return None
        for key in ("nickname", "user_name", "username", "role_name", "name"):
            value = payload.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()
        # Một số endpoint trả nested {"data": {...}}
        data = payload.get("data")
        if isinstance(data, dict):
            for key in ("nickname", "user_name", "username", "role_name", "name"):
                value = data.get(key)
                if isinstance(value, str) and value.strip():
                    return value.strip()
        return None
