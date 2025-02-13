from datetime import datetime
from typing import Annotated

import hishel
from fastapi import Depends
from pydantic import BaseModel, Field

from internal.nooa.nooa_parser import (
    NooaAuroraKp3Col,
    NooaAuroraKp27Row,
    parse_kp_3_forecast,
    parse_kp_27_outlook,
)

controller = hishel.Controller(force_cache=True)
storage = hishel.InMemoryStorage(capacity=64, ttl=3600)
client = hishel.CacheClient(storage=storage, controller=controller)

long_storage = hishel.InMemoryStorage(capacity=64, ttl=24 * 3600)
long_client = hishel.CacheClient(storage=long_storage, controller=controller)


class NooaAuroraRes(BaseModel):
    Observation_Time: datetime = Field(alias="Observation Time")
    Forecast_Time: datetime = Field(alias="Forecast Time")
    Data_Format: str = Field(alias="Data Format")
    coordinates: list[list[int]]

    model_config = {
        "populate_by_name": True,
        "json_schema_extra": {
            "examples": [
                {
                    "Observation_Time": "2025-01-11T15:06:00Z",
                    "Forecast_Time": "2025-01-11T16:06:00Z",
                    "Data_Format": "[Longitude, Latitude, Aurora]",
                    "coordinates": [
                        [0, -90, 3],
                        [0, -89, 0],
                        [0, -88, 4],
                        [0, -87, 5],
                    ],
                }
            ]
        },
    }


def use_nooa_aurora_client() -> bytes:
    res = client.get(
        "https://services.swpc.noaa.gov/json/ovation_aurora_latest.json"
    )
    if res.status_code != 200:
        raise Exception("Failed to get data from nooa (aurora client)")
    return res.content


AuroraDep = Annotated[NooaAuroraRes, Depends(use_nooa_aurora_client)]


# https://services.swpc.noaa.gov/text/3-day-forecast.txt
NooaAuroraKp3Req = list[NooaAuroraKp3Col]


def use_nooa_aurora_kp_client() -> NooaAuroraKp3Req:
    res = long_client.get(
        "https://services.swpc.noaa.gov/text/3-day-forecast.txt"
    )
    if res.status_code != 200:
        raise Exception("Failed to get data from nooa (3-day-forecast)")
    return parse_kp_3_forecast(res.text)


Kp3Dep = Annotated[NooaAuroraKp3Req, Depends(use_nooa_aurora_kp_client)]


# https://services.swpc.noaa.gov/text/27-day-outlook.txt
NooaAuroraKp27Req = list[NooaAuroraKp27Row]


def use_nooa_aurora_kp_27_client() -> NooaAuroraKp27Req:
    res = long_client.get(
        "https://services.swpc.noaa.gov/text/27-day-outlook.txt"
    )
    if res.status_code != 200:
        raise Exception("Failed to get data from nooa (27-day-outlook)")
    return parse_kp_27_outlook(res.text)


Kp27Dep = Annotated[NooaAuroraKp27Req, Depends(use_nooa_aurora_kp_27_client)]
