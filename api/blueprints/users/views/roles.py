from quart import request, jsonify
import time

from api.models import User
from .. import bp
import utils

request: utils.Request


@bp.route("/<int:user_id>/roles", methods=["GET"])
@utils.auth_required
async def fetch_user_roles(user_id: int):
    """Fetch the specific users roles"""
    query = """
        SELECT json_agg(json_build_object(
        'name', r.name,
        'base', r.base,
        'id', r.id::TEXT,
        'color', r.color,
        'position', r.position,
        'permissions', r.permissions::TEXT
        ))
        FROM roles r WHERE r.id IN (
            SELECT ur.role_id FROM userroles WHERE ur.user_id = $1
        )
    """
    record = await User.pool.fetchval(query, user_id)
    return jsonify(roles=record)
