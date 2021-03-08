from quart import request, jsonify, Response
from typing import Optional, Union
import time

from api.models import Role, Permission, UserRole
from .. import bp

import utils


request: utils.Request


@bp.route("", methods=["GET"])
@utils.auth_required
async def paginate_roles():
    """GET `Role` objects by bulk.

    Query parameters:

     name:          Only fetch roles with this name.
     page:          Pagination page.
     limit:         max number of records to return.
    """
    start = time.perf_counter()

    qs = {"name": request.args.get("name")}

    try:
        page = int(request.args.get("page", "0"))
        limit = int(request.args.get("limit", "100"))
    except ValueError as e:
        invalid_arg = str(e).split()[-1]
        return (
            jsonify(
                error="Bad Request", message="Invalid literal for int, %s" % invalid_arg
            ),
            400,
        )

    query = """
    SELECT json_agg(json_build_object(
        'name', r.name,
        'base', r.base,
        'id', r.id::TEXT,
        'color', r.color,
        'position', r.position,
        'permissions', r.permissions::TEXT
    ))
    FROM roles r"""

    checks = []
    args = []
    i = 1

    for key, val in qs.items():
        if val is not None:
            checks.append("%s = $%s" % (key, i))
            args.append(val),
            i += 1

    if checks:
        query += "\n    WHERE\n        " + "\n    AND\n        ".join(checks)

    limit = max(min(100, limit), 1)  # Restrict to minimum 1, maximum 100.
    offset = page * limit

    query += "\n    LIMIT %s OFFSET %s" % (limit, offset)

    records = await Role.pool.fetchval(query, *args)
    records = records or []

    return jsonify(
        page=page, limit=limit, roles=records, time=time.perf_counter() - start
    )


@bp.route("/<int:role_id>", methods=["GET"])
@utils.auth_required
async def fetch_role(role_id: int):
    """Fetch a role by id."""
    query = """
    SELECT
        id::TEXT,
        name,
        position,
        color,
        permissions::TEXT,
        base
    FROM roles
    WHERE id = $1
    """

    record = await Role.pool.fetchrow(query, role_id)

    if record is None:
        return jsonify(error="NotFound", message="No role with that id found."), 404

    return jsonify(**dict(record)), 200


@bp.route("", methods=["POST"])
@utils.auth_required
@utils.expects_data(
    name=Optional[str],
    position=Optional[int],
    color=Optional[int],
    permissions=Optional[Union[int, str]],
)
@utils.requires_perms(Permission.MANAGE_ROLES)
async def create_role(
    name: Optional[str] = "new role",
    color: Optional[int] = 0,
    permissions: Optional[Union[str, int]] = 0,
):
    """Create a new role."""
    role = await Role.create(name=name, color=color, permissions=permissions)

    return (
        jsonify(
            name=role.name,
            base=role.base,
            id=str(role.id),
            color=role.color,
            position=role.position,
            permissions=str(role.permissions),
        ),
        201,
        {"Location": "/roles/%s" % role.id},
    )


@bp.route("/<int:role_id>", methods=["DELETE"])
@utils.auth_required
@utils.requires_perms(Permission.MANAGE_ROLES)
async def delete_role(role_id: int):
    """Delete a role by id."""
    await Role.delete(role_id, user_id=request.user_id)
    return Response("", status=204)


@bp.route("/<int:role_id>", methods=["PATCH"])
@utils.auth_required
@utils.expects_data(
    name=Optional[str],
    position=Optional[int],
    color=Optional[int],
    permissions=Optional[Union[int, str]],
)
@utils.requires_perms(Permission.MANAGE_ROLES)
async def update_role(role_id: int, **data):
    """Update a role by id."""
    role = await Role.fetch(id=role_id)

    if role is None:
        return jsonify(error="NotFound", message="No role with that id found."), 404

    if (perms := data.get("permissions")) is not None:
        data["permissions"] = int(perms)

    await role.update(user_id=request.user_id, **data)

    return (
        jsonify(
            name=role.name,
            color=role.color,
            position=role.position,
            permissions=str(role.permissions),
        ),
        200,
    )


@bp.route("/<int:role_id>/members/<int:member_id>", methods=["PUT"])
@utils.auth_required
@utils.requires_perms(Permission.MANAGE_ROLES)
async def add_role_member(role_id: int, member_id: int):
    """Add a role to a user."""
    await UserRole.insert(member_id, role_id, user_id=request.user_id)
    return Response("", status=201)


@bp.route("/<int:role_id>/members/<int:member_id>", methods=["DELETE"])
@utils.auth_required
@utils.requires_perms(Permission.MANAGE_ROLES)
async def remove_role_member(role_id: int, member_id: int):
    """Remove a role from a user."""
    await UserRole.delete(member_id, role_id, user_id=request.user_id)
    return Response("", status=204)
