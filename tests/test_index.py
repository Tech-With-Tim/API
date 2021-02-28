from quart.testing import QuartClient
import pytest


@pytest.mark.asyncio
async def test_index(app: QuartClient):
    response = await app.get("/")
    assert response.status_code == 200
    assert response.content_type == "application/json"
    assert await response.get_json() == {"status": "OK"}
