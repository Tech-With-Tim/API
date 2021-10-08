import pytest

from httpx import AsyncClient

from api.models import Challenge, ChallengeLanguage, Role, User, UserRole
from api.models.permissions import (
    CreateWeeklyChallenge,
    EditWeeklyChallenge,
    DeleteWeeklyChallenge,
    ManageWeeklyChallengeLanguages,
)
from api.services import piston


@pytest.fixture(scope="module")
async def manage_challenges_role(db):
    query = """
        INSERT INTO roles (id, name, color, permissions, position)
            VALUES (create_snowflake(), $1, $2, $3, (SELECT COUNT(*) FROM roles) + 1)
            RETURNING *;
    """
    record = await Role.pool.fetchrow(
        query,
        "Challenges Manager",
        0x0,
        CreateWeeklyChallenge().value
        + EditWeeklyChallenge().value
        + DeleteWeeklyChallenge().value,
    )
    yield Role(**record)
    await db.execute("DELETE FROM roles WHERE id = $1;", record["id"])


@pytest.fixture(scope="function")
async def manage_challenges_user(manage_challenges_role: Role, user: User):
    await UserRole.create(user.id, manage_challenges_role.id)
    yield user
    await UserRole.delete(user.id, manage_challenges_role.id)


@pytest.fixture(scope="module")
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


@pytest.fixture(scope="function")
async def manage_challenge_languages_user(
    manage_challenge_languages_role: Role, user: User
):
    await UserRole.create(user.id, manage_challenge_languages_role.id)
    yield user
    await UserRole.delete(user.id, manage_challenge_languages_role.id)


@pytest.fixture(scope="function")
async def language(db, manage_challenge_languages_user: User):
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
    yield language
    await db.execute("DELETE FROM challengelanguages WHERE id = $1", language.id)


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
    token: str,
    manage_challenge_languages_user: User,
    data: dict,
    status: int,
):
    await complete_piston_data(data)

    try:
        res = await app.post(
            "/api/v1/challenges/languages",
            json=data,
            headers={"Authorization": token},
        )
        assert res.status_code == status

    finally:
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
    token,
    language: ChallengeLanguage,
    request_data: dict,
    new_data: dict,
    status: int,
):
    await complete_piston_data(request_data)
    await complete_piston_data(new_data)

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


@pytest.mark.db
@pytest.mark.asyncio
async def test_challenge_language_delete_success(
    app: AsyncClient,
    db,
    token: str,
    language: ChallengeLanguage,
):
    res = await app.delete(
        f"/api/v1/challenges/languages/{language.id}",
        headers={"Authorization": token},
    )

    assert res.status_code == 204

    record = await db.fetchrow(
        "SELECT * FROM challengelanguages WHERE id = $1", language.id
    )
    assert record is None


@pytest.mark.db
@pytest.mark.asyncio
async def test_challenge_language_delete_fail_403(
    app: AsyncClient,
    db,
    token: str,
    manage_challenges_user: User,
    language: ChallengeLanguage,
):
    try:
        query = """
            INSERT INTO challenges (id, title, slug, author_id, description, example_in, example_out, language_ids)
                VALUES (create_snowflake(), $1, $2, $3, $4, $5, $6, $7)
                RETURNING *;
        """
        challenge = Challenge(
            **await db.fetchrow(
                query,
                "Test challenge",
                "test-challenge",
                manage_challenges_user.id,
                "For testing",
                ["in"],
                ["out"],
                [language.id],
            )
        )

        res = await app.delete(
            f"/api/v1/challenges/languages/{language.id}",
            headers={"Authorization": token},
        )

        assert res.status_code == 403
    finally:
        await db.execute("DELETE FROM challenges WHERE id = $1", challenge.id)


@pytest.mark.db
@pytest.mark.asyncio
async def test_challenge_language_delete_fail_404(
    app: AsyncClient,
    token: str,
    manage_challenge_languages_user: User,
):
    res = await app.delete(
        "/api/v1/challenges/languages/0",
        headers={"Authorization": token},
    )

    assert res.status_code == 404
