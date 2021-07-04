import pytest
from httpx import AsyncClient
from pytest_mock import MockerFixture
from api.versions.v1.routers.auth.helpers import get_redirect, SCOPES


@pytest.mark.asyncio
async def test_redirect_default_code(app: AsyncClient):
    res = await app.get("/v1/auth/discord/redirect", allow_redirects=False)
    assert res.status_code == 307


@pytest.mark.asyncio
async def test_redirect_default_url(app: AsyncClient):
    res = await app.get("/v1/auth/discord/redirect")
    assert str(res.url) == get_redirect(
        callback="http://127.0.0.1/v1/auth/discord/callback",
        scopes=SCOPES,
    )


@pytest.mark.asyncio
async def test_redirect_invalid_callback(app: AsyncClient):
    res = await app.get("/v1/auth/discord/redirect?callback=okand")
    assert res.json() == {
        "error": "Bad Request",
        "message": "Not a well formed redirect URL.",
    }


@pytest.mark.asyncio
async def test_redirect_valid_callback_url(app: AsyncClient):
    res = await app.get("/v1/auth/discord/redirect?callback=https://twt.gg")
    assert str(res.url) == get_redirect(
        callback="https://twt.gg",
        scopes=SCOPES,
    )


@pytest.mark.asyncio
async def test_callback_discord_error(app: AsyncClient, mocker: MockerFixture):
    async def exchange_code(**kwargs):
        return {"error": "internal server error"}, 500

    mocker.patch("api.versions.v1.routers.auth.routes.exchange_code", new=exchange_code)

    res = await app.post(
        "/v1/auth/discord/callback",
        json={"code": "okand", "callback": "https://twt.gg"},
    )

    assert res.status_code == 502


@pytest.mark.asyncio
async def test_callback_invalid_code(app: AsyncClient, mocker: MockerFixture):
    async def exchange_code(**kwargs):
        return {"error": 'invalid "code" in request'}, 400

    mocker.patch("api.versions.v1.routers.auth.routes.exchange_code", new=exchange_code)
    res = await app.post(
        "/v1/auth/discord/callback",
        json={"code": "invalid", "callback": "https://twt.gg"},
    )

    assert res.json() == {
        "error": "Bad Request",
        "data": (await exchange_code())[0],
        "message": "Discord returned 400 status.",
    }


@pytest.mark.asyncio
@pytest.mark.db
async def test_callback_success(app: AsyncClient, db, mocker: MockerFixture):
    async def exchange_code(**kwargs):
        return {
            "expires_in": 69420,
            "access_token": "super_doper_secret_token",
            "refresh_token": "super_doper_doper_secret_token",
        }, 200

    async def get_user(**kwargs):
        return {
            "username": "M7MD",
            "discriminator": "1701",
            "id": 601173582516584602,
            "avatar": "135fa48ba8f26417c4b9818ae2e37aa0",
        }

    mocker.patch("api.versions.v1.routers.auth.routes.get_user", new=get_user)
    mocker.patch("api.versions.v1.routers.auth.routes.exchange_code", new=exchange_code)

    res = await app.post(
        "/v1/auth/discord/callback",
        json={"code": "invalid", "callback": "https://twt.gg"},
    )

    assert res.status_code == 200
