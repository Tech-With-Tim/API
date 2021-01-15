from api import app as quart_app

from quart.testing import QuartClient
import pytest


@pytest.fixture(name="app")
def _test_app() -> QuartClient:
    return quart_app.test_client()


@pytest.mark.asyncio
async def test_get_all_users_no_queries(app: QuartClient):
    response = await app.get("/users/get-all?discriminator=2")
    assert response.status_code == 200
    assert response.content_type == "application/json"
