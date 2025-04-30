from datetime import datetime, timedelta

import pytest
from fastapi.testclient import TestClient

from internal.db.models import Cities, Customers
from internal.db.schemas import CityIn, CustIn
from tests.fixtures import admin_auth, city, client, user
from tests.test_utils import init_memory_sqlite


@pytest.mark.asyncio
@init_memory_sqlite()
async def test_unhobo_empty(client: TestClient):
    res = client.post("/api/v1/force-hobo", auth=admin_auth)
    assert res.status_code == 200
    assert res.json() == {"rows": 0, "message": "ok"}


@pytest.fixture
async def hobo_customers(user: CustIn):
    new_c = user.model_dump()
    new_c_8 = new_c | dict(
        hobo=True,
        hobo_at=datetime.now() - timedelta(days=8),
    )
    new_c_5 = new_c | dict(
        hobo=True,
        hobo_at=datetime.now() - timedelta(days=5),
    )
    return new_c_8, new_c_5


@pytest.mark.asyncio
@init_memory_sqlite()
async def test_unhobo(client: TestClient, city: CityIn, hobo_customers):
    _ = await Cities.create(**city.model_dump())
    for c in hobo_customers:
        await Customers.create(**c)

    res = client.post("/api/v1/force-hobo", auth=admin_auth)
    assert res.status_code == 200
    assert res.json() == {"rows": 1, "message": "ok"}
