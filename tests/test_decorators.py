from api import app as quart_app

from quart.testing import QuartClient
from quart import jsonify
import pytest


import utils


@quart_app.route("/app_only")
@utils.app_only
async def endpoint1():
    return jsonify(status="OK")


@quart_app.route("/auth_required")
@utils.auth_required
async def endpoint2():
    return jsonify(status="OK")


@pytest.fixture(name="app")
def _test_app() -> QuartClient:
    return quart_app.test_client()


# TODO: Add tests where we provide authorization and test user type.
#  Database and env values are required for this.


@pytest.mark.asyncio
async def test_app_only_401(app: QuartClient):
    response = await app.get("/app_only")

    assert response.status_code == 401
    assert response.mimetype == "application/json"
    assert (await response.json) == {
        "error": "Unauthorized",
        "message": "No permission -- see authorization schemes",
    }


@pytest.mark.asyncio
async def test_auth_required_401(app: QuartClient):
    response = await app.get("/auth_required")

    assert response.status_code == 401
    assert response.mimetype == "application/json"
    assert (await response.json) == {
        "error": "Unauthorized",
        "message": "No permission -- see authorization schemes",
    }
