import pytest
from fastapi.testclient import TestClient

from internal.db.schemas import BannerIn, CityIn
from tests.test_api import city
from tests.test_user import setup_city
from tests.test_utils import admin_auth, client, init_memory_sqlite


@pytest.fixture
def banner():
    return BannerIn(
        default=True,
        name="test",
        url="https://test.com/test.png",
    )


def setup_banner(client: TestClient, banner: BannerIn) -> dict:
    res = client.post(
        "/api/v1/set-banner",
        json=banner.model_dump(),
        auth=admin_auth,
    )
    assert res.status_code == 200
    return res.json()


@pytest.mark.asyncio
@init_memory_sqlite()
async def test_add_banner(client: TestClient, banner: BannerIn):
    b = setup_banner(client, banner)
    assert b == banner.model_dump()


@pytest.fixture
def banner_by_city_id():
    return BannerIn(
        city_id=1,
        name="test",
        url="https://test.com/test.png",
    )


@pytest.mark.asyncio
@init_memory_sqlite()
async def test_add_banner_with_city_id(
    client: TestClient,
    banner_by_city_id: BannerIn,
    city: CityIn,
):
    _ = setup_city(client, city)
    b = setup_banner(client, banner_by_city_id)
    assert b == banner_by_city_id.model_dump()


@pytest.fixture
def banner_by_locale():
    return BannerIn(
        locale="ru",
        name="test",
        url="https://test.com/test.png",
    )


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
    _ = setup_banner(client, banner)
    res = client.delete(
        "/api/v1/banner/1",
        auth=admin_auth,
    )
    assert res.status_code == 200
    res = client.get("/api/v1/all-banners")
    assert res.status_code == 200
    assert res.json() == []
