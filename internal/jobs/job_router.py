from contextlib import asynccontextmanager
from datetime import UTC
from typing import AsyncGenerator

import structlog
from apscheduler.schedulers.asyncio import AsyncIOScheduler  # type: ignore
from fastapi import APIRouter, Depends, FastAPI

from internal.auth import check_credentials
from internal.jobs.unhobo import unhobo_job
from internal.settings import SCHEDULER_ENABLED

log = structlog.stdlib.get_logger(__name__)


def init_jobs(s: AsyncIOScheduler):
    s.configure(timezone=UTC)

    s.add_job(
        unhobo_job,
        trigger="interval",
        # start_date = 17:00,
        days=1,
        replace_existing=True,
        id="aboba_job",
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
    num = await unhobo_job()
    return {"message": "ok", "rows": num}
