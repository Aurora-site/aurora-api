from datetime import datetime, timedelta, timezone

import structlog

from internal.db.models import Subscriptions
from internal.logger import setup_job_contextvars

logger = structlog.stdlib.get_logger(__name__)


async def expire_sub(sub: Subscriptions):
    # fmt: off
    if sub.created_at + timedelta(days=sub.sub_type) \
        < datetime.now(timezone.utc):
        # fmt: on
        sub.active = False
        sub.updated_at = datetime.now(timezone.utc)
        logger.info(
            f"Expire subscription {sub.id} for user {sub.cust_id}"  # type: ignore
            f" Reason: {sub.sub_type} days passed"
        )
        await sub.save()
        return True
    return False


async def expire_subscriptions_job():
    setup_job_contextvars("expire_subscriptions")
    s = await Subscriptions.filter(active=True)
    expired_subs = 0
    if not s:
        return 0
    for sub in s:
        expired_subs += await expire_sub(sub)
    logger.info(f"Expired {expired_subs} subscriptions")
    return expired_subs
