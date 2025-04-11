from pathlib import Path

import structlog
from fastapi import APIRouter, Depends, HTTPException, Request, UploadFile

from internal.auth import check_credentials
from internal.db.models import Banners, Cities, Customers, Tours
from internal.db.schemas import (
    BannerIn,
    City,
    CityIn,
    CityUpdate,
    Cust,
    Message,
    Tour,
    TourIn,
)
from internal.nooa import nooa_req, swpc_req
from internal.settings import MEDIA_FOLDER

logger = structlog.stdlib.get_logger(__name__)
router = APIRouter(
    prefix="/api/v1",
    tags=["Admin"],
    dependencies=[Depends(check_credentials)],
)


@router.get("/all-customers", response_model=list[Cust])
async def all_customers():
    """Получение списка всех пользователей"""
    ac = await Customers.all()
    return ac


@router.post("/set-cities", response_model=list[City])
async def set_cities(cities: list[CityIn]):
    """Перезапись списка городов"""
    res = await Cities.all().delete()
    logger.info(f"Deleted cities: {res} ", count=res)
    cs = []
    for c in cities:
        nc = await Cities.create(**c.model_dump())
        cs.append(nc)
    return cs


@router.post("/new-city", response_model=City)
async def new_city(city: CityIn):
    """Добавление города"""
    c = await Cities.create(**city.model_dump())
    return c


@router.delete("/city/{city_id}", response_model=Message)
async def drop_city(city_id: int):
    """Удаление города"""
    c = await Cities.get_or_none(id=city_id)
    if c is None:
        raise HTTPException(status_code=404, detail="City not found")
    await c.delete()
    return Message(detail="ok")


@router.put("/city/{city_id}", response_model=City)
async def update_city(city_id: int, city: CityUpdate):
    """Обновление города"""
    c = await Cities.get_or_none(id=city_id)
    if c is None:
        raise HTTPException(status_code=404, detail="City not found")
    upd_c = await c.update_from_dict(
        {k: v for k, v in city.model_dump().items() if v is not None}
    )
    await upd_c.save()
    return upd_c


@router.delete("/drop-cache")
async def drop_cache():
    """Очистка кэша запросов в NOOA"""
    swpc_req.storage._cache.cache = {}
    nooa_req.storage._cache.cache = {}
    nooa_req.long_storage._cache.cache = {}
    return {"message": "ok"}


@router.post("/tour", response_model=Tour)
async def set_tour(tour: TourIn):
    """Добавление тура"""
    t = await Tours.create(**tour.model_dump())
    return t


@router.delete(
    "/tour/{tour_id}",
    responses={
        200: {"model": Message},
        404: {"model": Message},
    },
)
async def drop_tour(tour_id: int):
    """Удаление тура"""
    t = await Tours.get_or_none(id=tour_id)
    if t is None:
        raise HTTPException(status_code=404, detail="Tour not found")
    await t.delete()
    return Message(detail="ok")


@router.post("/create-object", responses={409: {"model": Message}})
async def create_object(
    req: Request,
    file: UploadFile,
    name: str | None = None,
) -> str:
    """Сохранение медиафайла в папку media"""
    if file.filename is None:
        if name is not None:
            file.filename = name
        else:
            raise HTTPException(status_code=400, detail="Filename is required")
    obj = Path(MEDIA_FOLDER) / (name or file.filename)

    if obj.exists():
        raise HTTPException(
            status_code=409, detail=f"File {name} already exists"
        )
    obj.write_bytes(await file.read())
    return f"{req.base_url}{obj.as_posix()}"


@router.post("/set-banner", response_model=BannerIn)
async def set_banner(banner: BannerIn):
    """Перезапись баннера"""
    banner_data = banner.model_dump()
    if banner.default:
        b = await Banners.get_or_none(default=True, locale=banner.locale)
        if b is None:
            b = await Banners.create(**banner.model_dump())
            return b
        await b.update_from_dict(banner.model_dump())
        await b.save()
        return b

    elif banner.city_id is not None and banner.locale is not None:
        b = await Banners.get_or_none(
            city_id=banner.city_id, locale=banner.locale, default=False
        )
    elif banner.city_id is not None:
        b = await Banners.get_or_none(
            city_id=banner.city_id, locale__isnull=True, default=False
        )
    elif banner.locale is not None:
        b = await Banners.get_or_none(
            locale=banner.locale, city_id__isnull=True, default=False
        )
    else:
        raise HTTPException(status_code=400, detail="Unknown banner type")

    if b is None:
        return await Banners.create(**banner_data)

    await b.update_from_dict(banner_data)
    await b.save()
    return b


@router.delete(
    "/banner/{banner_id}",
    responses={
        200: {"model": Message},
        404: {"model": Message},
    },
)
async def banner(banner_id: int):
    """Удаление баннера"""
    t = await Banners.get_or_none(id=banner_id)
    if t is None:
        raise HTTPException(status_code=404, detail="Banner not found")
    await t.delete()
    return Message(detail="ok")
