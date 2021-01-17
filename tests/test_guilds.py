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
    if status_code == 201:
        json = await response.json
        assert int(json["id"]) == int(data["id"])
        assert json["name"] == data["name"]
        assert int(json["owner_id"]) == int(data["owner_id"])
        assert json["icon_hash"] == data.get("icon_hash", None)
        assert response.headers["Location"] == f"/guilds/{data['id']}"


@pytest.mark.asyncio
@pytest.mark.db
async def test_get_guild(app: QuartClient, db, guild: Guild):
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
    response = await app.get(
        "/guilds/523456202403"
    )  # spamming random digits on keyboard
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
        f"/guilds/{guild.id}",
        json={"owner_id": 268837679884402688, "name": "avib is the best"},
    )
    assert response.status_code == 200
    assert response.content_type == "application/json"
    json = await response.json
    guild = await Guild.fetch(guild.id)  # guild was updated in db, need to fetch again
    assert int(json["id"]) == guild.id
    assert json["name"] == guild.name
    assert int(json["owner_id"]) == guild.owner_id
    assert json["icon_hash"] == guild.icon_hash


@pytest.mark.asyncio
@pytest.mark.db
async def test_delete_guild(app: QuartClient, db):
    guild = await Guild.create(
        id=781645181744316476,
        name="postDB",
        owner_id=144112966176997376,
        icon_hash="ffa2d83b0779a1cf240f8df018324be6",
    )
    response = await app.delete(f"/guilds/{guild.id}")
    assert response.status_code == 200
    assert response.content_type == "application/json"
    json = await response.json
    assert int(json["id"]) == guild.id
    assert json["name"] == guild.name
    assert int(json["owner_id"]) == guild.owner_id
    assert json["icon_hash"] == guild.icon_hash
    guild = await Guild.fetch(guild.id)  # guild was deleted in db, need to fetch again
    assert guild is None


@pytest.fixture(name="guild", scope="session")
async def _guild():
    return await Guild.create(
        id=501090983539245061,
        name="Tech With Tim",
        owner_id=501089409379205161,
        icon_hash="a_5aa83d87a200585758846a075ffc52ba",
    )


@pytest.mark.asyncio
@pytest.mark.db
@pytest.mark.parametrize(
    ("querystring", "expected_url"),
    [("", "gif?size=128")]
    + [
        (f"format={format}", f"{format}?size=128")
        for format in ["jpeg", "jpg", "webp", "png", "gif"]
    ]
    + [
        (f"size={size}", f"gif?size={size}")
        for size in [16, 32, 64, 128, 256, 512, 1024, 2048, 4096]
    ],
)
async def test_get_guild_icon(
    app: QuartClient, db, guild: Guild, querystring: str, expected_url: str
):
    response = await app.get(f"/guilds/{guild.id}/icon?{querystring}")
    assert response.status_code == 302
    assert (
        response.headers["Location"]
        == f"https://cdn.discordapp.com/icons/{guild.id}/{guild.icon_hash}.{expected_url}"
    )
