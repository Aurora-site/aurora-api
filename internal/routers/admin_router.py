from pathlib import Path

import structlog
from fastapi import APIRouter, Depends, HTTPException, Request, UploadFile

from internal.auth import check_credentials
from internal.db.models import Cities, Customers, Tours
from internal.db.schemas import City, CityIn, Cust, Message, Tour, TourIn
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
