import json

import structlog
from firebase_admin import (  # type: ignore
    credentials,
    initialize_app,
    messaging,
)

from internal.db.models import Customers, Subscriptions
from internal.settings import FCM_CERT, FCM_DRY_RUN

logger = structlog.stdlib.get_logger(__name__)


def get_cert() -> dict:
    try:
        s = json.loads(FCM_CERT)
    except json.JSONDecodeError as e:
        logger.error("Invalid FCM_CERT")
        raise e

    return s


default_app = initialize_app(
    options={"projectId": "polar-lights-235b0"},
    credential=credentials.Certificate(get_cert()),
)


def subscribe_to_user_topic(user: Customers) -> Exception | None:
    topic = f"aurora-api-{user.city_id}-{user.locale}"  # type: ignore
    logger.info(
        f"Subscribing user {user.id} to topic {topic}",
        user=user.id,
    )
    if FCM_DRY_RUN:
        return None
    res = messaging.subscribe_to_topic([user.token], topic)
    if res.success_count == 0:
        return Exception(
            f"Failed to subscribe user to topic: {res.errors[0].reason}"
        )
    return None


def subscribe_to_topic(
    token: str,
    user: Customers,
    sub: Subscriptions,
) -> Exception | None:
    topic = f"aurora-api-{user.city_id}-{user.locale}-{sub.alert_probability}"  # type: ignore
    logger.info(
        f"Subscribing user {user.id} to topic {topic} sub id: {sub.id}",
        user=user.id,
        sub=sub.id,
        topic=topic,
    )
    if FCM_DRY_RUN:
        return None
    res = messaging.subscribe_to_topic([token], topic)

    if res.success_count == 0:
        return Exception("Failed to subscribe user to topic")

    return None


def send_topic_message(city_id: int, probability: int):
    messages = []
    for locale in ["ru", "cn"]:
        topic = f"aurora-api-{city_id}-{locale}-{probability}"
        messages.append(
            messaging.Message(
                notification=messaging.Notification(
                    title="Hello, world!",
                    body="This is a topic test notification",
                    image="https://test-aurora-api.akorz.duckdns.org/media/aboba.png",
                ),
                topic=topic,
            )
        )
    response = messaging.send_all(messages, dry_run=FCM_DRY_RUN)
    logger.info(
        f"Sent {len(messages)} messages to {len(response.responses)} users"
    )
