from launch import load_env

from quart.testing import QuartClient
import pytest


load_env(fp="./local.env", args=("SECRET_KEY",), exit_on_missing=False)


@pytest.mark.asyncio
async def test_users_no_auth(app: QuartClient):
    response = await app.get("/users")

    assert response.status_code == 401
    assert response.mimetype == "application/json"
    assert (await response.json) == {
        "error": "Unauthorized",
        "message": "No permission -- see authorization schemes",
    }


@pytest.mark.asyncio
async def test_users_me_no_auth(app: QuartClient):
    response = await app.get("/users/@me")

    assert response.status_code == 401
    assert response.mimetype == "application/json"
    assert (await response.json) == {
        "error": "Unauthorized",
        "message": "No permission -- see authorization schemes",
    }


@pytest.mark.asyncio
@pytest.mark.db
async def test_users_me(auth_app: QuartClient):
    response = await auth_app.get(
        "/users/@me", headers={"Authorization": auth_app.token}
    )

    assert response.status_code == 200
    assert response.mimetype == "application/json"
    assert (await response.json) == {
        "avatar": None,
        "discriminator": "0000",
        "id": "1",
        "type": "APP",
        "username": "test",
    }


@pytest.mark.asyncio
@pytest.mark.db
async def test_users_specific_user(auth_app: QuartClient):
    response = await auth_app.get(
        f"/users/{auth_app.user.id}", headers={"Authorization": auth_app.token}
    )

    assert response.status_code == 200
    assert response.mimetype == "application/json"
    assert (await response.json) == {
        "avatar": None,
        "discriminator": "0000",
        "id": "1",
        "type": "APP",
        "username": "test",
    }


@pytest.mark.asyncio
@pytest.mark.db
async def test_users_invalid_specific_user(auth_app: QuartClient):
    response = await auth_app.get(
        "/users/100", headers={"Authorization": auth_app.token}
    )

    assert response.status_code == 400
    assert response.mimetype == "application/json"
    assert (await response.json) == {
        "error": "NotFound",
        "message": "Could not find the requested user in our database.",
    }


@pytest.mark.asyncio
@pytest.mark.db
async def test_users_bulk(auth_app: QuartClient):
    response = await auth_app.get("/users", headers={"Authorization": auth_app.token})

    assert response.status_code == 200
    assert response.mimetype == "application/json"

    data = await response.json

    time = data.pop("time")

    assert (await response.json) == {
        "limit": 100,
        "page": 0,
        "users": [
            {
                "avatar": None,
                "discriminator": "0000",
                "id": "1",
                "type": "APP",
                "username": "test",
            }
        ],
    }

    assert isinstance(time, float)
