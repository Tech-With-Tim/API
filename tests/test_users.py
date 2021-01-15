import os
from api import app as quart_app

from quart.testing import QuartClient
from postDB import Model
import pytest


@pytest.fixture(name="app")
def _test_app() -> QuartClient:
    return quart_app.test_client()


@pytest.mark.asyncio
async def test_get_all_users_no_queries(app: QuartClient):
    await Model.create_pool(os.environ["DB_URI"])
    response = await app.get("/users/get-all")
    assert response.status_code == 200
    assert response.content_type == "application/json"
