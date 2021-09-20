import pytest

from httpx import AsyncClient

from api.models import Role, UserRole
from api.models.permissions import ManageWeeklyChallengeLanguages
from api.services import piston as piston_service


@pytest.fixture
async def manage_challenge_languages_role(db):
    query = """
        INSERT INTO roles (id, name, color, permissions, position)
            VALUES (create_snowflake(), $1, $2, $3, (SELECT COUNT(*) FROM roles) + 1)
            RETURNING *;
    """
    record = await Role.pool.fetchrow(
        query,
        "Challenge Languages Manager",
        0x0,
        ManageWeeklyChallengeLanguages().value,
    )
    yield Role(**record)
    await db.execute("DELETE FROM roles WHERE id = $1;", record["id"])


@pytest.fixture(scope="session")
async def piston():
    piston_service.init()
    yield piston_service.client
    await piston_service.close()


@pytest.mark.db
@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("data", "status"),
    [
        ({}, 422),
        (
            {
                "name": "",
                "piston_lang": "....",
                "piston_lang_ver": "....",
            },
            422,
        ),
        (
            {
                "name": "....",
                "piston_lang": "....",
                "piston_lang_ver": "....",
                "download_url": "this isn't an url",
            },
            422,
        ),
        (
            {
                "name": "....",
                "piston_lang": "doesntexist",
                "piston_lang_ver": "0.0.0",
            },
            404,
        ),
        (
            {
                "name": "test1",
                "piston_lang": "TO COMPLETE",  # completed inside the test bcs the wrapper is async
                "piston_lang_ver": "TO COMPLETE",
            },
            201,
        ),
        (
            {
                "name": "test1",
                "piston_lang": "TO COMPLETE",  # completed inside the test bcs the wrapper is async
                "piston_lang_ver": "TO COMPLETE",
            },
            409,
        ),
    ],
)
async def test_challenge_languages_create(
    app: AsyncClient,
    db,
    user,
    token,
    manage_challenge_languages_role,
    piston: piston_service.PistonClient,
    data,
    status,
):
    if data.get("piston_lang") == "TO COMPLETE":
        runtime = (await piston.get_runtimes())[0]
        data["piston_lang"] = runtime.language
        data["piston_lang_ver"] = runtime.version
    try:
        await UserRole.create(user.id, manage_challenge_languages_role.id)
        res = await app.post(
            "/api/v1/challenges/languages",
            json=data,
            headers={"Authorization": token},
        )
        assert res.status_code == status
    finally:
        await UserRole.delete(user.id, manage_challenge_languages_role.id)
        if status == 409:
            await db.execute(
                "DELETE FROM challengelanguages WHERE name = $1", data["name"]
            )


@pytest.mark.db
@pytest.mark.asyncio
async def test_fetch_all_challenge_languages(app: AsyncClient):
    res = await app.get("/api/v1/challenges/languages")

    assert res.status_code == 200
    assert type(res.json()) == list
