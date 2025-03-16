import json

from fastapi import (
    APIRouter,
    HTTPException,
    Response,
)
from pydantic import BaseModel

from internal.db.models import Banners, Cities, Tours
from internal.db.schemas import BannerIn, City, Tour
from internal.nooa import nooa_req, swpc_req
from internal.nooa.calc import (
    AuroraNooaProbabilityResponse,
    AuroraProbabilityBody,
    AuroraProbabilityCalculation,
    NooaAuroraReq,
    UserBody,
    aurora_probability,
    nearst_aurora_probability,
)

router = APIRouter(
    prefix="/api/v1",
    tags=["API"],
)


class SwpcApiData(BaseModel):
    dst: swpc_req.SwpcDstReq
    bz: swpc_req.SwpcBzReq
    kp: swpc_req.SwpcKpReq


class AuroraProbabilityResponse(BaseModel):
    calc_data: AuroraProbabilityCalculation
    user_data: AuroraProbabilityBody
    api_data: SwpcApiData


@router.post(
    "/aurora-probabilitiy",
    response_model=AuroraProbabilityResponse,
)
async def api_aurora_probability(
    ub: UserBody,
    dst: swpc_req.DstDep,
    bz: swpc_req.BzDep,
    kp: swpc_req.KpDep,
):
    """Получение вероятности северного сияния по заданным параметрам"""
    ad = SwpcApiData(dst=dst, bz=bz, kp=kp)
    res = aurora_probability(
        user_data=ub,
        dst=ad.dst,
        bz=ad.bz,
        kp=ad.kp,
        speed=ub.speed,
        clouds=ub.clouds,
    )

    return AuroraProbabilityResponse(
        calc_data=res,
        user_data=ub,
        api_data=ad,
    )


@router.post(
    "/aurora-nooa-probability", response_model=AuroraNooaProbabilityResponse
)
async def api_aurora_nooa_probability(
    req: NooaAuroraReq, aurora_res: nooa_req.AuroraDep
):
    """Получение вероятности северного сияния по заданным координатам из nooa"""
    res = nooa_req.NooaAuroraRes.model_validate(json.loads(aurora_res))  # type: ignore
    return nearst_aurora_probability(pos=req, prob_map=res)


@router.get("/aurora-map", response_model=nooa_req.NooaAuroraRes)
async def api_aurora_map(aurora_res: nooa_req.AuroraDep):
    """Получение карты северного сияния"""
    return Response(content=aurora_res, media_type="application/json")


@router.get("/aurora-kp-3", response_model=nooa_req.NooaAuroraKp3Req)
async def api_aurora_kp_3(aurora_kp_res: nooa_req.Kp3Dep):
    """Получение планетарного k-индекса за 3 дня"""
    return aurora_kp_res


@router.get("/aurora-kp-27", response_model=nooa_req.NooaAuroraKp27Req)
async def api_aurora_kp_map(aurora_kp_res: nooa_req.Kp27Dep):
    """Получение планетарного k-индекса за 27 дней"""
    return aurora_kp_res


@router.get("/all-cities", response_model=list[City])
async def api_all_cities():
    """Получение списка всех городов для выбора"""
    return await Cities.all()


@router.get("/all-tours", response_model=list[Tour])
async def api_all_tours():
    """Получение списка всех туров для выбора"""
    return await Tours.all()


@router.get("/banner", response_model=BannerIn)
async def api_banner(id: int = 1):
    """Получение баннера"""
    b = await Banners.get_or_none(id=1)
    if b is None:
        raise HTTPException(status_code=404, detail="Banner not found")
    return b
