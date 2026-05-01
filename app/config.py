"""Cấu hình ứng dụng đọc từ biến môi trường."""

from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Cấu hình runtime, đọc từ env hoặc file .env."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Lựa chọn provider lookup nickname
    lienquan_provider: str = "mock"

    # Cấu hình cho GarenaShopProvider
    garena_shop_base_url: str = "https://shop.garena.vn"
    garena_shop_app_id: str = "100067"
    garena_shop_timeout: float = 10.0

    # CORS
    cors_origins: str = "*"

    # Server
    host: str = "0.0.0.0"
    port: int = 8000

    @property
    def cors_origins_list(self) -> list[str]:
        """Danh sách origin sau khi tách từ chuỗi config."""
        if self.cors_origins.strip() == "*":
            return ["*"]
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


def get_settings() -> Settings:
    """Trả về instance Settings (đọc lại env mỗi lần gọi cho test)."""
    return Settings()
