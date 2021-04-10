from api.models import Challenge

from quart.testing import QuartClient
import pytest


def challenge_to_dict(challenge: Challenge) -> dict:
    return {
        "id": str(challenge.id),
        "title": challenge.title,
        "description": str(challenge.description),
        "examples": challenge.examples,
        "rules": challenge.rules,
        "created_by": challenge.created_by,
        "difficulty": challenge.difficulty,
    }


@pytest.fixture(name="challenge", scope="session")
async def _challenge():
    return await Challenge.create(
        id="1",
        title="test",
        description="this is a test",
        examples="x = 1",
        rules="work",
        created_by="sarzz",
        difficulty="easy",
    )


@pytest.mark.asyncio
@pytest.mark.db
@pytest.mark.parametrize(
    ("data", "status_code"),
    [
        (
            {
                "id": "1",
                "title": "changed",
                "description": "this is a test",
                "examples": "x = 1",
                "rules": "work",
                "created_by": "sarzz",
                "difficulty": "easy",
            },
            201,
        ),
        (
            {
                "id": 2,
                "title": "changed",
                "description": "this is a test",
                "examples": "x = 1",
                "rules": "work",
                "created_by": "sarzz",
                "difficulty": "easy",
            },
            201,
        ),
        (
            {
                "id": 3,
                "title": "c",
                "description": "xx",
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
async def test_create_weekly_challenge(
    auth_app: QuartClient, db, data: dict, status_code: int
):
    response = await auth_app.post(
        "/", json=data, headers={"authorization": auth_app.token}
    )
    assert response.content_type == "application/json"
    assert response.status_code == status_code
    if status_code == 201:
        assert (await response.json) == {
            n: str(data.get(n, "")) or None
            for n in (
                "id",
                "title",
                "description",
                "examples",
                "rules",
                "created_by",
                "difficulty",
            )
        }
        assert response.headers["Location"] == f"/wkc/{data['id']}"


@pytest.mark.asyncio
@pytest.mark.db
async def test_get_weekly_challenge(app: QuartClient, db, challenge: Challenge):
    response = await app.get(f"/wkc/{challenge.id}")
    assert response.status_code == 200
    assert response.content_type == "application/json"
    assert (await response.json) == challenge_to_dict(challenge)


@pytest.mark.asyncio
@pytest.mark.db
async def test_get_weekly_challenge_404(app: QuartClient, db):
    response = await app.get("/wkc/0")  # spamming random digits on keyboard
    assert response.status_code == 404
    assert response.content_type == "application/json"


@pytest.mark.asyncio
@pytest.mark.db
async def test_patch_guild(auth_app: QuartClient, db):
    challenge = await Challenge.create(
        id="1",
        title="test",
        description="this is a test",
        examples="x = 1",
        rules="work",
        created_by="sarzz",
        difficulty="easy",
    )
    response = await auth_app.patch(
        f"/wkc/{challenge.id}",
        json={
            "title": "changed",
            "description": "this is a test",
            "examples": "x = 1",
            "rules": "work",
            "created_by": "sarzzz",
            "difficulty": "easy",
        },
        headers={"authorization": auth_app.token},
    )
    assert response.status_code == 200
    assert response.content_type == "application/json"
    guild = await Challenge.fetch(
        challenge.id
    )  # guild was updated in db, need to fetch again
    assert (await response.json) == challenge_to_dict(guild)


@pytest.mark.asyncio
@pytest.mark.db
async def test_delete_weekly_challenge(auth_app: QuartClient, db):
    challenge = await Challenge.create(
        id="1",
        title="test",
        description="this is a test",
        examples="x = 1",
        rules="work",
        created_by="sarzz",
        difficulty="easy",
    )
    response = await auth_app.delete(
        f"/wkc/{challenge.id}", headers={"authorization": auth_app.token}
    )
    assert response.status_code == 204
    guild = await Challenge.fetch(
        challenge.id
    )  # guild was deleted in db, need to fetch again
    assert guild is None
