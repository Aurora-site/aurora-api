import json
from contextlib import asynccontextmanager
from datetime import UTC
from typing import AsyncGenerator

import structlog
from apscheduler.schedulers.asyncio import AsyncIOScheduler  # type: ignore
from fastapi import APIRouter, Depends, FastAPI

from internal.auth import check_credentials
from internal.db.models import Cities
from internal.jobs.expire_subscriptions_job import expire_subscriptions_job
from internal.jobs.send_fcm import (
    ProbDict,
    common_fcm_job,
    subscription_job,
    user_job,
)
from internal.jobs.unhobo import unhobo_job
from internal.nooa import nooa_req
from internal.nooa.calc import NooaAuroraReq, nearst_aurora_probability
from internal.settings import SCHEDULER_ENABLED

log = structlog.stdlib.get_logger(__name__)


def init_jobs(s: AsyncIOScheduler):
    s.configure(timezone=UTC)

    s.add_job(
        unhobo_job,
        trigger="interval",
        # TODO: start_date = 17:00,
        days=1,
        replace_existing=True,
        id="aboba_job",
    )

    s.add_job(
        common_fcm_job,
        trigger="interval",
        hours=1,
        replace_existing=True,
        id="common_fcm_job",
    )

    s.add_job(
        expire_subscriptions_job,
        trigger="interval",
        hours=1,
        replace_existing=True,
        id="expire_subscriptions_job",
    )


@asynccontextmanager
async def scheduler_lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    if SCHEDULER_ENABLED:
        app.state.scheduler = AsyncIOScheduler()
        init_jobs(app.state.scheduler)
        try:
            app.state.scheduler.start()
            yield
        finally:
            app.state.scheduler.shutdown()
    else:
        log.info("Scheduler is disabled")
        yield


router = APIRouter(
    prefix="/api/v1",
    tags=["Jobs"],
    dependencies=[Depends(check_credentials)],
)


@router.post("/force-hobo")
async def force_hobo():
    """Запускает задачу по восстановлению израсходованных бесплатных пушей
    для пользователей
    """
    num = await unhobo_job()
    return {"message": "ok", "rows": num}


@router.post("/force-send-subscription")
async def force_subscription(prob_dict: ProbDict | None = None):
    """Отправляет push уведомления по топикам на всех подписчиков
    принимает словарь для переопределения вероятности по каждому городу
    где ключ - id города (city_id)
    значение - вероятность сияния в данном городе (в процентах)
    """
    if prob_dict is None:
        prob_dict = {}
    num = await subscription_job(prob_dict)
    return {"message": "ok", "rows": num}


@router.post("/force-user-job")
async def force_user_job(prob_dict: ProbDict | None = None):
    """Отправляет push уведомления для бесплатных пользователей (hobo)
    принимает словарь для переопределения вероятности по каждому городу
    где ключ - id города (city_id)
    значение - вероятность сияния в данном городе (в процентах)
    """
    if prob_dict is None:
        prob_dict = {}
        res = nooa_req.NooaAuroraRes.model_validate(
            json.loads(nooa_req.use_nooa_aurora_client())
        )
        cities = await Cities.all()
        for city in cities:
            prob_dict[city.id] = nearst_aurora_probability(
                pos=NooaAuroraReq(lat=city.lat, lon=city.long),
                prob_map=res,
            ).probability
    num = await user_job(prob_dict)
    return {"message": "ok", "rows": num}


@router.post("/force-expire-subscriptions")
async def force_expire_subscriptions():
    """Запускает задачу по удалению подписок которые уже не активны
    в базе данных
    """
    num = await expire_subscriptions_job()
    return {"message": "ok", "rows": num}
