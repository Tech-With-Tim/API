from typing import Optional

from quart import request, jsonify, Response

from api.models import Role, Permission, UserRole
from .. import bp

import utils

request: utils.Request


@bp.route("/<int:role_id>/", methods=["GET"])
@utils.auth_required
async def get_role(role_id: int):
    role = await Role.fetch_or_404(role_id)

    return jsonify(role.to_dict())


@bp.route("/", methods=["POST"])
@utils.auth_required
@utils.expects_data(
    name=Optional[str],
    position=Optional[int],
    color=Optional[int],
    permissions=Optional[int],
)
@utils.requires_perms(Permission.MANAGE_ROLES)
async def create_role(
    name: Optional[str] = "new role",
    color: Optional[int] = 0,
    permissions: Optional[int] = 0,
):
    role = await Role.create(name, color, permissions)

    return (jsonify(role.to_dict()), 201, {"Location": "/roles/%s" % role.id})


@bp.route("/<int:role_id>/", methods=["DELETE"])
@utils.auth_required
@utils.requires_perms(Permission.MANAGE_ROLES)
async def delete_role(role_id: int):
    await Role.delete(role_id, user_id=request.user_id)
    return Response("", status=204)


@bp.route("/<int:role_id>/", methods=["PATCH"])
@utils.auth_required
@utils.expects_data(
    name=Optional[str],
    position=Optional[int],
    color=Optional[int],
    permissions=Optional[int],
)
@utils.requires_perms(Permission.MANAGE_ROLES)
async def update_role(role_id: int, **data):
    role = await Role.fetch_or_404(role_id)
    await role.update(user_id=request.user_id, **data)

    return (jsonify(role.to_dict()), 200)


@bp.route("/<int:role_id>/members/<int:member_id>/", methods=["PUT"])
@utils.auth_required
@utils.requires_perms(Permission.MANAGE_ROLES)
async def add_member(role_id: int, member_id: int):
    await UserRole.insert(member_id, role_id, user_id=request.user_id)
    return Response("", status=201)


@bp.route("/<int:role_id>/members/<int:member_id>/", methods=["DELETE"])
@utils.auth_required
@utils.requires_perms(Permission.MANAGE_ROLES)
async def remove_member(role_id: int, member_id: int):
    await UserRole.delete(member_id, role_id, user_id=request.user_id)
    return Response("", status=204)
