import asyncio
from datetime import datetime, timezone

import structlog
from firebase_admin import messaging  # type: ignore
from tortoise import Tortoise

from internal import fcm
from internal.db.models import Cities, Customers
from internal.logger import setup_job_contextvars
from internal.nooa import nooa_req
from internal.nooa.calc import NooaAuroraReq, nearst_aurora_probability
from internal.nooa.nooa_req import use_nooa_aurora_client

logger = structlog.stdlib.get_logger(__name__)

ProbDict = dict[int, float]


async def calc_cites_probabilities() -> ProbDict:
    res = nooa_req.NooaAuroraRes.model_validate_json(use_nooa_aurora_client())
    cities = await Cities.all()
    prob_dict = {}
    for city in cities:
        prob_dict[city.id] = nearst_aurora_probability(
            pos=NooaAuroraReq(lat=city.lat, lon=city.long),
            prob_map=res,
        ).probability

    return prob_dict


async def common_fcm_job(prob_dict: ProbDict | None = None):
    setup_job_contextvars("common_fcm")
    if prob_dict is None:
        prob_dict = await calc_cites_probabilities()

    async with asyncio.TaskGroup() as tg:
        tg.create_task(subscription_job_per_user(prob_dict))
        tg.create_task(user_job(prob_dict))


async def subscription_job_per_user(prob_dict: ProbDict):
    """Send push notifications once per user"""
    conn = Tortoise.get_connection("default")
    alerted_users: list[int] = []
    messages: list[messaging.Message] = []
    for city_id, prob in prob_dict.items():
        user_pool = await conn.execute_query_dict(
            """
            select * from customers c
            left join subscriptions s on s.cust_id = c.id
            join cities ci on ci.id = c.city_id
                where s.active = true
                    and c.city_id = ?
            """,
            [city_id],
        )
        for user in user_pool:
            if prob < user["alert_probability"]:
                continue
            locale = user.get("locale", "ru")
            city_name = await fcm.get_city_name(user)
            messages.append(
                fcm.create_message(user["token"], locale, city_name)
            )
            alerted_users.append(user["id"])
    err = fcm.send_messages_to_subs(messages)
    if err is not None:
        logger.exception(f"Failed to send messages: {err}")
        return {"error": err}
    return {
        "rows": len(alerted_users),
        "users": alerted_users,
    }


# NOTE: removed topic implementation
async def subscription_job(prob_dict: ProbDict):
    """Send push notifications by topics
    by city id and probability
    """
    structlog.contextvars.bind_contextvars(job_name="subscription_job")
    messages: list[messaging.Message] = []
    alerted_cities = 0
    for city_id, prob in prob_dict.items():
        # 20 40 60
        if prob < 20:
            continue
        messages.extend(
            fcm.prepare_topic_message(city_id, fcm.get_probability_range(prob)),
        )
        alerted_cities += 1
    err = fcm.send_messages_to_subs(messages)
    if err is not None:
        logger.exception(f"Failed to send messages: {err}")
        return err
    logger.info(
        f"alerted {alerted_cities}"
        f" cities: {({k: v for k, v in prob_dict.items() if v >= 20})}"
    )
    return alerted_cities


async def user_job(prob_dict: ProbDict):
    """Send push notifications once per week"""
    structlog.contextvars.bind_contextvars(job_name="user_job")
    cities_to_send = {k: v for k, v in prob_dict.items() if v >= 50}
    # select all unhobo user with no subscriptions
    conn = Tortoise.get_connection("default")
    # TODO: possible SQL injection rewrite as orm query later
    users_to_send = await conn.execute_query_dict(
        f"""
        select * from customers c
        left join subscriptions s on s.cust_id = c.id
        join cities ci on ci.id = c.city_id
            where c.hobo = false
            and (
                s.active = false
                or s.active is null
            )
            and ci.id in ({','.join([str(i) for i in cities_to_send.keys()])})
        """
    )

    # send push notification to each user
    err = await fcm.send_message_to_users(users_to_send)
    if err is not None:
        logger.exception(f"Failed to send messages: {err}")
        return err

    # and then set hobo to true
    to_hobo = await Customers.filter(
        id__in=[user["id"] for user in users_to_send]
    )
    if not to_hobo:
        return 0
    for c in to_hobo:
        c.hobo = True
        c.hobo_at = datetime.now(timezone.utc)
        logger.info(f"Hobo user {c.id}")

    res = await Customers.bulk_update(to_hobo, ["hobo", "hobo_at"])
    return res
