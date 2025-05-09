import asyncio
import random
from datetime import datetime, timedelta, timezone
from typing import cast

import pytest
from apscheduler.job import Job  # type: ignore
from fastapi import FastAPI
from fastapi.testclient import TestClient
from freezegun.api import FrozenDateTimeFactory

from internal.db.schemas import CityIn, CustIn, SubIn
from internal.jobs.job_router import init_jobs, scheduler_lifespan
from internal.jobs.test_expire_subscriptions_job import setup_sub, test_sub_3d
from tests.fixtures import admin_auth, city, client, setup_user, user
from tests.test_utils import init_memory_sqlite


async def setup_alert_subs(city, user, test_sub_3d):
    s1 = await setup_sub(city, user, test_sub_3d)
    sub2 = test_sub_3d.model_copy(
        update={"cust_id": 2, "alert_probability": 40}
    )
    s2 = await setup_sub(city, user, sub2)
    sub3 = test_sub_3d.model_copy(
        update={"cust_id": 3, "alert_probability": 60}
    )
    s3 = await setup_sub(city, user, sub3)
    return s1, s2, s3


@pytest.mark.parametrize(
    "prob_dict, rows",
    [
        ({1: 20, 2: 40, 3: 60}, 1),
        ({"1": 21, "2": 40, "3": 60}, 1),
        ({"1": "39", "2": "40", "3": "60"}, 1),
    ],
)
@pytest.mark.asyncio
@init_memory_sqlite()
async def test_prob_dict(
    client: TestClient,
    prob_dict,
    rows,
    city: CityIn,
    user: CustIn,
    test_sub_3d: SubIn,
):
    await setup_alert_subs(city, user, test_sub_3d)
    res = client.post(
        "/api/v1/force-send-subscription",
        auth=admin_auth,
        json=prob_dict,
    )
    assert res.status_code == 200
    assert res.json() == {
        "message": "ok",
        "rows": rows,
        "users": list(range(1, rows + 1)),
    }


@pytest.mark.asyncio
@init_memory_sqlite()
async def test_force_send_subscription(
    client: TestClient,
    city: CityIn,
    user: CustIn,
    test_sub_3d: SubIn,
):
    await setup_alert_subs(city, user, test_sub_3d)
    res = client.post(
        "/api/v1/force-send-subscription",
        auth=admin_auth,
        json={user.city_id: 45},
    )
    assert res.status_code == 200
    # only alert on 20 and 40
    assert res.json() == {
        "message": "ok",
        "rows": 2,
        "users": [1, 2],
    }


@pytest.mark.asyncio
@init_memory_sqlite()
async def test_force_user_job(
    client: TestClient,
    city: CityIn,
    user: CustIn,
):
    setup_user(client, user, city)
    res = client.post(
        "/api/v1/force-user-job",
        auth=admin_auth,
        json={user.city_id: 80},
    )
    assert res.status_code == 200
    assert res.json() == {"message": "ok", "rows": 1}


@pytest.mark.asyncio
@init_memory_sqlite()
async def test_init_jobs(client: TestClient, freezer: FrozenDateTimeFactory):
    app = cast(FastAPI, client.app)
    dt = datetime(2012, 1, 14, 12, 0, 1, tzinfo=timezone.utc)
    start_dt = dt.replace(hour=dt.hour + 1, minute=0, second=0)
    freezer.move_to(start_dt)
    async with scheduler_lifespan(app) as s:
        common_fcm_job: Job = s.get_job("common_fcm_job")
        interval = start_dt + timedelta(hours=1)
        assert common_fcm_job.next_run_time == interval
        assert len(common_fcm_job._get_run_times(interval)) == 1

        expire_subscriptions_job: Job = s.get_job("expire_subscriptions_job")
        assert expire_subscriptions_job.next_run_time == interval
        assert len(expire_subscriptions_job._get_run_times(interval)) == 1

        unhobo_job: Job = s.get_job("unhobo_job")
        unhobo_interval = start_dt.replace(hour=17)
        assert unhobo_job.next_run_time == unhobo_interval
        assert len(unhobo_job._get_run_times(unhobo_interval)) == 1
