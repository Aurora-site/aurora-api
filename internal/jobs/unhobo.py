import uuid
from datetime import datetime, timedelta, timezone

import structlog

from internal.db.models import Customers

logger = structlog.stdlib.get_logger(__name__)


async def unhobo_job():
    structlog.contextvars.bind_contextvars(job_id=str(uuid.uuid4()))
    hobo_customers = await Customers.filter(
        hobo_at__lt=datetime.now() - timedelta(days=7),
        hobo=True,
    )
    logger.info(f"Found customers to unhobo {len(hobo_customers)}")
    if not hobo_customers:
        return 0
    for c in hobo_customers:
        c.hobo = False
        c.hobo_at = datetime.now(timezone.utc)
        logger.info(f"Unhobo customer {c.id}")

    res = await Customers.bulk_update(hobo_customers, ["hobo"])
    return res
