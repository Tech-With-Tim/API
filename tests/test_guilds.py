from api.models import Guild

from quart.testing import QuartClient
import pytest


def guild_to_dict(guild: Guild) -> dict:
    return {
        "id": str(guild.id),
        "name": guild.name,
        "owner_id": str(guild.owner_id),
        "icon_hash": guild.icon_hash,
    }


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
async def test_create_guild(auth_app: QuartClient, db, data: dict, status_code: int):
    response = await auth_app.post(
        "/guilds", json=data, headers={"authorization": auth_app.token}
    )
    assert response.content_type == "application/json"
    assert response.status_code == status_code
    if status_code == 201:
        assert (await response.json) == {
            n: str(data.get(n, "")) or None
            for n in ("id", "name", "owner_id", "icon_hash")
        }
        assert response.headers["Location"] == f"/guilds/{data['id']}"


@pytest.mark.asyncio
@pytest.mark.db
async def test_get_guild(app: QuartClient, db, guild: Guild):
    response = await app.get(f"/guilds/{guild.id}")
    assert response.status_code == 200
    assert response.content_type == "application/json"
    assert (await response.json) == guild_to_dict(guild)


@pytest.mark.asyncio
@pytest.mark.db
async def test_get_guild_404(app: QuartClient, db):
    response = await app.get("/guilds/0")  # spamming random digits on keyboard
    assert response.status_code == 404
    assert response.content_type == "application/json"


@pytest.mark.asyncio
@pytest.mark.db
async def test_patch_guild(auth_app: QuartClient, db):
    guild = await Guild.create(
        id=420,
        name="Tim is the best",
        owner_id=501089409379205161,
        icon_hash="63fadd7a1f176935279865f88bd3c1e8",
    )
    response = await auth_app.patch(
        f"/guilds/{guild.id}",
        json={"owner_id": 268837679884402688, "name": "avib is the best"},
        headers={"authorization": auth_app.token},
    )
    assert response.status_code == 200
    assert response.content_type == "application/json"
    guild = await Guild.fetch(guild.id)  # guild was updated in db, need to fetch again
    assert (await response.json) == guild_to_dict(guild)


@pytest.mark.asyncio
@pytest.mark.db
async def test_delete_guild(auth_app: QuartClient, db):
    guild = await Guild.create(
        id=781645181744316476,
        name="postDB",
        owner_id=144112966176997376,
        icon_hash="ffa2d83b0779a1cf240f8df018324be6",
    )
    response = await auth_app.delete(
        f"/guilds/{guild.id}", headers={"authorization": auth_app.token}
    )
    assert response.status_code == 204
    guild = await Guild.fetch(guild.id)  # guild was deleted in db, need to fetch again
    assert guild is None
