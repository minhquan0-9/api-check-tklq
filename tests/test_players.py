"""Test endpoint /api/players/*."""

from __future__ import annotations

from fastapi.testclient import TestClient

VALID_ID = "123456789"
SHORT_ID = "12345"  # < 6 chars → mock provider trả not found, nhưng route min_length=4 nên nhận
INVALID_FORMAT_ID = "abc%24"  # chứa $ encoded — không khớp pattern ^[A-Za-z0-9_-]+$
TOO_SHORT_ID = "ab"  # < min_length=4 → 422


def test_lookup_nickname_found(client: TestClient) -> None:
    resp = client.get(f"/api/players/{VALID_ID}/nickname")
    assert resp.status_code == 200
    body = resp.json()
    assert body["player_id"] == VALID_ID
    assert body["found"] is True
    assert body["nickname"]
    assert body["source"] == "mock"
    assert "looked_up_at" in body


def test_lookup_nickname_deterministic(client: TestClient) -> None:
    """Cùng input → cùng nickname (mock provider deterministic)."""
    a = client.get(f"/api/players/{VALID_ID}/nickname").json()
    b = client.get(f"/api/players/{VALID_ID}/nickname").json()
    assert a["nickname"] == b["nickname"]


def test_lookup_nickname_not_found_short_id(client: TestClient) -> None:
    resp = client.get(f"/api/players/{SHORT_ID}/nickname")
    assert resp.status_code == 404


def test_lookup_nickname_invalid_format(client: TestClient) -> None:
    """Path validator reject ký tự đặc biệt (đã URL-encode)."""
    resp = client.get(f"/api/players/{INVALID_FORMAT_ID}/nickname")
    assert resp.status_code == 422


def test_lookup_nickname_too_short(client: TestClient) -> None:
    """Path validator reject id < min_length."""
    resp = client.get(f"/api/players/{TOO_SHORT_ID}/nickname")
    assert resp.status_code == 422


def test_player_profile_stub(client: TestClient) -> None:
    resp = client.get(f"/api/players/{VALID_ID}/profile")
    assert resp.status_code == 200
    body = resp.json()
    assert body["player_id"] == VALID_ID
    assert body["nickname"]
    assert body["rank"]["tier"]
    assert body["rank"]["season"] == "S1-2026"
    assert "stub" in body["note"].lower() or "data source" in body["note"].lower()


def test_player_heroes_stub(client: TestClient) -> None:
    resp = client.get(f"/api/players/{VALID_ID}/heroes")
    assert resp.status_code == 200
    assert resp.json() == []


def test_player_heroes_not_found(client: TestClient) -> None:
    resp = client.get(f"/api/players/{SHORT_ID}/heroes")
    assert resp.status_code == 404
