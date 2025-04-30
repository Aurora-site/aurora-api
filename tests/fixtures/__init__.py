import httpx
import pytest
from fastapi.testclient import TestClient

from internal.db.schemas import CityIn, CustIn
from internal.settings import ADMIN_TEST_PASS, ADMIN_USER
from main import app

user_auth = httpx.BasicAuth(username="1", password="test")
admin_auth = httpx.BasicAuth(username=ADMIN_USER, password=ADMIN_TEST_PASS)


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def city():
    return CityIn(name="test city", lat=10, long=10)


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


@pytest.fixture
def user():
    return CustIn(
        city_id=1,
        locale="ru",
        token="test",
    )


def setup_user(client: TestClient, user: CustIn, city: CityIn):
    setup_city(client, city)
    res = client.post(
        "/api/v1/new-user",
        json=user.model_dump(),
    )
    assert res.status_code == 200
    return res.json()
