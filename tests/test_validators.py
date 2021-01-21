from api import app as quart_app

from quart.testing import QuartClient
from quart import jsonify
import typing
import pytest


import utils


@quart_app.route("/testing", methods=["POST"])
@utils.expects_data(
    name=str, id=typing.Union[str, int], type=typing.Literal["ONE", "TWO"]
)
async def endpoint(
    name: str, id: typing.Union[str, int], type: typing.Literal["ONE", "TWO"]
):
    return jsonify(name=name, id=id, type=type)


@pytest.fixture(name="app")
def _test_app() -> QuartClient:
    return quart_app.test_client()


@pytest.mark.asyncio
async def test_validator_no_data(app: QuartClient):
    response = await app.post("/testing")

    assert response.status_code == 400
    assert response.mimetype == "application/json"
    assert (await response.json) == {
        "error": "Bad Request",
        "message": "No json data provided.",
    }


@pytest.mark.asyncio
async def test_validator_empty_data(app: QuartClient):
    response = await app.post("/testing", json={})

    assert response.status_code == 400
    assert response.mimetype == "application/json"
    assert (await response.json) == {
        "data": ["name", "id", "type"],
        "error": "Bad Request",
        "message": "Missing keyword arguments.",
    }


@pytest.mark.asyncio
async def test_validator_invalid_data(app: QuartClient):
    response = await app.post("/testing", json={"name": 5, "id": 1.0, "type": "FOO"})

    assert response.status_code == 400
    assert response.mimetype == "application/json"

    assert (await response.json) == {
        "data": {
            "id": "Expected argument of type `Union[str, int]`, got `float`",
            "name": "Expected argument of type `str`, got `int`",
            "type": "Parameter needs to be one of Literal['ONE', 'TWO']",
        },
        "error": "Bad Request",
        "message": "JSON Validation failed.",
    }


@pytest.mark.asyncio
async def test_validator_valid_data(app: QuartClient):
    data = {"name": "Sylte", "id": "1", "type": "ONE"}

    response = await app.post("/testing", json=data)

    assert response.status_code == 200
    assert response.mimetype == "application/json"
    assert (await response.json) == data
