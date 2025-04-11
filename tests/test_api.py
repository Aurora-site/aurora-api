import pytest
from fastapi.testclient import TestClient

from internal.db.schemas import BannerIn, CityIn
from internal.db.test_models import city
from main import app
from tests.test_utils import (
    admin_auth,
    banner,
    city,
    init_memory_sqlite,
    setup_banner,
    setup_city,
)


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


@pytest.mark.asyncio
@init_memory_sqlite()
async def test_personal_banner_not_found(client: TestClient):
    res = client.post(
        "/api/v1/personal-banner",
        json={"default": True},
        auth=admin_auth,
    )
    assert res.status_code == 404


# @pytest.mark.asyncio
# @init_memory_sqlite()
# async def test_personal_banner_city_id(
#     client: TestClient,
#     city: CityIn,
# ):
#     setup_city(client, city)
#     b = setup_banner(
#         client,
#         BannerIn(
#             city_id=1,
#             name="aboba",
#             url="https://test.com/test.png",
#         ),
#     )
#     res = client.post(
#         "/api/v1/personal-banner",
#         json={"city_id": 1},
#         auth=admin_auth,
#     )
#     assert res.status_code == 200
#     assert res.json() == b


# @pytest.mark.asyncio
# @init_memory_sqlite()
# async def test_personal_banner_locale(
#     client: TestClient,
#     banner: BannerIn,
#     city: CityIn,
# ):
#     setup_city(client, city)
#     b = setup_banner(
#         client,
#         BannerIn(
#             locale="ru",
#             name="amogus",
#             url="https://test.com/test.png",
#         ),
#     )
#     res = client.post(
#         "/api/v1/personal-banner",
#         json={"locale": "ru"},
#         auth=admin_auth,
#     )
#     assert res.status_code == 200
#     assert res.json() == b


# @pytest.mark.asyncio
# @init_memory_sqlite()
# async def test_personal_banner_default(
#     client: TestClient,
#     banner: BannerIn,
#     city: CityIn,
# ):
#     setup_city(client, city)
#     b = setup_banner(client, banner)
#     res = client.post(
#         "/api/v1/personal-banner",
#         json={"default": True},
#         auth=admin_auth,
#     )
#     assert res.status_code == 200
#     assert res.json() == b


@pytest.mark.asyncio
@init_memory_sqlite()
async def test_personal_banner_city_id_locale(
    client: TestClient,
    city: CityIn,
):
    setup_city(client, city)
    b = setup_banner(
        client,
        BannerIn(
            city_id=1,
            locale="ru",
            name="amogus-aboba",
            url="https://test.com/test.png",
        ),
    )
    res = client.post(
        "/api/v1/personal-banner",
        json={"city_id": 1, "locale": "ru"},
        auth=admin_auth,
    )
    assert res.status_code == 200
    assert res.json() == b


@pytest.mark.asyncio
@init_memory_sqlite()
async def test_all_banner_default(
    client: TestClient,
    banner: BannerIn,
    city: CityIn,
):
    setup_city(client, city)
    b = setup_banner(client, banner)
    b["id"] = 1
    res = client.get(
        "/api/v1/all-banners",
    )
    assert res.status_code == 200
    assert res.json() == [b]
