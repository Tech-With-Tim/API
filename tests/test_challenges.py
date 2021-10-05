import pytest

from httpx import AsyncClient

from api.models import Role, UserRole, ChallengeLanguage
from api.models.permissions import ManageWeeklyChallengeLanguages
from api.services import piston


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


async def complete_piston_data(data: dict):
    """Replace "TO COMPLETE" data with actual data from the Piston API"""
    if (
        data.get("piston_lang") == "TO COMPLETE"
        or data.get("piston_lang_ver") == "TO COMPLETE"
    ):
        runtime = (await piston.get_runtimes())[0]

        if data.get("piston_lang") == "TO COMPLETE":
            data["piston_lang"] = runtime.language

        if data.get("piston_lang_ver") == "TO COMPLETE":
            data["piston_lang_ver"] = runtime.version


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
                "download_url": "not an url",
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
    data,
    status,
):
    await complete_piston_data(data)

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


@pytest.mark.db
@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("request_data", "new_data", "status"),
    [
        (
            {},
            {
                "name": "test",
                "download_url": "https://example.com/download",
                "disabled": False,
                "piston_lang": "testlang",
                "piston_lang_ver": "1.2.3",
            },
            204,
        ),
        (
            {"name": ""},
            {
                "name": "test",
                "download_url": "https://example.com/download",
                "disabled": False,
                "piston_lang": "testlang",
                "piston_lang_ver": "1.2.3",
            },
            422,
        ),
        (
            {"download_url": "not an url"},
            {
                "name": "test",
                "download_url": "https://example.com/download",
                "disabled": False,
                "piston_lang": "testlang",
                "piston_lang_ver": "1.2.3",
            },
            422,
        ),
        (
            {"disabled": "not a boolean"},
            {
                "name": "test",
                "download_url": "https://example.com/download",
                "disabled": False,
                "piston_lang": "testlang",
                "piston_lang_ver": "1.2.3",
            },
            422,
        ),
        (
            {
                "piston_lang": "doesntexist",
                "piston_lang_ver": "0.0.0",
            },
            {
                "name": "test",
                "download_url": "https://example.com/download",
                "disabled": False,
                "piston_lang": "testlang",
                "piston_lang_ver": "1.2.3",
            },
            404,
        ),
        (
            {
                "name": "new name",
                "download_url": "https://test.com/download",
                "piston_lang": "TO COMPLETE",  # completed inside the test bcs the wrapper is async
                "piston_lang_ver": "TO COMPLETE",
            },
            {
                "name": "new name",
                "download_url": "https://test.com/download",
                "disabled": False,
                "piston_lang": "TO COMPLETE",  # completed inside the test bcs the wrapper is async
                "piston_lang_ver": "TO COMPLETE",
            },
            204,
        ),
    ],
)
async def test_challenge_language_update(
    app: AsyncClient,
    db,
    user,
    token,
    manage_challenge_languages_role,
    request_data,
    new_data,
    status,
):
    await complete_piston_data(request_data)
    await complete_piston_data(new_data)

    try:
        await UserRole.create(user.id, manage_challenge_languages_role.id)

        query = """
            INSERT INTO challengelanguages (id, name, download_url, disabled, piston_lang, piston_lang_ver)
                VALUES (create_snowflake(), $1, $2, $3, $4, $5)
                RETURNING *;
        """
        language = ChallengeLanguage(
            **await db.fetchrow(
                query,
                "test",
                "https://example.com/download",
                False,
                "testlang",
                "1.2.3",
            )
        )

        res = await app.patch(
            f"/api/v1/challenges/languages/{language.id}",
            json=request_data,
            headers={"Authorization": token},
        )

        assert res.status_code == status

        language = ChallengeLanguage(
            **await db.fetchrow(
                "SELECT * FROM challengelanguages WHERE id = $1", language.id
            )
        )

        data = language.as_dict()
        data.pop("id")

        assert data == new_data
    finally:
        await UserRole.delete(user.id, manage_challenge_languages_role.id)
        await db.execute("DELETE FROM challengelanguages WHERE id = $1", language.id)


# TODO test DELETE /challenges/languages/{id}
