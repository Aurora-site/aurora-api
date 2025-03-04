from typing import Annotated

import httpx
from fastapi import APIRouter, Path, Response

client = httpx.AsyncClient()


router = APIRouter(
    prefix="/api/v1",
    tags=["Proxy"],
)

OsmCoord = Annotated[int, Path()]


@router.get("/proxy/osm-tile-map/{z}/{x}/{y}.png")
async def api_cloud_map(
    z: OsmCoord,
    x: OsmCoord,
    y: OsmCoord,
):
    res = await client.get(f"https://tile.openstreetmap.org/{z}/{x}/{y}.png")
    return Response(content=res.content, media_type="image/png")
