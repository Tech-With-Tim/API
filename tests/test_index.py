import pytest

from fastapi.testclient import TestClient


@pytest.mark.asyncio
def test_index(app: TestClient):
    response = app.get("/")
    assert response.json() == {"status": "ok"}
