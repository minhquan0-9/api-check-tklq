"""Fixtures dùng chung cho test."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.main import create_app


@pytest.fixture
def client() -> TestClient:
    """Test client với MockProvider mặc định."""
    app = create_app()
    with TestClient(app) as c:
        yield c
