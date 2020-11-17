from quart import current_app, Response, request, jsonify

import time

from utils import Request, auth_required, expects_data
from .. import blueprint

from db.models import User

request: Request


@blueprint.route("/users", methods=["GET"])
# @auth_required - Disabled for testing reasons.
async def bulk_get_users() -> Response:
    """
    GET `User` objects by bulk.

    TODO: Restrict access.

    TODO: Add different orderings:
            - by Username
            - by ID (user age)

    TODO: Add pagination.
            - `x` users per page
            - Selecting page `x`
            - Selecting users from index `x -> y` depending on ordering.
    """
    start = time.perf_counter()

    query = "SELECT * FROM users;"
    records = await current_app.db.fetch(query)

    return jsonify(
        {
            "count": len(records),
            "time_taken": time.perf_counter() - start,
            "users": [dict(record) for record in records],
        }
    )


@blueprint.route("/users", methods=["POST"])
@expects_data(
    id=int,
    username=str,
    discriminator=(str, int),
    avatar=(str, type(None)),
    xp=int,
    type=str,
    coins=(float, int),
    verified=bool,
)
# @auth_required - Disabled for testing reasons.
async def create_user(data: dict):
    """
    Create a User object.

    Returns status 202 if a new user was not created, 201 if a new user was created.

    TODO: Restrict access.
    """

    type = data["type"].upper()

    if type not in User.TYPES.__members__:
        return (
            jsonify(
                {
                    "error": "400 Bad Request",
                    "data": {
                        "type": "Bad User type -> Expected one of `USER, BOT, APP`, got {}".format(
                            type
                        )
                    },
                }
            ),
            400,
        )

    user = User(
        id=data["id"],
        username=data["username"],
        discriminator=str(data["discriminator"]),
        avatar=data["avatar"],
        xp=max(0, data["xp"]),
        type=type,
        coins=float(max(0, data["coins"])),
        verified=data["verified"],
    )
    created = await user.create()

    print(created)

    return Response("", status=202 - int(created))


@blueprint.route("/users/<int:id>")
# @auth_required - Disabled for testing reasons.
async def get_specific_user(id):
    """
    Returns a User object for a given user ID.

    TODO: Restrict access.
    """
    query = "SELECT * FROM users WHERE id = $1"
    record = await current_app.db.fetchrow(query, id)

    if record is None:
        return (
            jsonify(
                {
                    "error": "404 Not Found - The requested user could not be found in our database."
                }
            ),
            404,
        )

    user = User(**record)
    return jsonify(user.as_dict())


@blueprint.route("/users/@me", methods=["GET"])
@auth_required
async def get_user() -> Response:
    """
    Returns the `User` object of the requesters account.

    Requires Token authentication.
    """
    return jsonify(request.user.as_dict())
