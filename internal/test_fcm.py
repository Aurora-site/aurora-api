import pytest
from fastapi.testclient import TestClient

from internal.db.schemas import CityIn, CustIn
from internal.fcm import (
    get_city_name,
    get_probability_range,
    prepare_topic_message,
)
from tests.fixtures import city, client, setup_city, setup_user, user, user_auth
from tests.test_utils import init_memory_sqlite


@pytest.mark.parametrize(
    "prob, expected",
    [
        (20, 20),
        (33, 20),
        (40, 40),
        (42, 40),
        (60, 60),
        (99, 60),
        (10000, 60),
    ],
)
def test_get_probability_range(prob, expected):
    assert get_probability_range(prob) == expected


@pytest.mark.parametrize(
    "probability, expected_probs",
    [
        (20, [20]),
        (40, [20, 40]),
        (60, [20, 40, 60]),
    ],
)
def test_prepare_topic_message(probability, expected_probs):
    city_id = 1
    m = prepare_topic_message(city_id, probability)
    topics = [i.topic for i in m]

    for _prob in expected_probs:
        assert f"dev-aurora-api-{city_id}-ru-{_prob}" in topics
        assert f"dev-aurora-api-{city_id}-cn-{_prob}" in topics


@pytest.mark.asyncio
@init_memory_sqlite()
async def test_get_city_name(client: TestClient, user: CustIn, city: CityIn):
    city.name_ru = "test city"  # type: ignore
    setup_user(client, user, city)
    n = await get_city_name(user.model_dump())
    assert n == city.name_ru  # type: ignore


@pytest.mark.asyncio
@init_memory_sqlite()
async def test_get_city_name_none(
    client: TestClient, user: CustIn, city: CityIn
):
    setup_user(client, user, city)
    u = user.model_dump()
    u["city_id"] = 2
    n = await get_city_name(u)
    assert n is None
