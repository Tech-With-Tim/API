from api import app as quart_app

from quart.testing import QuartClient
import pytest


@pytest.fixture(name="app")
def _test_app() -> QuartClient:
    return quart_app.test_client()


@pytest.mark.asyncio
async def test_index(app: QuartClient):
    response = await app.get("/")
    assert response.status_code == 200
