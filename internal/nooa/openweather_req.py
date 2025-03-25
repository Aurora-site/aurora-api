from typing import Annotated

import hishel
from fastapi import Path, Response

from internal.routers.api_router import router
from internal.settings import OW_API_KEY

# cap is 64 cuz its max amount of tiles we need to full world map on client
storage = hishel.InMemoryStorage(capacity=64, ttl=30 * 60)
controller = hishel.Controller(force_cache=True, allow_stale=True)
client = hishel.CacheClient(storage=storage, controller=controller)


@router.get("/cloud-map/{z}/{x}/{y}")
async def api_cloud_map(
    z: Annotated[int, Path(ge=3, le=3)],
    x: Annotated[int, Path(ge=0, le=7)],
    y: Annotated[int, Path(ge=0, le=7)],
):
    """Получение тайлов облачнсти от OpenWeatherMap

    - **Источник**: openweathermap.org
    - **Cache TTL**: 30 минут
    - **Cache Size**: 64 тайла
    """
    res = client.get(
        f"https://tile.openweathermap.org/map/clouds/"
        f"{z}/{x}/{y}.png?appid={OW_API_KEY}"
    )
    if res.status_code != 200:
        raise Exception("Failed to get cloud map data (aurora client)")
    return Response(content=res.content, media_type="image/png")
