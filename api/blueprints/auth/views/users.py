from quart import current_app, Response, request, jsonify

from logging import getLogger

from .. import blueprint

from api.models import User
import utils

request: utils.Request
log = getLogger("/auth/users")


@blueprint.route("/users", methods=["GET"])
@utils.auth_required
async def bulk_get_users():
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
    return (
        jsonify(
            {"error": "501 Not Implemented - Server does not support this operation"}
        ),
        501,
    )


@blueprint.route("/users", methods=["POST"])
@utils.expects_data(
    id=int,
    username=str,
    discriminator=(str, int),
    avatar=(str, type(None))
)
@utils.auth_required
async def create_user(data: dict):
    """
    Create a User object.

    Returns status 202 if a new user was not created, 201 if a new user was created.

    TODO: Restrict access.
    """

    type = data["type"]

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
    )
    created = await user.create()

    return Response("", status=202 - created)


@blueprint.route("/users/<int:id>")
@utils.app_only
async def get_specific_user(id: int):
    """
    Returns a User object for a given user ID.
    """

    user = await current_app.db.fetch_user(id=id)

    if user is None:
        return (
            jsonify(
                {
                    "error": "404 Not Found - The requested user could not be found in our database."
                }
            ),
            404,
        )

    return jsonify(user.as_dict(user))


@blueprint.route("/users/@me", methods=["GET"])
@utils.auth_required
async def get_user() -> Response:
    """
    Returns the `User` object of the requesters account.

    Requires Token authentication.
    """
    return jsonify(request.user.as_dict())
