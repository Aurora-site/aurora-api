from internal.fcm import get_probability_range


def test_get_probability_range():
    assert get_probability_range(20) == 20
    assert get_probability_range(33) == 20
    assert get_probability_range(40) == 40
    assert get_probability_range(42) == 40
    assert get_probability_range(60) == 60
    assert get_probability_range(10000) == 60
