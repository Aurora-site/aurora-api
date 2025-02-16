from functools import wraps

import httpx
from tortoise import Tortoise

from internal.db.config import ORM_MODELS
from internal.settings import ADMIN_PASS, ADMIN_USER

MEMORY_SQLITE = "sqlite://:memory:"


def init_memory_sqlite(models: list[str] | None = None):
    if models is None:
        models = ORM_MODELS

    def wrapper(func):
        @wraps(func)
        async def runner(*args, **kwargs):
            await Tortoise.init(
                db_url=MEMORY_SQLITE,
                modules={"models": models},
            )
            await Tortoise.generate_schemas()
            try:
                await func(*args, **kwargs)
            finally:
                await Tortoise.close_connections()

        return runner

    return wrapper


admin_auth = httpx.BasicAuth(username=ADMIN_USER, password=ADMIN_PASS)
