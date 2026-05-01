"""Test các provider trực tiếp."""

from __future__ import annotations

import httpx
import pytest
import respx

from app.providers.garena_shop import GarenaShopProvider
from app.providers.mock import MockProvider


async def test_mock_provider_found() -> None:
    provider = MockProvider()
    result = await provider.lookup_nickname("987654321")
    assert result.found is True
    assert result.nickname is not None
    assert result.source == "mock"


async def test_mock_provider_not_found_short() -> None:
    provider = MockProvider()
    result = await provider.lookup_nickname("123")
    assert result.found is False
    assert result.nickname is None


async def test_mock_provider_not_found_non_digit() -> None:
    provider = MockProvider()
    result = await provider.lookup_nickname("abcdef")
    assert result.found is False


async def test_mock_provider_strips_whitespace() -> None:
    provider = MockProvider()
    result = await provider.lookup_nickname("  123456  ")
    assert result.found is True
    assert result.player_id == "123456"


@respx.mock
async def test_garena_shop_provider_extracts_nickname() -> None:
    provider = GarenaShopProvider(base_url="https://shop.test", app_id="100067")
    try:
        respx.get("https://shop.test/api/shop/inv_check").mock(
            return_value=httpx.Response(200, json={"nickname": "TestPlayer"})
        )
        result = await provider.lookup_nickname("12345678")
        assert result.found is True
        assert result.nickname == "TestPlayer"
        assert result.source == "garena_shop"
    finally:
        await provider.aclose()


@respx.mock
async def test_garena_shop_provider_not_found_404() -> None:
    provider = GarenaShopProvider(base_url="https://shop.test", app_id="100067")
    try:
        respx.get("https://shop.test/api/shop/inv_check").mock(
            return_value=httpx.Response(404)
        )
        result = await provider.lookup_nickname("12345678")
        assert result.found is False
        assert result.nickname is None
    finally:
        await provider.aclose()


@respx.mock
async def test_garena_shop_provider_nested_data() -> None:
    provider = GarenaShopProvider(base_url="https://shop.test", app_id="100067")
    try:
        respx.get("https://shop.test/api/shop/inv_check").mock(
            return_value=httpx.Response(200, json={"data": {"role_name": "Quan Cong"}})
        )
        result = await provider.lookup_nickname("12345678")
        assert result.found is True
        assert result.nickname == "Quan Cong"
    finally:
        await provider.aclose()


@respx.mock
async def test_garena_shop_provider_empty_response() -> None:
    provider = GarenaShopProvider(base_url="https://shop.test", app_id="100067")
    try:
        respx.get("https://shop.test/api/shop/inv_check").mock(
            return_value=httpx.Response(200, json={})
        )
        result = await provider.lookup_nickname("12345678")
        assert result.found is False
    finally:
        await provider.aclose()


@respx.mock
async def test_garena_shop_provider_propagates_network_error() -> None:
    provider = GarenaShopProvider(base_url="https://shop.test", app_id="100067")
    try:
        respx.get("https://shop.test/api/shop/inv_check").mock(
            side_effect=httpx.ConnectError("boom")
        )
        with pytest.raises(httpx.HTTPError):
            await provider.lookup_nickname("12345678")
    finally:
        await provider.aclose()


async def test_garena_shop_rejects_non_digit() -> None:
    provider = GarenaShopProvider()
    try:
        result = await provider.lookup_nickname("abc123")
        assert result.found is False
    finally:
        await provider.aclose()
