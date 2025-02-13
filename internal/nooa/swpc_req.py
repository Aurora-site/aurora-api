from datetime import datetime
from typing import Annotated

import hishel
from fastapi import Depends
from pydantic import BaseModel, Field

controller = hishel.Controller(force_cache=True)
storage = hishel.InMemoryStorage(capacity=64, ttl=3600)
client = hishel.CacheClient(storage=storage, controller=controller)


class SwpcDstReq(BaseModel):
    dst: float
    time_tag: datetime


def use_dst_client() -> SwpcDstReq:
    res = client.get(
        "https://services.swpc.noaa.gov/json/geospace/geospace_dst_1_hour.json"
    )
    if res.status_code != 200:
        raise Exception("Failed to get data from swpc (dst client)")
    data = res.json()[0]
    return SwpcDstReq.model_validate(data)


DstDep = Annotated[SwpcDstReq, Depends(use_dst_client)]


class SwpcBzReq(BaseModel):
    bz_gsm: float
    bz_gse: float
    time_tag: datetime


def use_bz_client() -> SwpcBzReq:
    res = client.get(
        "https://services.swpc.noaa.gov/json/dscovr/dscovr_mag_1s.json"
    )
    if res.status_code != 200:
        raise Exception("Failed to get data from swpc (bz client)")
    data = res.json()[0]
    return SwpcBzReq.model_validate(data)


BzDep = Annotated[SwpcBzReq, Depends(use_bz_client)]


class SwpcKpReq(BaseModel):
    kp: int = Field(alias="kp_index")
    time_tag: datetime


def use_kp_client() -> SwpcKpReq:
    res = client.get(
        "https://services.swpc.noaa.gov/json/planetary_k_index_1m.json"
    )
    if res.status_code != 200:
        raise Exception("Failed to get data from swpc (kp client)")
    data = res.json()[0]
    return SwpcKpReq.model_validate(data)


KpDep = Annotated[SwpcKpReq, Depends(use_kp_client)]
