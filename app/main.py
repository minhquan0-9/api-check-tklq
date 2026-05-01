"""FastAPI application entrypoint."""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import __version__
from app.config import get_settings
from app.heroes_repo import hero_count
from app.providers import build_provider
from app.routers import heroes, players


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Khởi tạo provider khi app start, đóng khi shutdown."""
    settings = get_settings()
    provider = build_provider(settings)
    app.state.player_provider = provider
    app.state.settings = settings
    try:
        yield
    finally:
        await provider.aclose()


def create_app() -> FastAPI:
    """Factory tạo FastAPI app — tách ra để test dễ inject provider khác."""
    settings = get_settings()
    app = FastAPI(
        title="API Check Tài Khoản Liên Quân Mobile",
        description=(
            "API tra cứu thông tin **công khai** của tài khoản Liên Quân Mobile.\n\n"
            "**Phạm vi:**\n"
            "- Tra cứu nickname theo Open ID — qua provider có thể cấu hình\n"
            "- Danh sách tướng / chi tiết tướng — dataset đi kèm\n"
            "- Hồ sơ người chơi (rank, level, tướng sở hữu) — STUB\n\n"
            "**Lưu ý:** Liên Quân Mobile không có public API chính thức cho rank/skin/level."
        ),
        version=__version__,
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(players.router)
    app.include_router(heroes.router)

    @app.get("/", tags=["meta"], summary="Thông tin API")
    async def root() -> dict[str, object]:
        return {
            "name": "api-check-tklq",
            "version": __version__,
            "provider": settings.lienquan_provider,
            "heroes_in_dataset": hero_count(),
            "docs": "/docs",
        }

    @app.get("/health", tags=["meta"], summary="Healthcheck")
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    return app


app = create_app()
