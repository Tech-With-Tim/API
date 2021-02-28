# from api.blueprints.auth.views.tokens import get_redirect, SCOPES
from api import app as quart_app
from launch import load_env

from quart.testing import QuartClient
import pytest


load_env(fp="./local.env", args=("SECRET_KEY",), exit_on_missing=False)


@pytest.fixture(name="app")
def _test_app() -> QuartClient:
    return quart_app.test_client()


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


# TODO: tests for User endpoints.
#  Needs database before functioning.
