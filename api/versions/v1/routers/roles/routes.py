import utils
import asyncpg

from typing import List, Union
from fastapi import APIRouter, Depends, HTTPException, Query, Response

from api.models import Role, UserRole
from api.dependencies import access_token
from api.models.permissions import ManageRoles
from api.versions.v1.routers.roles.models import (
    NewRoleBody,
    RoleResponse,
    UpdateRoleBody,
    DetailedRoleResponse,
)


router = APIRouter(prefix="/roles")


@router.get("", tags=["roles"], response_model=List[RoleResponse])
async def fetch_all_roles(
    limit: int = Query(None),
    offset: int = Query(None),
):
    query = """
        SELECT
            *, id::TEXT
        FROM roles
        LIMIT $1
        OFFSET $2;
    """
    records = await Role.pool.fetch(query, limit, offset)

    return [dict(record) for record in records]


@router.get("/{id}", tags=["roles"], response_model=DetailedRoleResponse)
async def fetch_role(id: int):
    query = """
        SELECT
            *,
            id::TEXT,
            COALESCE(
                (
                    SELECT
                        json_agg(user_id::TEXT)
                    FROM userroles ur
                    WHERE ur.role_id = $1
                ), '[]'
            ) members
        FROM roles r
        WHERE r.id = $1;
    """
    record = await Role.pool.fetchrow(query, id)

    return dict(record)


@router.post("", tags=["roles"], response_model=RoleResponse)
async def create_role(body: NewRoleBody, token=Depends(access_token)):
    query = """
        WITH user_roles AS (
            SELECT role_id FROM userroles WHERE user_id = $1
        )
            SELECT permissions FROM roles WHERE id IN (SELECT * FROM user_roles);
    """

    records = await Role.pool.fetch(query, token["uid"])
    if not records:
        raise HTTPException(403, "Missing Permissions")

    user_permissions = 0
    for record in records:
        user_permissions |= record["permissions"]

    if not utils.has_permission(
        user_permissions, body.permissions
    ) or not utils.has_permission(user_permissions, ManageRoles()):
        raise HTTPException(403, "Missing Permissions")

    query = """
        INSERT INTO roles (id, name, color, permissions, position)
            VALUES (create_snowflake(), $1, $2, $3, (SELECT COUNT(*) FROM roles) + 1)
            RETURNING *;
    """
    try:
        record = await Role.pool.fetchrow(
            query, body.name, body.color, body.permissions
        )
    except asyncpg.exceptions.UniqueViolationError:
        raise HTTPException(409, "Role with that name already exists")

    return utils.JSONResponse(status_code=201, content=dict(record))


@router.patch("/{id}", tags=["roles"])
async def update_role(id: int, body: UpdateRoleBody, token=Depends(access_token)):
    role = await Role.fetch(id)
    if not role:
        raise HTTPException(404, "Role Not Found")

    query = """
        WITH user_roles AS (
            SELECT role_id FROM userroles WHERE user_id = $1
        )
            SELECT position, permissions FROM roles WHERE id IN (SELECT * FROM user_roles);
    """

    records = await Role.pool.fetch(query, token["uid"])
    if not records:
        raise HTTPException(403, "Missing Permissions")

    user_permissions = 0
    for record in records:
        user_permissions |= record["permissions"]

    top_role = min(records, key=lambda record: record["position"])
    if (
        not utils.has_permission(user_permissions, ManageRoles())
        or top_role["position"] >= role.position
    ):
        raise HTTPException(403, "Missing Permissions")

    data = body.dict(exclude_unset=True)
    if not utils.has_permission(user_permissions, body.permissions):
        raise HTTPException(403, "Missing Permissions")

    if name := data.get("name", None):
        record = await Role.pool.fetchrow("SELECT * FROM roles WHERE name = $1", name)

        if record:
            raise HTTPException(409, "Role with that name already exists")

    if (
        position := data.pop("position", None)
    ) is not None and position != role.position:
        if position <= top_role["position"]:
            raise HTTPException(403, "Missing Permissions")

        if position > role.position:
            new_pos = position + 0.5
        else:
            new_pos = position - 0.5

        query = """
            UPDATE roles r SET position = $1
                WHERE r.id = $2;
        """
        await Role.pool.execute(query, new_pos, id)

        query = """
            WITH todo AS (
                SELECT r.id,
                    ROW_NUMBER() OVER (ORDER BY position) AS position
                FROM roles r
            )
            UPDATE roles r SET
                position = td.position
            FROM todo td
            WHERE r.id = td.id;
        """
        await Role.pool.execute(query)

    if data:
        query = "UPDATE ROLES SET "
        query += ", ".join("%s = $%d" % (key, i) for i, key in enumerate(data, 2))
        query += " WHERE id = $1"

        await Role.pool.execute(query, id, *data.values())

    return utils.JSONResponse(status_code=204)


@router.delete("/{id}", tags=["roles"])
async def delete_role(id: int, token=Depends(access_token)):
    role = await Role.fetch(id)
    if not role:
        raise HTTPException(404, "Role Not Found")

    query = """
        WITH user_roles AS (
            SELECT role_id FROM userroles WHERE user_id = $1
        )
            SELECT position, permissions FROM roles WHERE id IN (SELECT * FROM user_roles);
    """

    records = await Role.pool.fetch(query, token["uid"])
    if not records:
        raise HTTPException(403, "Missing Permissions")

    user_permissions = 0
    for record in records:
        user_permissions |= record["permissions"]

    top_role = min(records, key=lambda record: record["position"])
    if (
        not utils.has_permission(user_permissions, ManageRoles())
        or top_role["position"] >= role.position
    ):
        raise HTTPException(403, "Missing Permissions")

    query = """
        WITH deleted AS (
            DELETE FROM roles r
                WHERE r.id = $1
                RETURNING r.id
        ),
             to_update AS (
                SELECT r.id,
                    ROW_NUMBER() OVER (ORDER BY r.position) AS position
                FROM roles r
                 WHERE r.id != (SELECT id FROM deleted)
             )
        UPDATE roles r SET
            position = tu.position
        FROM to_update tu
        WHERE r.id = tu.id
    """
    await Role.pool.execute(query, id)

    return utils.JSONResponse(status_code=204)


@router.put("/{role_id}/members/{member_id}", tags=["roles"])
async def add_member_to_role(
    role_id: int, member_id: int, token=Depends(access_token)
) -> Union[Response, utils.JSONResponse]:
    role = await Role.fetch(role_id)
    if not role:
        raise HTTPException(404, "Role Not Found")

    query = """
        WITH user_roles AS (
            SELECT role_id FROM userroles WHERE user_id = $1
        )
            SELECT position, permissions FROM roles WHERE id IN (SELECT * FROM user_roles);
    """

    records = await Role.pool.fetch(query, token["uid"])
    if not records:
        raise HTTPException(403, "Missing Permissions")

    user_permissions = 0
    for record in records:
        user_permissions |= record["permissions"]

    top_role = min(records, key=lambda record: record["position"])
    if (
        not utils.has_permission(user_permissions, ManageRoles())
        or top_role["position"] >= role.position
    ):
        raise HTTPException(403, "Missing Permissions")

    try:
        await UserRole.create(member_id, role_id)
    except asyncpg.exceptions.UniqueViolationError:
        raise HTTPException(409, "User already has the role")

    return Response(status_code=204, content="")


@router.delete("/{role_id}/members/{member_id}", tags=["roles"])
async def remove_member_from_role(
    role_id: int, member_id: int, token=Depends(access_token)
) -> Union[Response, utils.JSONResponse]:
    role = await Role.fetch(role_id)
    if not role:
        raise HTTPException(404, "Role Not Found")

    query = """
        WITH user_roles AS (
            SELECT role_id FROM userroles WHERE user_id = $1
        )
            SELECT position, permissions FROM roles WHERE id IN (SELECT * FROM user_roles);
    """

    records = await Role.pool.fetch(query, token["uid"])
    if not records:
        raise HTTPException(403, "Missing Permissions")

    user_permissions = 0
    for record in records:
        user_permissions |= record["permissions"]

    top_role = min(records, key=lambda record: record["position"])
    if (
        not utils.has_permission(user_permissions, ManageRoles())
        or top_role["position"] >= role.position
    ):
        raise HTTPException(403, "Missing Permissions")

    await UserRole.delete(member_id, role_id)

    return Response(status_code=204, content="")
