import pytest

from httpx import AsyncClient

from api.models import Role, UserRole
from api.models.permissions import ManageRoles


@pytest.fixture
async def manage_roles_role(db):
    query = """
        INSERT INTO roles (id, name, color, permissions, position)
            VALUES (create_snowflake(), $1, $2, $3, (SELECT COUNT(*) FROM roles) + 1)
            RETURNING *;
    """
    record = await Role.pool.fetchrow(query, "Roles Manager", 0x0, ManageRoles().value)
    yield Role(**record)
    await db.execute("DELETE FROM roles WHERE id = $1;", record["id"])


@pytest.mark.db
@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("data", "status"),
    [
        ({}, 422),
        ({"name": ""}, 422),
        ({"permissions": -1}, 422),
        ({"name": "test1", "color": 0xFFFFFFF}, 422),
        ({"name": "test1", "color": -0x000001}, 422),
        ({"name": "test2", "color": 0x000000, "permissions": 8}, 403),
        ({"name": "test2", "color": 0x000000, "permissions": 0}, 201),
        ({"name": "test2", "color": 0x000000, "permissions": 0}, 409),
    ],
)
async def test_role_create(
    app: AsyncClient, db, user, token, manage_roles_role, data, status
):
    try:
        await UserRole.create(user.id, manage_roles_role.id)
        res = await app.post(
            "/api/v1/roles", json=data, headers={"Authorization": token}
        )
        assert res.status_code == status
    finally:
        await db.execute(
            "DELETE FROM userroles WHERE role_id = $1 AND user_id = $2;",
            manage_roles_role.id,
            user.id,
        )
        if status == 409:
            await db.execute("DELETE FROM roles WHERE name = $1", data["name"])


@pytest.mark.db
@pytest.mark.asyncio
async def test_fetch_all_roles(app: AsyncClient):
    res = await app.get("/api/v1/roles")

    assert res.status_code == 200
    assert type(res.json()) == list


@pytest.mark.db
@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("request_data", "new_data", "status"),
    [
        ({}, {"name": "test update", "permissions": 0, "color": 0}, 204),
        ({"name": ""}, {"name": "test update", "permissions": 0, "color": 0}, 422),
        (
            {"permissions": -1},
            {"name": "test update", "permissions": 0, "color": 0},
            422,
        ),
        (
            {"color": 0xFFFFFFF},
            {"name": "test update", "permissions": 0, "color": 0},
            422,
        ),
        (
            {"color": -0x000001},
            {"name": "test update", "permissions": 0, "color": 0},
            422,
        ),
        (
            {"color": 0x5, "permissions": 8},
            {"name": "test update", "permissions": 0, "color": 0x0},
            403,
        ),
        (
            {"color": 0x5, "permissions": ManageRoles().value},
            {"name": "test update", "permissions": ManageRoles().value, "color": 0x5},
            204,
        ),
    ],
)
async def test_role_update(
    app: AsyncClient, db, user, token, manage_roles_role, request_data, new_data, status
):
    try:
        query = """
            INSERT INTO roles (id, name, color, permissions, position)
                VALUES (create_snowflake(), 'test update', 0, 0, (SELECT COUNT(*) FROM roles) + 1)
                RETURNING *;
        """
        role = Role(**await Role.pool.fetchrow(query))
        await UserRole.create(user.id, manage_roles_role.id)

        res = await app.patch(
            f"/api/v1/roles/{role.id}",
            json=request_data,
            headers={"Authorization": token},
        )

        assert res.status_code == status

        role = await Role.fetch(role.id)

        data = role.as_dict()
        data.pop("id")
        data.pop("position")

        assert data == new_data
    finally:
        await db.execute(
            "DELETE FROM userroles WHERE role_id = $1 AND user_id = $2;",
            manage_roles_role.id,
            user.id,
        )
        await db.execute("DELETE FROM roles WHERE id = $1", role.id)


@pytest.mark.db
@pytest.mark.asyncio
async def test_role_delete(app: AsyncClient, db, user, token, manage_roles_role):
    try:
        query = """
            INSERT INTO roles (id, name, color, permissions, position)
                VALUES (create_snowflake(), 'test delete', 0, 0, (SELECT COUNT(*) FROM roles) + 1)
                RETURNING *;
        """
        role = Role(**await Role.pool.fetchrow(query))
        await UserRole.create(user.id, manage_roles_role.id)

        res = await app.delete(
            f"/api/v1/roles/{role.id}",
            headers={"Authorization": token},
        )

        assert res.status_code == 204
    finally:
        await db.execute(
            "DELETE FROM userroles WHERE role_id = $1 AND user_id = $2;",
            manage_roles_role.id,
            user.id,
        )
        await db.execute("DELETE FROM roles WHERE id = $1", role.id)


@pytest.mark.db
@pytest.mark.asyncio
async def test_role_delete_high_position(
    app: AsyncClient, db, user, token, manage_roles_role
):
    try:
        query = """
            INSERT INTO roles (id, name, color, permissions, position)
                VALUES (create_snowflake(), 'test delete', 0, 0, 0)
                RETURNING *;
        """
        role = Role(**await Role.pool.fetchrow(query))
        await UserRole.create(user.id, manage_roles_role.id)

        res = await app.delete(
            f"/api/v1/roles/{role.id}",
            headers={"Authorization": token},
        )

        assert res.status_code == 403
    finally:
        await db.execute(
            "DELETE FROM userroles WHERE role_id = $1 AND user_id = $2;",
            manage_roles_role.id,
            user.id,
        )
        await db.execute("DELETE FROM roles WHERE id = $1", role.id)


@pytest.mark.db
@pytest.mark.asyncio
async def test_role_add(app: AsyncClient, db, user, token, manage_roles_role):
    try:
        query = """
            INSERT INTO roles (id, name, color, permissions, position)
                VALUES (create_snowflake(), 'test add', 0, 0, (SELECT COUNT(*) FROM roles) + 1)
                RETURNING *;
        """
        role = Role(**await Role.pool.fetchrow(query))
        await UserRole.create(user.id, manage_roles_role.id)

        res = await app.put(
            f"/api/v1/roles/{role.id}/members/{user.id}",
            headers={"Authorization": token},
        )

        assert res.status_code == 204
    finally:
        await db.execute(
            "DELETE FROM userroles WHERE role_id = $1 AND user_id = $2;",
            manage_roles_role.id,
            user.id,
        )
        await db.execute("DELETE FROM roles WHERE id = $1", role.id)


@pytest.mark.db
@pytest.mark.asyncio
async def test_role_add_high_position(
    app: AsyncClient, db, user, token, manage_roles_role
):
    try:
        query = """
            INSERT INTO roles (id, name, color, permissions, position)
                VALUES (create_snowflake(), 'test add', 0, 0, 0)
                RETURNING *;
        """
        role = Role(**await Role.pool.fetchrow(query))
        await UserRole.create(user.id, manage_roles_role.id)

        res = await app.put(
            f"/api/v1/roles/{role.id}/members/{user.id}",
            headers={"Authorization": token},
        )

        assert res.status_code == 403
    finally:
        await db.execute(
            "DELETE FROM userroles WHERE role_id = $1 AND user_id = $2;",
            manage_roles_role.id,
            user.id,
        )
        await db.execute("DELETE FROM roles WHERE id = $1", role.id)


@pytest.mark.db
@pytest.mark.asyncio
async def test_role_remove(app: AsyncClient, db, user, token, manage_roles_role):
    try:
        query = """
            INSERT INTO roles (id, name, color, permissions, position)
                VALUES (create_snowflake(), 'test remove', 0, 0, (SELECT COUNT(*) FROM roles) + 1)
                RETURNING *;
        """
        role = Role(**await Role.pool.fetchrow(query))
        await UserRole.create(user.id, manage_roles_role.id)

        res = await app.delete(
            f"/api/v1/roles/{role.id}/members/{user.id}",
            headers={"Authorization": token},
        )

        assert res.status_code == 204
    finally:
        await db.execute(
            "DELETE FROM userroles WHERE role_id = $1 AND user_id = $2;",
            manage_roles_role.id,
            user.id,
        )
        await db.execute("DELETE FROM roles WHERE id = $1", role.id)


@pytest.mark.db
@pytest.mark.asyncio
async def test_role_remove_high_position(
    app: AsyncClient, db, user, token, manage_roles_role
):
    try:
        query = """
            INSERT INTO roles (id, name, color, permissions, position)
                VALUES (create_snowflake(), 'test remove', 0, 0, 0)
                RETURNING *;
        """
        role = Role(**await Role.pool.fetchrow(query))
        await UserRole.create(user.id, manage_roles_role.id)

        res = await app.delete(
            f"/api/v1/roles/{role.id}/members/{user.id}",
            headers={"Authorization": token},
        )

        assert res.status_code == 403
    finally:
        await db.execute(
            "DELETE FROM userroles WHERE role_id = $1 AND user_id = $2;",
            manage_roles_role.id,
            user.id,
        )
        await db.execute("DELETE FROM roles WHERE id = $1", role.id)


@pytest.mark.db
@pytest.mark.asyncio
async def test_update_role_positions_up(
    app: AsyncClient, db, user, token, manage_roles_role
):
    try:
        roles = []
        # manage roles -> 1 -> 3 -> 2 -> 4
        role_names = ["1", "3", "2", "4"]
        for role_name in role_names:
            query = """
                INSERT INTO roles (id, name, color, permissions, position)
                    VALUES (create_snowflake(), $1, 0, 0, (SELECT COUNT(*) FROM roles) + 1)
                    RETURNING *;
            """
            role = Role(**await Role.pool.fetchrow(query, role_name))
            roles.append(role)

        await UserRole.create(user.id, manage_roles_role.id)

        res = await app.patch(
            f"/api/v1/roles/{roles[2].id}",
            json={"position": 3},
            headers={"Authorization": token},
        )
        assert res.status_code == 204

        res = await app.get("/api/v1/roles")
        new_roles = sorted(res.json(), key=lambda x: x["position"])

        for i, role in enumerate(new_roles, 1):
            assert (
                role["position"] == i
            )  # make sure roles are ordered with no missing positions

        for i in range(1, 5):
            assert new_roles[i]["name"] == str(i)
    finally:
        await db.execute(
            "DELETE FROM userroles WHERE role_id = $1 AND user_id = $2;",
            manage_roles_role.id,
            user.id,
        )
        for role in roles:
            await db.execute("DELETE FROM roles WHERE id = $1", role.id)


@pytest.mark.db
@pytest.mark.asyncio
async def test_update_role_positions_down(
    app: AsyncClient, db, user, token, manage_roles_role
):
    try:
        roles = []
        # manage roles -> 1 -> 3 -> 2 -> 4
        role_names = ["1", "3", "2", "4"]
        for role_name in role_names:
            query = """
                INSERT INTO roles (id, name, color, permissions, position)
                    VALUES (create_snowflake(), $1, 0, 0, (SELECT COUNT(*) FROM roles) + 1)
                    RETURNING *;
            """
            role = Role(**await Role.pool.fetchrow(query, role_name))
            roles.append(role)

        await UserRole.create(user.id, manage_roles_role.id)

        res = await app.patch(
            f"/api/v1/roles/{roles[1].id}",
            json={"position": 4},
            headers={"Authorization": token},
        )
        assert res.status_code == 204

        res = await app.get("/api/v1/roles")
        new_roles = sorted(res.json(), key=lambda x: x["position"])

        for i, role in enumerate(new_roles, 1):
            assert (
                role["position"] == i
            )  # make sure roles are ordered with no missing positions

        for i in range(1, 5):
            assert new_roles[i]["name"] == str(i)
    finally:
        await db.execute(
            "DELETE FROM userroles WHERE role_id = $1 AND user_id = $2;",
            manage_roles_role.id,
            user.id,
        )
        for i in roles:
            await db.execute("DELETE FROM roles WHERE id = $1", int(role["id"]))
