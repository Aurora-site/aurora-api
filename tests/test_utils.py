from functools import wraps

import httpx
import pytest
from fastapi.testclient import TestClient
from tortoise import Tortoise

from internal.db.config import ORM_MODELS
from internal.db.schemas import BannerIn, CityIn, CustIn
from internal.settings import ADMIN_PASS, ADMIN_TEST_PASS, ADMIN_USER
from main import app

MEMORY_SQLITE = "sqlite://:memory:"


@pytest.fixture
def client():
    return TestClient(app)


def init_memory_sqlite(models: list[str] | None = None):
    if models is None:
        models = ORM_MODELS

    def wrapper(func):
        @wraps(func)
        async def runner(*args, **kwargs):
            await Tortoise.init(
                db_url=MEMORY_SQLITE,
                modules={"models": models},
            )
            await Tortoise.generate_schemas()
            try:
                await func(*args, **kwargs)
            finally:
                await Tortoise.close_connections()

        return runner

    return wrapper


admin_auth = httpx.BasicAuth(username=ADMIN_USER, password=ADMIN_TEST_PASS)


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


@pytest.fixture
def city():
    return CityIn(name="test city", lat=10, long=10)
