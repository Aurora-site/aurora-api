from datetime import datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient

from internal.db.models import Cities, Customers, Subscriptions
from internal.db.schemas import CityIn, CustIn, SubIn
from tests.fixtures import test_city, test_customer, test_sub
from tests.test_utils import admin_auth, client, init_memory_sqlite


@pytest.mark.asyncio
@init_memory_sqlite()
async def test_expire_subscriptions_job_empty(client: TestClient):
    res = client.post("/api/v1/force-expire-subscriptions", auth=admin_auth)
    assert res.status_code == 200
    assert res.json() == {"rows": 0, "message": "ok"}


@pytest.fixture
def test_sub2():
    return SubIn(
        cust_id=1,
        alert_probability=20,
        sub_type=3,
        geo_push_type="CURRENT",
        active=True,
    )


@pytest.mark.asyncio
@init_memory_sqlite()
async def test_expire_subscriptions_job(
    client: TestClient,
    test_city: CityIn,
    test_customer: CustIn,
    test_sub: SubIn,
):
    _ = await Cities.create(**test_city.model_dump())
    _ = await Customers.create(**test_customer.model_dump())
    _ = await Subscriptions.create(**test_sub.model_dump())
    sub1 = await Subscriptions.create(**test_sub.model_dump())
    sub1.created_at = datetime.now() - timedelta(days=10)
    await sub1.save()
    res = client.post("/api/v1/force-expire-subscriptions", auth=admin_auth)
    assert res.status_code == 200
    assert res.json() == {"rows": 1, "message": "ok"}


@pytest.mark.asyncio
@init_memory_sqlite()
async def test_expire_subscriptions_job_unchanged(
    client: TestClient,
    test_city: CityIn,
    test_customer: CustIn,
    test_sub2: SubIn,
):
    _ = await Cities.create(**test_city.model_dump())
    _ = await Customers.create(**test_customer.model_dump())
    _ = await Subscriptions.create(**test_sub2.model_dump())
    sub = await Subscriptions.create(**test_sub2.model_dump())
    sub.created_at = datetime.now(timezone.utc) - timedelta(
        days=2,
        hours=23,
        minutes=59,
        seconds=59,
    )
    await sub.save()
    res = client.post("/api/v1/force-expire-subscriptions", auth=admin_auth)
    assert res.status_code == 200
    assert res.json() == {"rows": 0, "message": "ok"}
