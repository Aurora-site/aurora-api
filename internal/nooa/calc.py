from datetime import datetime, timezone
from typing import Annotated

from fastapi import Body
from pydantic import AwareDatetime, BaseModel, Field

from internal.nooa import swpc_req
from internal.nooa.nooa_req import NooaAuroraRes
from internal.validators import GeoFloat


# Определение геомагнитной широты
def calculate_geomagnetic_latitude(latitude: float, longitude: float) -> float:
    # Простое преобразование, точный расчет возможен через GeoMag
    return min(latitude + 5, 90)


# Функции расчёта:
# Определение зоны видимости на основе Kp-индекса
def kp_zone(kp: int) -> int:
    kp_zones = {
        1: 67,
        2: 66,
        3: 65,
        4: 60,
        5: 55,
        6: 50,
        7: 45,
        8: 40,
        9: 35,
    }
    return kp_zones.get(kp, 0)


# Вес Bz
def bz_factor(bz: float) -> float:
    if bz < 0:  # Южное направление
        return 1.5 + abs(bz) / 10
    else:  # Северное направление
        return max(0.8, 1.0 - bz / 10)


# Вес по скорости солнечного ветра
def speed_factor(speed: float) -> float:
    return 1.0 if speed > 400 else 0.5


# Вес по Dst-индексу
def dst_factor(dst: float) -> float:
    return 1.2 if dst < -50 else 1.0


# Вес по облачности
def clouds_factor(clouds: float) -> float:
    return 1 - clouds / 100


# Вес времени суток
def time_factor(local_hour: int) -> float:
    return 1.0 if 22 <= local_hour or local_hour <= 2 else 0.5


class AuroraProbabilityCalculation(BaseModel):
    base_probability: float
    bz_weight: float
    speed_weight: float
    dst_weight: float
    clouds_weight: float
    time_weight: float
    probability: float


class AuroraProbabilityBody(BaseModel):
    local_time: AwareDatetime = datetime.now(timezone.utc)
    lat: float
    lon: float
    speed: float = 450
    clouds: float = 30


UserBody = Annotated[
    AuroraProbabilityBody,
    Body(
        openapi_examples={
            "Murmansk": {
                "value": {
                    "lat": 68.9792,
                    "lon": 33.0925,
                }
            },
            "Kirov": {
                "value": {
                    "lat": 58.6,
                    "lon": 49.6,
                }
            },
            "Moscow": {
                "value": {
                    "local_time": "2023-03-01T00:00:00+03:00",
                    "lat": 55.75,
                    "lon": 37.62,
                    "speed": 450,
                    "clouds": 30,
                }
            },
        }
    ),
]


# Основной расчёт:
def aurora_probability(
    user_data: AuroraProbabilityBody,
    dst: swpc_req.SwpcDstReq,
    bz: swpc_req.SwpcBzReq,
    kp: swpc_req.SwpcKpReq,
    speed: float,
    clouds: float,
) -> AuroraProbabilityCalculation:
    # Расчёт геомагнитной широты
    geomagnetic_latitude = calculate_geomagnetic_latitude(
        user_data.lat, user_data.lon
    )

    # Зона видимости по Kp-индексу
    visibility_zone = kp_zone(kp.kp)
    base_probability = max(
        0, (100 - (visibility_zone - geomagnetic_latitude) * 10)
    )

    # Весовые коэффициенты
    bz_weight = bz_factor(bz.bz_gse)
    speed_weight = speed_factor(speed)
    dst_weight = dst_factor(dst.dst)
    clouds_weight = clouds_factor(clouds)
    time_weight = time_factor(user_data.local_time.hour)

    # Итоговая вероятность
    probability = (
        base_probability
        * bz_weight
        * speed_weight
        * dst_weight
        * clouds_weight
        * time_weight
    )
    return AuroraProbabilityCalculation(
        base_probability=base_probability,
        bz_weight=bz_weight,
        speed_weight=speed_weight,
        dst_weight=dst_weight,
        clouds_weight=clouds_weight,
        time_weight=time_weight,
        probability=min(probability, 100),
    )


class NooaAuroraReq(BaseModel):
    lat: GeoFloat
    lon: GeoFloat


class AuroraNooaProbabilityResponse(BaseModel):
    probability: int = Field(le=100, ge=0)
    lat: int
    lon: int
    nooa_lat: int
    nooa_lon: int


def nearst_aurora_probability(
    pos: NooaAuroraReq,
    prob_map: NooaAuroraRes,
):
    rounded_lat = round(pos.lat, 0)
    rounded_lon = round(pos.lon, 0)
    nooa_lon, nooa_lat, pb = next(
        v
        for v in prob_map.coordinates
        # fmt: off
        if v[:2] == [
            rounded_lon if rounded_lon > 0 else rounded_lon + 360,
            rounded_lat,
        ]
        # fmt: on
    )
    return AuroraNooaProbabilityResponse(
        probability=pb,
        nooa_lat=nooa_lat,
        nooa_lon=nooa_lon,
        lat=rounded_lat,
        lon=rounded_lon,
    )
