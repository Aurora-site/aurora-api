import pytest

from internal.fcm import get_probability_range


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
