from datetime import datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient

from internal.db.models import Cities, Customers, Subscriptions
from internal.db.schemas import CityIn, CustIn, SubIn
from tests.fixtures import (
    admin_auth,
    city,
    client,
    user,
)
from tests.fixtures.subs import (
    setup_sub,
    test_sub_1d,
    test_sub_3d,
    test_sub_all,
)
from tests.test_utils import init_memory_sqlite


def check_expired_subs(client: TestClient, count: int):
    res = client.post("/api/v1/force-expire-subscriptions", auth=admin_auth)
    assert res.status_code == 200
    assert res.json() == {"rows": count, "message": "ok"}


@pytest.mark.asyncio
@init_memory_sqlite()
async def test_expire_subscriptions_job_empty(client: TestClient):
    check_expired_subs(client=client, count=0)


@pytest.mark.asyncio
@init_memory_sqlite()
async def test_expire_subscriptions_job(
    client: TestClient,
    city: CityIn,
    user: CustIn,
    test_sub_1d: SubIn,
):
    sub = await setup_sub(city, user, test_sub_1d)
    sub.created_at = datetime.now() - timedelta(days=10)
    await sub.save()
    check_expired_subs(client=client, count=1)


@pytest.mark.asyncio
@init_memory_sqlite()
async def test_expire_subscriptions_job_unchanged(
    client: TestClient,
    city: CityIn,
    user: CustIn,
    test_sub_3d: SubIn,
):
    sub = await setup_sub(city, user, test_sub_3d)
    sub.created_at = datetime.now(timezone.utc) - timedelta(
        days=2,
        hours=23,
        minutes=59,
        seconds=59,
    )
    await sub.save()
    check_expired_subs(client=client, count=0)


@pytest.mark.asyncio
@init_memory_sqlite()
async def test_expire_subscriptions_job_all(
    client: TestClient,
    city: CityIn,
    user: CustIn,
    test_sub_all: SubIn,
):
    sub = await setup_sub(city, user, test_sub_all)
    sub.created_at = datetime.now(timezone.utc) - timedelta(
        days=test_sub_all.sub_type  # type: ignore[attr-defined]
    )
    await sub.save()
    check_expired_subs(client=client, count=1)
