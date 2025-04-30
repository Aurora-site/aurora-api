import pytest
from fastapi.testclient import TestClient

from internal.db.schemas import BannerIn

from . import admin_auth


@pytest.fixture
def banner():
    return BannerIn(
        default=True,
        name="test",
        url="https://test.com/test.png",
    )


@pytest.fixture
def banner_by_city_id():
    return BannerIn(
        city_id=1,
        name="test",
        url="https://test.com/test.png",
    )


@pytest.fixture
def banner_by_locale():
    return BannerIn(
        locale="ru",
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
