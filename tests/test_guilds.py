from api.models import Guild

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
        (
            None,
            400,
        ),
    ],
)
async def test_create_guild(app: QuartClient, db, data: dict, status_code: int):
    response = await app.post("/guilds", json=data)
    assert response.content_type == "application/json"
    assert response.status_code == status_code


@pytest.mark.asyncio
@pytest.mark.db
async def test_get_guild(app: QuartClient, db):
    guild = await Guild.create(
        id=501090983539245061,
        name="Tech With Tim",
        owner_id=501089409379205161,
        icon_hash="a_5aa83d87a200585758846a075ffc52ba",
    )
    response = await app.get(f"/guilds/{guild.id}")
    assert response.status_code == 200
    assert response.content_type == "application/json"
    json = await response.json
    assert int(json["id"]) == guild.id
    assert json["name"] == guild.name
    assert int(json["owner_id"]) == guild.owner_id
    assert json["icon_hash"] == guild.icon_hash


@pytest.mark.asyncio
@pytest.mark.db
async def test_get_guild_404(app: QuartClient, db):
    response = await app.get("/guilds/523456202403")  # spamming random digits on keyboard
    assert response.status_code == 404
    assert response.content_type == "application/json"
    json = await response.json
    assert json["error"] == "Not found"


@pytest.mark.asyncio
@pytest.mark.db
async def test_patch_guild(app: QuartClient, db):
    guild = await Guild.create(
        id=420,
        name="Tim is the best",
        owner_id=501089409379205161,
        icon_hash="63fadd7a1f176935279865f88bd3c1e8",
    )
    response = await app.patch(
        f"/guilds/{guild.id}", json={"owner_id": 268837679884402688, "name": "avib is the best"}
    )
    assert response.status_code == 200
    assert response.content_type == "application/json"
    json = await response.json
    guild = await Guild.fetch(guild.id)  # guild was updated in db, need to fetch again
    assert int(json["id"]) == guild.id
    assert json["name"] == guild.name
    assert int(json["owner_id"]) == guild.owner_id
    assert json["icon_hash"] == guild.icon_hash


# TODO: Add test for DELETE /guilds/<id>
# TODO: Add test for GET /guilds/<id>/icon
