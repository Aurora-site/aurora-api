from typing import TYPE_CHECKING

from pydantic import BaseModel, EmailStr, Field
from tortoise.contrib.pydantic import (
    pydantic_model_creator,
)

from internal.db.models import Banners, Cities, Customers, Subscriptions, Tours
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
    city_id: int | None


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
    city_id: int | None = Field(gt=0, default=None)


class CustUpdate(BaseModel):
    city_id: int | None = Field(gt=0, default=None)
    locale: str | None = Field(max_length=2, default=None)


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
    email: EmailStr | None = Field(max_length=255, default=None)


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


class CityUpdate(BaseModel):
    name: str | None = Field(max_length=255, default=None)
    name_ru: str | None = Field(max_length=255, default=None)
    name_en: str | None = Field(max_length=255, default=None)
    name_cn: str | None = Field(max_length=255, default=None)
    lat: GeoFloat | None = Field(le=90, ge=-90, default=None)
    long: GeoFloat | None = Field(le=180, ge=-180, default=None)


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


if TYPE_CHECKING:

    class Banner_Pydantic(BaseModel):
        pass

else:
    Banner_Pydantic = pydantic_model_creator(
        Banners,
        name="Banners",
    )


class Banner(Banner_Pydantic):
    pass


if TYPE_CHECKING:

    class BannerIn_Pydantic(BaseModel):
        pass

else:
    BannerIn_Pydantic = pydantic_model_creator(
        Banners,
        name="BannersIn",
        exclude_readonly=True,
    )


class BannerIn(BannerIn_Pydantic):
    default: bool = Field(default=False)
    city_id: int | None = Field(gt=0, default=None)
    locale: str | None = Field(max_length=2, default=None)
