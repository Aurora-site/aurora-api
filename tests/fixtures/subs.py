import pytest

from internal.db.schemas import SubIn


@pytest.fixture
def test_sub_1d():
    return SubIn(
        cust_id=1,
        alert_probability=20,
        sub_type=1,
        geo_push_type="CURRENT",
        active=True,
    )


@pytest.fixture
def test_sub_3d():
    return SubIn(
        cust_id=1,
        alert_probability=20,
        sub_type=3,
        geo_push_type="CURRENT",
        active=True,
    )


@pytest.fixture(params=[1, 7, 30])
def test_sub_all(request: pytest.FixtureRequest):
    return SubIn(
        cust_id=1,
        alert_probability=20,
        sub_type=request.param,
        geo_push_type="CURRENT",
        active=True,
    )
