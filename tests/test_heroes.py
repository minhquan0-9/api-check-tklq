"""Test endpoint /api/heroes/*."""

from __future__ import annotations

from fastapi.testclient import TestClient


def test_list_heroes(client: TestClient) -> None:
    resp = client.get("/api/heroes")
    assert resp.status_code == 200
    heroes = resp.json()
    assert isinstance(heroes, list)
    assert len(heroes) > 0
    # Mỗi hero phải có id, name, role
    for h in heroes:
        assert h["id"]
        assert h["name"]
        assert h["role"] in {"TANK", "WARRIOR", "ASSASSIN", "MAGE", "MARKSMAN", "SUPPORT"}


def test_filter_by_role(client: TestClient) -> None:
    resp = client.get("/api/heroes", params={"role": "MARKSMAN"})
    assert resp.status_code == 200
    heroes = resp.json()
    assert len(heroes) > 0
    assert all(h["role"] == "MARKSMAN" for h in heroes)


def test_filter_by_role_case_insensitive(client: TestClient) -> None:
    resp = client.get("/api/heroes", params={"role": "marksman"})
    assert resp.status_code == 200
    assert len(resp.json()) > 0


def test_filter_unknown_role_empty(client: TestClient) -> None:
    resp = client.get("/api/heroes", params={"role": "UNKNOWN_ROLE"})
    assert resp.status_code == 200
    assert resp.json() == []


def test_get_hero_detail(client: TestClient) -> None:
    resp = client.get("/api/heroes/krixi")
    assert resp.status_code == 200
    body = resp.json()
    assert body["id"] == "krixi"
    assert body["name"] == "Krixi"
    assert body["role"] == "MAGE"


def test_get_hero_detail_case_insensitive(client: TestClient) -> None:
    resp = client.get("/api/heroes/KRIXI")
    assert resp.status_code == 200
    assert resp.json()["id"] == "krixi"


def test_get_hero_not_found(client: TestClient) -> None:
    resp = client.get("/api/heroes/nonexistent-hero-xyz")
    assert resp.status_code == 404
