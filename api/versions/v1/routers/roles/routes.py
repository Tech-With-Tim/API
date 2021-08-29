import utils

from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query

from api.models import Role
from api.access_token import access_token
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
async def create_role(body: NewRoleBody, token: str = Depends(access_token)):
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
    record = await Role.pool.fetchrow(query, body.name, body.color, body.permissions)

    return dict(record)


@router.patch("/{id}", tags=["roles"])
async def update_role(
    id: int, body: UpdateRoleBody, token: str = Depends(access_token)
):
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

    top_role = max(records, key=lambda record: record["position"])
    if (
        not utils.has_permission(user_permissions, ManageRoles())
        or top_role["position"] >= role.position
    ):
        raise HTTPException(403, "Missing Permissions")

    data = body.dict()
    if not utils.has_permission(user_permissions, data["permissions"]):
        raise HTTPException(403, "Missing Permissions")

    if (position := data.pop("position")) != object and position != role.position:
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

    new_data = list(filter(lambda key: data[key] != object, data))
    if new_data:
        query = "UPDATE ROLES SET "
        query += ", ".join("%s = %d" % (key, i) for i, key in enumerate(new_data, 2))
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

    top_role = max(records, key=lambda record: record["position"])
    if (
        not utils.has_permission(user_permissions, ManageRoles())
        or top_role["position"] >= role.position
    ):
        raise HTTPException(403, "Missing Permissions")

    query = """
        WITH deleted AS (
            DELETE FROM roles r
                WHERE r.id = $1
                RETURNING r.position
        ),
             to_update AS (
                 SELECT r.id
                 FROM roles r
                 WHERE r.position > (SELECT position FROM deleted)
             ),
             updated AS (
                 UPDATE roles r SET position = r.position - 1
                     WHERE r.id IN (SELECT id FROM to_update)
             )
        SELECT 1;
    """
    await Role.pool.execute(query, id)

    return utils.JSONResponse(status_code=204)
