import pytest

from internal.db.models import Cities, Customers
from internal.db.schemas import CityIn, CustIn
from tests.test_utils import init_memory_sqlite


@pytest.fixture
def city():
    return CityIn(name="test city", lat=10, long=10)


@pytest.fixture
def customer():
    return CustIn(
        selected_geo_lat=1,
        selected_geo_long=2,
        token="token",
        city_id=1,
    )


@pytest.mark.asyncio
@init_memory_sqlite()
async def test_db_create_city(city: CityIn):
    ct = await Cities.create(**city.model_dump())
    assert ct.name == city.name
    assert ct.lat == city.lat
    assert ct.long == city.long


@pytest.mark.asyncio
@init_memory_sqlite()
async def test_db_create_cust(city: CityIn, customer: CustIn):
    ct = await Cities.create(**city.model_dump())
    c = await Customers.create(**customer.model_dump())
    assert c.selected_geo_lat == customer.selected_geo_lat
    assert c.selected_geo_long == customer.selected_geo_long
    assert c.token == customer.token
    assert c.city_id == ct.id  # type: ignore
