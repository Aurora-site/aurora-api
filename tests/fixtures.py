import pytest

from internal.db.schemas import CityIn, CustIn, SubIn


@pytest.fixture
def test_city():
    return CityIn(name="test city", lat=10, long=10)


@pytest.fixture
def test_customer():
    return CustIn(
        selected_geo_lat=1,
        selected_geo_long=2,
        token="token",
        city_id=1,
    )


@pytest.fixture
def test_sub():
    return SubIn(
        cust_id=1,
        alert_probability=20,
        sub_type=1,
        geo_push_type="CURRENT",
        active=True,
    )
