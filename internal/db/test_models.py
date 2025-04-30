import pytest

from internal.db.models import Cities, Customers
from internal.db.schemas import CityIn, CustIn
from tests.fixtures import city, user
from tests.test_utils import init_memory_sqlite


@pytest.mark.asyncio
@init_memory_sqlite()
async def test_db_create_city(city: CityIn):
    ct = await Cities.create(**city.model_dump())
    assert ct.name == city.name
    assert ct.lat == city.lat
    assert ct.long == city.long


@pytest.mark.asyncio
@init_memory_sqlite()
async def test_db_create_cust(city: CityIn, user: CustIn):
    ct = await Cities.create(**city.model_dump())
    c = await Customers.create(**user.model_dump())
    assert c.locale == user.locale
    assert c.token == user.token
    assert c.city_id == ct.id  # type: ignore
