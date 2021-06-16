from fastapi.testclient import TestClient

from api import app

client = TestClient(app)


def test_read_index_status_code():
    response = client.get("/")
    assert response.status_code == 200


def test_read_index_body():
    response = client.get("/")
    assert response.json() == {"msg": "Hello World"}
