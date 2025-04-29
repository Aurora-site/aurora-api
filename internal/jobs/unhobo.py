from datetime import datetime, timedelta

import structlog

from internal.db.models import Customers
from internal.logger import setup_job_contextvars

logger = structlog.stdlib.get_logger(__name__)


async def unhobo_job():
    setup_job_contextvars("unhobo")
    hobo_customers = await Customers.filter(
        hobo_at__lt=datetime.now() - timedelta(days=7),
        hobo=True,
    )
    logger.info(f"Found customers to unhobo {len(hobo_customers)}")
    if not hobo_customers:
        return 0
    for c in hobo_customers:
        c.hobo = False
        logger.info(f"Unhobo customer {c.id}")

    res = await Customers.bulk_update(hobo_customers, ["hobo"])
    return res
