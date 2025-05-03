import pytest

from internal.fcm import get_probability_range, prepare_topic_message


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
