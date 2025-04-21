import json
from typing import Literal, TypeAlias

import structlog
from firebase_admin import (  # type: ignore
    App,
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


default_app: App | None = None


# TODO: call later when app is created but not in tests runtime
def init_app():
    global default_app
    if default_app is not None:
        return default_app
    default_app = initialize_app(
        options={"projectId": "polar-lights-235b0"},
        credential=credentials.Certificate(get_cert()),
    )
    return default_app


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


ProbabilityRange: TypeAlias = Literal[20, 40, 60]


def get_probability_range(probability: int | float) -> ProbabilityRange:
    if probability < 20:
        raise ValueError("Probability must be greater than 20")
    if probability < 40:
        return 20
    if probability < 60:
        return 40
    return 60


def send_topic_message(city_id: int, probability: ProbabilityRange) -> None:
    init_app()
    messages = []
    for locale in ["ru", "cn"]:
        topic = f"aurora-api-{city_id}-{locale}-{probability}"
        messages.append(
            messaging.Message(
                notification=messaging.Notification(
                    title=f"Hello, world! {locale=} {city_id=} {probability=}",
                    body="This is a topic test notification",
                    image="https://test-aurora-api.akorz.duckdns.org/media/aboba.png",
                ),
                topic=topic,
            )
        )
    response: messaging.BatchResponse = messaging.send_all(
        messages,
        dry_run=FCM_DRY_RUN,
    )
    logger.info(
        f"Sent {len(messages)} messages to {len(response.responses)} users"
    )


def send_message_to_users(users: list[dict]):
    init_app()
    messages = []
    for user in users:
        messages.append(
            messaging.Message(
                notification=messaging.Notification(
                    title=f"Hello, world! {user['locale']} {user['city_id']}",
                    body="This is a topic test notification",
                    image="https://test-aurora-api.akorz.duckdns.org/media/aboba.png",
                ),
            )
        )
    response: messaging.BatchResponse = messaging.send_all(
        messages,
        dry_run=FCM_DRY_RUN,
    )
    logger.info(
        f"Sent {len(messages)} messages to {len(response.responses)} users"
    )
