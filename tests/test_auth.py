from api.blueprints.auth.views.tokens import get_redirect, SCOPES
from launch import load_env

from quart.testing import QuartClient
import pytest


load_env(fp="./local.env", args=("DISCORD_CLIENT_ID",), exit_on_missing=False)


@pytest.mark.asyncio
async def test_auth_redirect_no_qs(app: QuartClient):
    response = await app.get("/auth/discord/redirect")
    correct_location = get_redirect(
        callback="http://localhost/auth/discord/callback",
        # app.get requests to localhost but `127.0.0.1` should be used in development.
        scopes=SCOPES,
    )
    assert response.headers["Location"] == correct_location
    assert response.mimetype == "text/html"
    assert response.status_code == 302


@pytest.mark.asyncio
async def test_auth_redirect_invalid_qs(app: QuartClient):
    response = await app.get("/auth/discord/redirect?callback=invalid")
    assert await response.json == {
        "error": "Bad Request",
        "message": "Not a well formed redirect URL.",
    }
    assert response.mimetype == "application/json"
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_auth_redirect_valid_qs(app: QuartClient):
    response = await app.get("/auth/discord/redirect?callback=http://test.com")
    correct_location = get_redirect(
        callback="http://test.com",
        scopes=SCOPES,
    )
    assert response.headers["Location"] == correct_location
    assert response.mimetype == "text/html"
    assert response.status_code == 302


@pytest.mark.asyncio
async def test_auth_callback_no_qs(app: QuartClient):
    response = await app.get("/auth/discord/callback")

    expected_status = 400 if app.app.debug else 405
    assert response.status_code == expected_status
    assert response.mimetype == "application/json"
