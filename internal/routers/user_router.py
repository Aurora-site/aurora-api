import secrets
import uuid
from typing import Annotated

from fastapi import APIRouter, Body, Depends, HTTPException
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel

from internal.db.models import Customers, Subscriptions
from internal.db.schemas import Cust, CustIn, CustUpdate, Message, Sub, SubIn

AuthDep = Annotated[HTTPBasicCredentials, Depends(HTTPBasic())]


async def check_user_credentials(credentials: AuthDep) -> Customers:
    c = await Customers.get_or_none(id=credentials.username)
    if c is None:
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    if not secrets.compare_digest(
        credentials.password,
        c.token,
    ):
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return c


UserAuth = Annotated[Customers, Depends(check_user_credentials)]


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


@router.post("/new-user", response_model=Cust, tags=["User"])
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
async def get_user(id: int, c: UserAuth):
    """Получение пользователя и его подписок по id"""
    if c.id != id:
        raise HTTPException(status_code=401, detail="Not allowed")
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
async def new_subscription(sub: NewSubBody, c: UserAuth):
    """Создание новой подписки для существующего пользователя"""
    if c.id != sub.cust_id:
        raise HTTPException(status_code=401, detail="Not allowed")
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


@router.put("/mod-user/{id}", response_model=Cust)
async def mod_user(id: int, upd_cust: CustUpdate, u: UserAuth):
    """Модификация пользователя"""
    if u.id != id:
        raise HTTPException(status_code=401, detail="Not allowed")
    upd_u = await u.update_from_dict(
        {k: v for k, v in upd_cust.model_dump().items() if v is not None}
    )
    await upd_u.save()
    return upd_u
