import pytest
from fastapi.testclient import TestClient

from internal.db.schemas import BannerIn
from tests.test_utils import admin_auth, client, init_memory_sqlite


@pytest.fixture
def banner():
    return BannerIn(
        name="test",
        url="https://test.com/test.png",
    )


def setup_banner(client: TestClient, banner: BannerIn) -> dict:
    res = client.post(
        "/api/v1/set-banner",
        json=banner.model_dump(),
        auth=admin_auth,
    )
    assert res.status_code == 200
    return res.json()


@pytest.mark.asyncio
@init_memory_sqlite()
async def test_add_banner(client: TestClient, banner: BannerIn):
    b = setup_banner(client, banner)
    assert b == banner.model_dump()
