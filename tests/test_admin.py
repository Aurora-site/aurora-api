import pytest
from fastapi.testclient import TestClient

from internal.db.schemas import BannerIn, CityIn
from tests.fixtures import admin_auth, city, client
from tests.fixtures.banner import (
    banner,
    banner_by_city_id,
    banner_by_locale,
    setup_banner,
)
from tests.test_user import setup_city
from tests.test_utils import init_memory_sqlite


@pytest.mark.asyncio
@init_memory_sqlite()
async def test_add_banner(client: TestClient, banner: BannerIn):
    b = setup_banner(client, banner)
    assert b == banner.model_dump()


@pytest.mark.asyncio
@init_memory_sqlite()
async def test_add_banner_with_city_id(
    client: TestClient,
    banner_by_city_id: BannerIn,
    city: CityIn,
):
    setup_city(client, city)
    b = setup_banner(client, banner_by_city_id)
    assert b == banner_by_city_id.model_dump()


@pytest.mark.asyncio
@init_memory_sqlite()
async def test_add_banner_with_locale(
    client: TestClient,
    banner_by_locale: BannerIn,
):
    b = setup_banner(client, banner_by_locale)
    assert b == banner_by_locale.model_dump()


@pytest.mark.asyncio
@init_memory_sqlite()
async def test_delete_banner(
    client: TestClient,
    banner: BannerIn,
):
    setup_banner(client, banner)
    res = client.delete(
        "/api/v1/banner/1",
        auth=admin_auth,
    )
    assert res.status_code == 200
    res = client.get("/api/v1/all-banners")
    assert res.status_code == 200
    assert res.json() == []
