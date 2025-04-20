import json

import structlog

from internal import fcm
from internal.db.models import Cities
from internal.nooa import nooa_req
from internal.nooa.calc import NooaAuroraReq, nearst_aurora_probability
from internal.nooa.nooa_req import use_nooa_aurora_client

logger = structlog.stdlib.get_logger(__name__)


async def subscription_job():
    """Send push notifications by topics
    by city id and probability
    """
    res = nooa_req.NooaAuroraRes.model_validate(
        json.loads(use_nooa_aurora_client())
    )
    cities = await Cities.all()
    prob_dict = {}
    for city in cities:
        prob_dict[city.id] = nearst_aurora_probability(
            pos=NooaAuroraReq(lat=city.lat, lon=city.long),
            prob_map=res,
        ).probability

    alerted_cities = 0
    for city_id, prob in prob_dict.items():
        # 20 40 60
        if prob < 20:
            continue
        fcm.send_topic_message(city_id, prob)
        alerted_cities += 1

    logger.info(f"alerted {alerted_cities} cities")
    return alerted_cities


async def user_job():
    """Send push notifications once per week"""
    pass
