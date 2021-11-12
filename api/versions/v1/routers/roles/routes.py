import utils
import asyncpg

from typing import List, Union
from fastapi import APIRouter, HTTPException, Response

from api.models import Role, UserRole
from api.dependencies import has_permissions
from api.models.permissions import ManageRoles
from api.versions.v1.routers.roles.models import (
    NewRoleBody,
    RoleResponse,
    UpdateRoleBody,
    DetailedRoleResponse,
)


router = APIRouter(prefix="/roles")


@router.get("", tags=["roles"], response_model=List[RoleResponse])
async def fetch_all_roles():
    """Fetch all roles"""

    query = """
        SELECT *,
               r.id::TEXT
          FROM roles r
    """
    records = await Role.pool.fetch(query)

    return [dict(record) for record in records]


@router.get(
    "/{id}",
    tags=["roles"],
    response_model=DetailedRoleResponse,
    responses={
        404: {"description": "Role not found"},
    },
)
async def fetch_role(id: int):
    """Fetch a role by its id"""

    query = """
        SELECT *,
               id::TEXT,
               COALESCE(
                  (
                      SELECT json_agg(ur.user_id::TEXT)
                       FROM userroles ur
                      WHERE ur.role_id = r.id
                  ), '[]'
               ) members
         FROM roles r
        WHERE r.id = $1
    """
    record = await Role.pool.fetchrow(query, id)

    if not record:
        raise HTTPException(404, "Role not found")

    record = dict(record)
    if record["color"]:
        record["color"] = int(record["color"].as_hex()[1:], 16)
    return record


@router.post(
    "",
    tags=["roles"],
    response_model=RoleResponse,
    responses={
        201: {"description": "Role Created Successfully"},
        401: {"description": "Unauthorized"},
        403: {"description": "Missing Permissions"},
        409: {"description": "Role with that name already exists"},
    },
    status_code=201,
)
async def create_role(body: NewRoleBody, roles=has_permissions([ManageRoles()])):
    # Check if the user has administrator permission or all the permissions provided in the role
    user_permissions = 0
    for role in roles:
        user_permissions |= role.permissions

    if not utils.has_permission(user_permissions, body.permissions):
        raise HTTPException(403, "Missing Permissions")

    query = """
        INSERT INTO roles (id, name, color, permissions, position)
            VALUES (create_snowflake(), $1, $2, $3, (SELECT COUNT(*) FROM roles) + 1)
            RETURNING *;
    """

    try:
        record = await Role.pool.fetchrow(
            query, body.name, int(body.color.as_hex()[1:], 16), body.permissions
        )
    except asyncpg.exceptions.UniqueViolationError:
        raise HTTPException(409, "Role with that name already exists")

    return utils.JSONResponse(status_code=201, content=dict(record))


@router.patch(
    "/{id}",
    tags=["roles"],
    responses={
        204: {"description": "Role Updated Successfully"},
        401: {"description": "Unauthorized"},
        403: {"description": "Missing Permissions"},
        404: {"description": "Role not found"},
        409: {"description": "Role with that name already exists"},
    },
    status_code=204,
)
async def update_role(
    id: int,
    body: UpdateRoleBody,
    roles=has_permissions([ManageRoles()]),
):
    if body.color:
        body.color = int(body.color.as_hex()[1:], 16)

    role = await Role.fetch(id)
    if not role:
        raise HTTPException(404, "Role Not Found")

    # Check if the user has administrator permission or all the permissions provided in the role
    user_permissions = 0
    for r in roles:
        user_permissions |= r.permissions

    top_role = min(roles, key=lambda role: role.position)
    if top_role.position >= role.position:
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
        if position <= top_role.position:
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
        query = "UPDATE ROLESre SET "
        query += ", ".join("%s = $%d" % (key, i) for i, key in enumerate(data, 2))
        query += " WHERE id = $1"

        await Role.pool.execute(query, id, *data.values())

    return Response(status_code=204, content="")


@router.delete(
    "/{id}",
    tags=["roles"],
    responses={
        204: {"description": "Role Updated Successfully"},
        401: {"description": "Unauthorized"},
        403: {"description": "Missing Permissions"},
        404: {"description": "Role not found"},
    },
    status_code=204,
)
async def delete_role(id: int, roles=has_permissions([ManageRoles()])):
    role = await Role.fetch(id)
    if not role:
        raise HTTPException(404, "Role Not Found")

    top_role = min(roles, key=lambda role: role.position)
    if top_role.position >= role.position:
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

    return Response(status_code=204, content="")


@router.put(
    "/{role_id}/members/{member_id}",
    tags=["roles"],
    responses={
        204: {"description": "Role assigned to member"},
        401: {"description": "Unauthorized"},
        403: {"description": "Missing Permissions"},
        404: {"description": "Role or member not found"},
        409: {"description": "User already has the role"},
    },
    status_code=204,
)
async def add_member_to_role(
    role_id: int, member_id: int, roles=has_permissions([ManageRoles()])
) -> Union[Response, utils.JSONResponse]:
    role = await Role.fetch(role_id)
    if not role:
        raise HTTPException(404, "Role Not Found")

    top_role = min(roles, key=lambda role: role.position)
    if top_role.position >= role.position:
        raise HTTPException(403, "Missing Permissions")

    try:
        await UserRole.create(member_id, role_id)
    except asyncpg.exceptions.UniqueViolationError:
        raise HTTPException(409, "User already has the role")
    except asyncpg.exceptions.ForeignKeyViolationError:
        raise HTTPException(404, "Member not found")

    return Response(status_code=204, content="")


@router.delete(
    "/{role_id}/members/{member_id}",
    tags=["roles"],
    responses={
        204: {"description": "Role removed from member"},
        401: {"description": "Unauthorized"},
        403: {"description": "Missing Permissions"},
        404: {"description": "Role not found"},
    },
    status_code=204,
)
async def remove_member_from_role(
    role_id: int, member_id: int, roles=has_permissions([ManageRoles()])
) -> Union[Response, utils.JSONResponse]:
    role = await Role.fetch(role_id)
    if not role:
        raise HTTPException(404, "Role Not Found")

    top_role = min(roles, key=lambda role: role.position)
    if top_role.position >= role.position:
        raise HTTPException(403, "Missing Permissions")

    await UserRole.delete(member_id, role_id)

    return Response(status_code=204, content="")
