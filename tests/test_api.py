import pytest
from fastapi.testclient import TestClient

from internal.db.schemas import BannerIn, CityIn
from internal.db.test_models import city
from main import app
from tests.test_admin import banner, setup_banner
from tests.test_utils import admin_auth, init_memory_sqlite


@pytest.fixture
def client():
    return TestClient(app)


def test_health(client: TestClient):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.asyncio
@init_memory_sqlite()
async def test_add_remove_city(client: TestClient, city: CityIn):
    ct = city.model_dump()
    ct |= {"id": 1}
    res = client.post(
        "/api/v1/new-city",
        json=city.model_dump(),
        auth=admin_auth,
    )
    assert res.status_code == 200
    assert res.json() == ct
    res = client.get("/api/v1/all-cities")
    assert res.status_code == 200
    assert res.json() == [ct]
    res = client.delete("/api/v1/city/1", auth=admin_auth)
    assert res.status_code == 200
    res = client.get("/api/v1/all-cities")
    assert res.status_code == 200
    assert res.json() == []


@pytest.mark.asyncio
@init_memory_sqlite()
async def test_update_city(client: TestClient, city: CityIn):
    ct = city.model_dump()
    ct |= {"id": 1}
    res = client.post(
        "/api/v1/new-city",
        json=city.model_dump(),
        auth=admin_auth,
    )
    assert res.status_code == 200
    assert res.json() == ct
    upd = {
        "name_ru": "test",
        "name_en": "test",
        "name_cn": "test",
    }
    res = client.put(
        "/api/v1/city/1",
        json=upd,
        auth=admin_auth,
    )
    assert res.status_code == 200
    assert res.json() == ct | upd


@pytest.mark.asyncio
@init_memory_sqlite()
async def test_get_banner_not_found(client: TestClient, banner: BannerIn):
    res = client.get("/api/v1/banner")
    assert res.status_code == 404


@pytest.mark.asyncio
@init_memory_sqlite()
async def test_get_banner(client: TestClient, banner: BannerIn):
    b = setup_banner(client, banner)
    res = client.get("/api/v1/banner")
    assert res.status_code == 200
    assert res.json() == b
