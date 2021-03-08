from launch import load_env

from quart.testing import QuartClient
from typing import Dict
import pytest
import quart

from api.models import Role, UserRole


load_env(fp="./local.env", args=("SECRET_KEY",), exit_on_missing=False)


@pytest.fixture()
async def add_admin_role(auth_app, roles: Dict[str, Role]):
    # Grant auth_app administrator permission.
    try:
        await UserRole.insert(member_id=auth_app.user.id, role_id=roles["Admin"].id)
    except quart.exceptions.BadRequest:
        pass


@pytest.mark.asyncio
async def test_roles_no_auth(app: QuartClient):
    response = await app.get("/roles")

    assert response.status_code == 401
    assert response.mimetype == "application/json"
    assert (await response.json) == {
        "error": "Unauthorized",
        "message": "No permission -- see authorization schemes",
    }


@pytest.mark.db
@pytest.mark.asyncio
async def test_paginate_roles(auth_app, roles: Dict[str, Role]):
    response = await auth_app.get(f"/roles", headers={"Authorization": auth_app.token})

    assert response.status_code == 200
    assert response.mimetype == "application/json"

    solution = {"limit": 100, "page": 0, "roles": []}

    for role in roles.values():
        solution["roles"].append(
            {
                "id": str(role.id),
                "name": role.name,
                "base": role.base,
                "color": role.color,
                "position": role.position,
                "permissions": str(role.permissions),
            }
        )

    data = await response.json

    time = data.pop("time")

    assert data == solution

    assert isinstance(time, float)


@pytest.mark.db
@pytest.mark.asyncio
async def test_fetch_role(auth_app, roles: Dict[str, Role]):
    role = roles.get("Admin")

    response = await auth_app.get(
        f"/roles/{role.id}", headers={"Authorization": auth_app.token}
    )

    assert response.status_code == 200
    assert response.mimetype == "application/json"
    assert (await response.json) == {
        "name": role.name,
        "base": role.base,
        "id": str(role.id),
        "color": role.color,
        "position": role.position,
        "permissions": str(role.permissions),
    }


@pytest.mark.db
@pytest.mark.asyncio
async def test_create_default_role(auth_app, add_admin_role, roles: Dict[str, Role]):
    response = await auth_app.post(
        "/roles", json={}, headers={"Authorization": auth_app.token}
    )

    assert response.status_code == 201
    assert response.mimetype == "application/json"

    data = await response.json

    id = data.pop("id")

    assert data == {
        "name": "new role",
        "base": False,
        "color": 0xABCDEF,
        "position": len(roles) + 1,
        "permissions": "0",
    }

    assert isinstance(id, str)


@pytest.mark.db
@pytest.mark.asyncio
async def test_create_custom_role(auth_app, add_admin_role, roles: Dict[str, Role]):
    response = await auth_app.post(
        "/roles",
        json={"name": "custom role", "color": 0x123456, "permissions": 1},
        headers={"Authorization": auth_app.token},
    )

    assert response.status_code == 201
    assert response.mimetype == "application/json"

    data = await response.json

    id = data.pop("id")

    assert data == {
        "name": "custom role",
        "base": False,
        "color": 0x123456,
        "position": len(roles) + 1,
        "permissions": str(0b1),
    }

    assert isinstance(id, str)


@pytest.mark.db
@pytest.mark.asyncio
async def test_delete_role(auth_app, add_admin_role, roles: Dict[str, Role]):
    role = roles["new role"]

    response = await auth_app.delete(
        f"/roles/{role.id}", headers={"Authorization": auth_app.token}
    )

    assert response.status_code == 204
    assert response.mimetype == "text/html"


@pytest.mark.db
@pytest.mark.asyncio
async def test_update_role(auth_app, add_admin_role, roles: Dict[str, Role]):
    role = roles["custom role"]

    response = await auth_app.patch(
        f"/roles/{role.id}",
        json={"name": "role ala custom", "color": 0x111111},
        headers={"Authorization": auth_app.token},
    )

    assert response.status_code == 200
    assert response.mimetype == "application/json"
    assert (await response.json) == {
        "name": "role ala custom",
        "color": 0x111111,
        "position": role.position,
        "permissions": str(role.permissions),
    }
