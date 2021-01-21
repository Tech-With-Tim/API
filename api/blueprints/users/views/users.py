from quart import request, jsonify

from api.models import User
from .. import bp
import utils


request: utils.Request


@bp.route("/", methods=["GET"])
@utils.app_only
async def bulk_get_users():
    """GET `User` objects by bulk.

    Query parameters:
     type:          Only fetch users of this type.
     username:      Only fetch users with this username.
     discriminator: Only fetch users with this discriminator
     page:          Pagination page.
     limit:         max number of records to return.
    """

    qs = {
        "type": request.args.get("type"),
        "username": request.args.get("username"),
        "discriminator": request.args.get("discriminator"),
    }

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
        'id', u.id::TEXT,
        'username', u.username,
        'discriminator', u.discriminator,
        'avatar', u.avatar,
        'type', u.type
    ))
    FROM users u"""

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

    records = await User.pool.fetchval(query, *args)
    records = records or []

    return jsonify(records)
