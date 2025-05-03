from contextlib import asynccontextmanager
from typing import AsyncGenerator, Literal, TypeAlias

import structlog
from fastapi import FastAPI
from firebase_admin import (  # type: ignore
    App,
    credentials,
    initialize_app,
    messaging,
)

from internal.db.models import Customers, Subscriptions
from internal.settings import (
    ENV_NAME,
    FCM_DRY_RUN,
    FCM_PROJECT_ID,
    FCM_SETTINGS,
)


class FcmException(Exception):
    pass


logger = structlog.stdlib.get_logger(__name__)


default_app: App | None = None


def init_app(dry_run: bool = FCM_DRY_RUN) -> App:
    global default_app
    if dry_run:
        return None
    if default_app is not None:
        return default_app
    default_app = initialize_app(
        options=dict(projectId=FCM_PROJECT_ID),
        credential=credentials.Certificate(FCM_SETTINGS),
    )
    return default_app


@asynccontextmanager
async def fcm_lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    logger.info(f"Starting FCM with dry run: {FCM_DRY_RUN}")
    app.state.fcm = init_app(FCM_DRY_RUN)
    yield


def subscribe_to_topic(token: str, topic: str) -> Exception | None:
    # TODO: move logger here
    if FCM_DRY_RUN:
        return None
    res: messaging.TopicManagementResponse = messaging.subscribe_to_topic(
        [token],
        topic,
    )
    if res.success_count == 0:
        return Exception(f"Failed to subscribe user to topic: {res.errors}")
    return None


def unsubscribe_from_topic(token: str, topic: str) -> Exception | None:
    if FCM_DRY_RUN:
        return None
    res: messaging.TopicManagementResponse = messaging.unsubscribe_from_topic(
        [token],
        topic,
    )
    if res.success_count == 0:
        return Exception(f"Failed to unsubscribe user from topic: {res.errors}")
    return None


def get_free_topic(city_id: int, locale: str) -> str:
    return f"{ENV_NAME}-aurora-api-{city_id}-{locale}"


def subscribe_to_user_topic(user: Customers) -> Exception | None:
    topic = get_free_topic(user.city_id, user.locale)  # type: ignore
    logger.info(
        f"Subscribing user {user.id} to topic {topic}",
        user=user.id,
    )
    return subscribe_to_topic(user.token, topic)


def get_piad_topic(
    city_id: int,
    locale: str,
    probability: "ProbabilityRange",
) -> str:
    return f"{ENV_NAME}-aurora-api-{city_id}-{locale}-{probability}"


def subscribe_to_piad_topic(
    user: Customers,
    sub: Subscriptions,
) -> Exception | None:
    topic = get_piad_topic(
        user.city_id,  # type: ignore
        user.locale,
        get_probability_range(sub.alert_probability),
    )
    logger.info(
        f"Subscribing user {user.id} to topic {topic} sub id: {sub.id}",
        user=user.id,
        sub=sub.id,
        topic=topic,
    )
    return subscribe_to_topic(user.token, topic)


ProbabilityRange: TypeAlias = Literal[20, 40, 60]


def get_probability_range(probability: int | float) -> ProbabilityRange:
    if probability < 20:
        raise ValueError("Probability must be greater than 20")
    if probability < 40:
        return 20
    if probability < 60:
        return 40
    return 60


def log_fcm_send_result(response: messaging.BatchResponse):
    logger.info(
        f"Sent {len(response.responses)} messages to users "
        f"success: {response.success_count} errors: {response.failure_count}",
        fcm_send_success=response.success_count,
        fcm_send_error=response.failure_count,
    )
    m = [
        f"success={resp.success},msg_id={resp.message_id}  "
        for resp in response.responses
    ]
    logger.debug(f"Message ids: {m}")


def send_messages(messages: list[messaging.Message]) -> FcmException | None:
    try:
        # send_all is not working (returns 404 error)
        response: messaging.BatchResponse = messaging.send_each(
            messages,
            dry_run=FCM_DRY_RUN,
        )
    except Exception as e:
        logger.exception(f"Failed to send messages: {e}")
        return FcmException(f"Failed to send messages: {e}")
    log_fcm_send_result(response)
    return None


def get_localized_notification(locale: str) -> messaging.Notification | None:
    localized_texts = {
        "ru": {
            "title": "Северное сияние в ближайший час! Пора на охоту!",
            "body": "Проверяйте облачность и отправляйтесь за северным сиянем! "
            "Сейчас самое время!",
        },
        "cn": {
            "title": "极光将在一小时内出现！",
            "body": "确认无云，出发去追极光吧！现在正是最佳时机",
        },
    }
    return messaging.Notification(**localized_texts[locale])


def prepare_topic_message(
    city_id: int,
    probability: ProbabilityRange,
) -> list[messaging.Message]:
    messages: list[messaging.Message] = []
    locales = ["ru", "cn"]

    for locale in locales:
        topic = get_piad_topic(city_id, locale, probability)
        messages.append(
            messaging.Message(
                notification=get_localized_notification(locale),
                topic=topic,
            )
        )
    return messages


def send_messages_to_subs(
    messages: list[messaging.Message],
) -> FcmException | None:
    if FCM_DRY_RUN:
        logger.info(f"DRY RUN: Sent {len(messages)} messages to subs")
        return None
    return send_messages(messages)


def send_message_to_users(users: list[dict]) -> FcmException | None:
    messages: list[messaging.Message] = []
    for user in users:
        locale = user.get("locale", "ru")
        message = messaging.Message(
            notification=get_localized_notification(locale),
            token=user["token"],
        )
        messages.append(message)
    if FCM_DRY_RUN:
        logger.info(
            f"DRY RUN: Sent {len(messages)} messages "
            f"to users: {[u['id'] for u in users]}"
        )
        return None
    return send_messages(messages)
