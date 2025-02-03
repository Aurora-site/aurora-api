import uuid
from typing import Annotated

from fastapi import APIRouter, Body, HTTPException
from pydantic import BaseModel

from internal.db.models import Customers, Subscriptions
from internal.db.schemas import Cust, CustIn, Message, Sub, SubIn

router = APIRouter(
    prefix="/api/v1",
    tags=["User"],
    responses={
        409: {"model": Message},
    },
)

NewUserBody = Annotated[
    CustIn,
    Body(
        openapi_examples={
            "Ex User 1": {
                "value": {
                    "city_id": 1,
                    "locale": "ru",
                    "token": "test",
                }
            },
            "Ex User 2": {
                "value": {
                    "current_geo_lat": 40.3,
                    "current_geo_long": 40.4,
                    "city_id": 1,
                    "locale": "ch",
                    "token": "test",
                },
            },
        }
    ),
]


@router.post("/new-user", response_model=Cust)
async def new_user(cust: NewUserBody):
    """Создание нового пользователя"""
    c = await Customers.create(**cust.model_dump())
    return c


class GetUserResponse(BaseModel):
    cust: Cust
    subs: list[Sub]


@router.get(
    "/user/{id}",
    response_model=GetUserResponse,
    responses={
        404: {"model": Message},
    },
)
async def get_user(id: int):
    """Получение пользователя и его подписок по id"""
    c = await Customers.get_or_none(id=id)
    if c is None:
        raise HTTPException(status_code=404, detail="Customer not found")
    ss = await Subscriptions.filter(cust_id=c.id).all()
    return GetUserResponse(cust=c, subs=[Sub.model_validate(s) for s in ss])


NewSubBody = Annotated[
    SubIn,
    Body(
        openapi_examples={
            "Ex Sub 1": {
                "value": {
                    "cust_id": 1,
                    "email": "test@test.com",
                    "cust_name": "test",
                    "alert_probability": 50,
                    "sub_type": 1,
                    "geo_push_type": "CURRENT",
                }
            },
            "Ex Sub 2": {
                "value": {
                    "cust_id": 1,
                    "email": "test@test.com",
                    "cust_name": "test",
                    "cust_surname": "test",
                    "cust_patronymic": "test",
                    "cust_fullname": "test test test",
                    "alert_probability": 0.5,
                    "sub_type": 1,
                    "geo_push_type": "SELECTED",
                    "active": True,
                }
            },
        }
    ),
]


class CustSubResponse(BaseModel):
    sub: Sub
    cust: Cust


@router.post(
    "/new-subscription",
    response_model=CustSubResponse,
    responses={
        404: {"model": Message},
    },
)
async def new_subscription(sub: NewSubBody):
    """Создание новой подписки для существующего пользователя"""
    c = await Customers.get_or_none(id=sub.cust_id)
    if c is None:
        raise HTTPException(status_code=404, detail="Customer not found")
    s = await Subscriptions.create(**sub.model_dump())
    return CustSubResponse(sub=s, cust=c)


@router.get(
    "/subscription/{id}",
    response_model=Sub,
    responses={
        404: {"model": Message},
    },
)
async def get_subscription(id: uuid.UUID):
    """Получение подписки по id"""
    s = await Subscriptions.get_or_none(id=id)
    if s is None:
        raise HTTPException(status_code=404, detail="Subscription not found")
    return s
