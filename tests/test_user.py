import httpx
import pytest
from fastapi.testclient import TestClient

from internal.db.schemas import CityIn, CustIn
from tests.test_api import city
from tests.test_utils import admin_auth, client, init_memory_sqlite

user_auth = httpx.BasicAuth(username="1", password="test")


@pytest.fixture
def user():
    return CustIn(
        city_id=1,
        locale="ru",
        token="test",
    )


def setup_city(client: TestClient, city: CityIn):
    ct = city.model_dump()
    ct |= {"id": 1}
    res = client.post(
        "/api/v1/new-city",
        json=city.model_dump(),
        auth=admin_auth,
    )
    assert res.status_code == 200
    return ct


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

    return res


def setup_user(client: TestClient, user: CustIn):
    res = client.post(
        "/api/v1/new-user",
        json=user.model_dump(),
    )
    assert res.status_code == 200
    return res.json()


@pytest.mark.asyncio
@init_memory_sqlite()
async def test_get_user(client: TestClient, user: CustIn, city: CityIn):
    setup_city(client, city)
    setup_user(client, user)

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
