from typing import TYPE_CHECKING

from pydantic import BaseModel, EmailStr, Field
from tortoise.contrib.pydantic import (
    pydantic_model_creator,
)

from internal.db.models import Cities, Customers, Subscriptions, Tours
from internal.validators import GeoFloat


class Message(BaseModel):
    detail: str


if TYPE_CHECKING:

    class Customer_Pydantic(BaseModel):
        pass

else:
    Customer_Pydantic = pydantic_model_creator(
        Customers,
        name="Customers",
    )


class Cust(Customer_Pydantic):
    pass


if TYPE_CHECKING:

    class CustomerIn_Pydantic(BaseModel):
        pass

else:
    CustomerIn_Pydantic = pydantic_model_creator(
        Customers,
        name="CustomersIn",
        exclude_readonly=True,
    )


class CustIn(CustomerIn_Pydantic):
    current_geo_lat: float | None = Field(le=90, ge=-90, default=None)
    current_geo_long: float | None = Field(le=180, ge=-180, default=None)
    selected_geo_lat: float | None = Field(le=90, ge=-90, default=None)
    selected_geo_long: float | None = Field(le=180, ge=-180, default=None)
    locale: str = Field(max_length=2, default="ru")
    token: str = Field(max_length=255)
    city_id: int = Field(gt=0)


if TYPE_CHECKING:

    class Subscription_Pydantic(BaseModel):
        pass

else:
    Subscription_Pydantic = pydantic_model_creator(
        Subscriptions,
        name="Subscriptions",
    )


class Sub(Subscription_Pydantic):
    pass


if TYPE_CHECKING:

    class SubscriptionIn_Pydantic(BaseModel):
        pass

else:
    SubscriptionIn_Pydantic = pydantic_model_creator(
        Subscriptions,
        name="SubscriptionsIn",
        exclude_readonly=True,
    )


class SubIn(SubscriptionIn_Pydantic):
    cust_id: int = Field(gt=0)
    email: EmailStr = Field(max_length=255)


if TYPE_CHECKING:

    class City_Pydantic(BaseModel):
        pass

else:
    City_Pydantic = pydantic_model_creator(
        Cities,
        name="Cities",
    )


class City(City_Pydantic):
    pass


if TYPE_CHECKING:

    class CityIn_Pydantic(BaseModel):
        pass

else:
    CityIn_Pydantic = pydantic_model_creator(
        Cities,
        name="CitiesIn",
        exclude_readonly=True,
    )


class CityIn(CityIn_Pydantic):
    name: str = Field(max_length=255)
    lat: GeoFloat = Field(le=90, ge=-90)
    long: GeoFloat = Field(le=180, ge=-180)


if TYPE_CHECKING:

    class Tour_Pydantic(BaseModel):
        pass

else:
    Tour_Pydantic = pydantic_model_creator(
        Tours,
        name="Tours",
    )


class Tour(Tour_Pydantic):
    pass


if TYPE_CHECKING:

    class TourIn_Pydantic(BaseModel):
        pass

else:
    TourIn_Pydantic = pydantic_model_creator(
        Tours,
        name="ToursIn",
        exclude_readonly=True,
    )


class TourIn(TourIn_Pydantic):
    pass
