from functools import wraps

import httpx
import pytest
from fastapi.testclient import TestClient
from tortoise import Tortoise

from internal.db.config import ORM_MODELS
from internal.settings import ADMIN_PASS, ADMIN_TEST_PASS, ADMIN_USER
from main import app

MEMORY_SQLITE = "sqlite://:memory:"


@pytest.fixture
def client():
    return TestClient(app)


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


admin_auth = httpx.BasicAuth(username=ADMIN_USER, password=ADMIN_TEST_PASS)
