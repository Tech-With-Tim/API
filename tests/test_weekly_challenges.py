from api.models import Challenge

from quart.testing import QuartClient
import pytest


def challenge_to_dict(challenge: Challenge) -> dict:
    return {
        "id": challenge.id,
        "title": challenge.title,
        "description": str(challenge.description),
        "examples": challenge.examples,
        "rules": challenge.rules,
        "difficulty": challenge.difficulty,
    }


@pytest.fixture(name="challenge", scope="session")
async def _challenge():
    return await Challenge.create(
        id=1,
        title="test",
        description="this is a test",
        examples="x = 1",
        rules="work",
        created_by=1,
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
                "title": "test",
                "description": "this is a test",
                "examples": "x = 1",
                "rules": "work",
                "difficulty": "easy",
            },
            201,
        ),
        (
            {
                "id": 2,
                "title": "test",
                "description": "this is a test",
                "examples": "x = 1",
                "rules": "work",
                "difficulty": "easy",
            },
            201,
        ),
        (
            {"id": 3, "title": "c", "description": "xx"},
            400,
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
        "/challenges/weekly", json=data, headers={"authorization": auth_app.token}
    )
    assert response.content_type == "application/json"
    assert response.status_code == status_code
    if status_code == 201:
        assert (await response.json) == {
            n: str(data.get(n, "")) or 1
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


@pytest.mark.asyncio
@pytest.mark.db
async def test_get_weekly_challenge(app: QuartClient, db, challenge: Challenge):
    response = await app.get("/challenges/weekly/1")
    assert response.status_code == 200
    assert response.content_type == "application/json"
    assert (await response.json) == {
        "id": "1",
        "title": "test",
        "description": "this is a test",
        "examples": "x = 1",
        "rules": "work",
        "created_by": "1",
        "difficulty": "easy",
    }


@pytest.mark.asyncio
@pytest.mark.db
async def test_patch_challenge(auth_app: QuartClient, db):
    response = await auth_app.patch(
        "/challenges/weekly/1",
        json={
            "title": "changed",
            "description": "this is a test",
            "examples": "x = 1",
            "rules": "work",
            "difficulty": "easy",
        },
        headers={"authorization": auth_app.token},
    )
    assert response.status_code == 200


@pytest.mark.asyncio
@pytest.mark.db
async def test_delete_weekly_challenge(auth_app: QuartClient, db):
    response = await auth_app.delete(
        "/challenges/weekly/1", headers={"authorization": auth_app.token}
    )
    assert response.status_code == 200
    challenge = await Challenge.fetch(
        "1"
    )  # challenge was deleted in db, need to fetch again
    assert challenge is None
