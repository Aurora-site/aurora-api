import pytest
from fastapi.testclient import TestClient

from internal.db.schemas import CityIn, CustIn
from tests.fixtures import city, client, setup_city, setup_user, user, user_auth
from tests.test_utils import init_memory_sqlite


@pytest.mark.asyncio
@init_memory_sqlite()
async def test_new_user(client: TestClient, user: CustIn, city: CityIn):
    setup_city(client, city)
    res = client.post(
        "/api/v1/new-user",
        json=user.model_dump(),
    )
    assert res.status_code == 200
    r = res.json()
    assert r["city_id"] == user.city_id
    assert r["locale"] == user.locale
    assert r["token"] == user.token


@pytest.mark.asyncio
@init_memory_sqlite()
async def test_new_user_exist(client: TestClient, user: CustIn, city: CityIn):
    setup_user(client, user, city)
    res = client.post(
        "/api/v1/new-user",
        json=user.model_dump(),
    )
    assert res.status_code == 409


@pytest.mark.asyncio
@init_memory_sqlite()
async def test_get_user(client: TestClient, user: CustIn, city: CityIn):
    setup_user(client, user, city)
    res = client.get(
        "/api/v1/user/1",
        auth=user_auth,
    )
    assert res.status_code == 200
    r = res.json()["cust"]
    assert r["city_id"] == user.city_id
    assert r["locale"] == user.locale
    assert r["token"] == user.token
    assert res.status_code == 200
