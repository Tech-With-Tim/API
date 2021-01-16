from api import app as quart_app

from quart.testing import QuartClient
import pytest


@pytest.mark.asyncio
@pytest.mark.db
@pytest.mark.parametrize(
    ("data", "status_code"),
    [
        (
            {
                "id": "1",
                "name": "a",
                "owner_id": "1",
            },
            201,
        ),
        (
            {
                "id": 2,
                "name": "b",
                "owner_id": 2,
            },
            201,
        ),
        (
            {
                "id": 3,
                "name": "c",
                "owner_id": 3,
                "icon_hash": "abcdefgh",
            },
            201,
        ),
        (
            {
                "id": 3,
                "name": "c",
                "owner_id": 3,
            },
            409,
        ),
        (
            {},
            400,
        ),
    ],
)
async def test_create_guild(app: QuartClient, db, data: dict, status_code: int):
    response = await app.post("/guilds", json=data)
    assert response.content_type == "application/json"
    assert response.status_code == status_code
