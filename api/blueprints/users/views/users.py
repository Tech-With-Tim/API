from quart import request, jsonify


from .. import bp
import utils


request: utils.Request


@bp.route("/", methods=["GET"])
async def bulk_get_users():
    """GET `User` objects by bulk.

    TODO: Restrict access.

    Query parameters:
     username: Only fetch users with this username.
    """
    type = request.args.get("type")
    username = request.args.get("username")
    discriminator = request.args.get("discriminator")

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

    return jsonify(type, username, discriminator, page, limit), 501
