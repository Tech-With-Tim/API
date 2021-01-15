from postDB.model.model import Model
from quart import Quart, exceptions, jsonify, request
from datetime import datetime, date
from aiohttp import ClientSession
from typing import Any, Optional, Union
from quart_cors import cors
import logging
import json
from .models.user import User

import utils


from api.blueprints import auth


log = logging.getLogger()


class JSONEncoder(json.JSONEncoder):
    def default(self, o: Any) -> Any:
        if isinstance(o, (datetime, date)):
            o.replace(microsecond=0)
            return o.isoformat()

        return super().default(o)


class API(Quart):
    """Quart subclass to implement more API like handling."""

    http_session: Optional[ClientSession] = None
    request_class = utils.Request
    json_encoder = JSONEncoder

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("static_folder", None)
        super().__init__(*args, **kwargs)

    async def handle_http_exception(self, error: exceptions.HTTPException):
        """
        Returns errors as JSON instead of default HTML
        Uses custom error handler if one exists.
        """

        handler = self._find_exception_handler(error=error)

        if handler is not None:
            return await handler(error)

        headers = error.get_headers()
        headers["Content-Type"] = "application/json"

        return (
            jsonify({"error": error.name, "message": error.description}),
            error.status_code,
            headers,
        )

    async def startup(self) -> None:
        self.http_session = ClientSession()
        return await super().startup()


# Set up app
app = API(__name__)
app.asgi_app = utils.TokenAuthMiddleware(app.asgi_app, app)
app = cors(app, allow_origin="*")  # TODO: Restrict the origin(s) in production.
# Set up blueprints
auth.setup(app=app, url_prefix="/auth")


@app.route("/")
async def index():
    """Index endpoint used for testing."""
    return jsonify({"status": "OK"})


@app.route("/users", methods=["GET"])
async def get_users():

    # TODO:
    # * Pagination with:
    #     * x users per page
    #     * Selecting page y
    #     * Selecting users from index a->b

    sort_by: str = request.args.get("sort_by", default="id")
    order: str = request.args.get("order", default="ASC")
    username: str = request.args.get("username", default=None)
    discriminator: str = request.args.get("discriminator", default=None)
    type: str = request.args.get("type", default=None)
    page: Union[str, int] = request.args.get("pages", default=1)
    limit: Union[str, int] = request.args.get("limit", default=100)
    users = []

    # The following if statements are to check the number of queries passed
    # and allow the user to pass any number of queries possible
    if username is None and type is None and discriminator is None:
        query = """
                SELECT json_agg(records)
                FROM (
                    SELECT
                            json_build_object(
                                'id', id,
                                'username', username,
                                'discriminator', discriminator,
                                'avatar', avatar,
                                'type', type
                            ) as records
                    FROM users
                    GROUP BY id
                    ORDER BY {0} {1}
                    OFFSET $1::INT * $2::INT
                ) as users;
            """.format(
            sort_by, order
        )

        for i in range(120):
            await User.create(i + 1, f"DemoUser{i+1}", f"{i+1}", "some", "USER")

        users = await Model.pool.fetchval(query, int(page), int(limit))

    # To check if all queries are passed
    if username is not None and type is not None and discriminator is not None:
        query = """
            SELECT json_agg(records)
            FROM (
                SELECT
                        json_build_object(
                            'id', id::TEXT,
                            'username', username,
                            'discriminator', discriminator,
                            'avatar', avatar,
                            'type', type
                        ) as records
                FROM users
                WHERE username LIKE $1 AND discriminator LIKE $2 AND type LIKE $3
                GROUP BY id
                ORDER BY {0} {1}
                OFFSET $4::INT * $5::INT
            ) as users;
        """.format(
            sort_by, order
        )

        users = await Model.pool.fetchval(
            query,
            username + "%",
            discriminator + "%",
            type + "%",
            int(page),
            int(limit),
        )

    # The next 3 if statements are to check if 2 queries are passed
    if username is not None and type is not None and discriminator is None:
        query = """
            SELECT json_agg(records)
            FROM (
                SELECT
                        json_build_object(
                            'id', id,
                            'username', username,
                            'discriminator', discriminator,
                            'avatar', avatar,
                            'type', type
                        ) as records
                FROM users
                WHERE username LIKE $1 AND type LIKE $2
                GROUP BY id
                ORDER BY {0} {1}
                OFFSET $3::INT * $4::INT
            ) as users;
        """.format(
            sort_by, order
        )

        users = await Model.pool.fetchval(
            query, username + "%", type + "%", int(page), int(limit)
        )

    if username is not None and type is None and discriminator is not None:
        query = """
            SELECT json_agg(records)
            FROM (
                SELECT
                        json_build_object(
                            'id', id,
                            'username', username,
                            'discriminator', discriminator,
                            'avatar', avatar,
                            'type', type
                        ) as records
                FROM users
                WHERE username LIKE $1 AND discriminator LIKE $2
                GROUP BY id
                ORDER BY {0} {1}
                OFFSET $3::INT * $4::INT
            ) as users;
        """.format(
            sort_by, order
        )

        users = await Model.pool.fetchval(
            query, username + "%", discriminator + "%", int(page), int(limit)
        )

    if username is None and type is not None and discriminator is not None:
        query = """
            SELECT json_agg(records)
            FROM (
                SELECT
                        json_build_object(
                            'id', id,
                            'username', username,
                            'discriminator', discriminator,
                            'avatar', avatar,
                            'type', type
                        ) as records
                FROM users
                WHERE discriminator LIKE $1 AND type LIKE $2
                GROUP BY id
                ORDER BY {0} {1}
                OFFSET $3::INT * $4::INT
            ) as users;
        """.format(
            sort_by, order
        )

        users = await Model.pool.fetchval(
            query, discriminator + "%", type + "%", int(page), int(limit)
        )

    # The next 3 if statements are to check if only one query is passed
    if username is not None and discriminator is None and type is None:
        query = """
            SELECT json_agg(records)
            FROM (
                SELECT
                        json_build_object(
                            'id', id,
                            'username', username,
                            'discriminator', discriminator,
                            'avatar', avatar,
                            'type', type
                        ) as records
                FROM users
                WHERE username LIKE $1
                GROUP BY id
                ORDER BY {0} {1}
                OFFSET $2::INT * $3::INT
            ) as users;
        """.format(
            sort_by, order
        )

        users = await Model.pool.fetchval(query, username + "%", int(page), int(limit))

    if discriminator is not None and username is None and type is None:
        query = """
            SELECT json_agg(records)
            FROM (
                SELECT
                        json_build_object(
                            'id', id,
                            'username', username,
                            'discriminator', discriminator,
                            'avatar', avatar,
                            'type', type
                        ) as records
                FROM users
                WHERE discriminator LIKE $1
                GROUP BY id
                ORDER BY {0} {1}
                OFFSET $1::INT * $2::INT
            ) as users;
        """.format(
            sort_by, order
        )

        users = await Model.pool.fetchval(
            query, discriminator + "%", int(page), int(limit)
        )

    if type is not None and username is None and discriminator is None:
        query = """
            SELECT json_agg(records)
            FROM (
                SELECT
                        json_build_object(
                            'id', id,
                            'username', username,
                            'discriminator', discriminator,
                            'avatar', avatar,
                            'type', type
                        ) as records
                FROM users
                WHERE type LIKE $1
                GROUP BY id
                ORDER BY {0} {1}
                OFFSET $1:INT * $2::INT
            ) as users;
        """.format(
            sort_by, order
        )

        users = await Model.pool.fetchval(query, type + "%", int(page), int(limit))

    if page is not None and limit is None:
        return jsonify(
            {
                "error": "If the pages query is provided then limit query should also be provided."
            }
        )

    # To check if there are no users
    if users is None or users == []:
        return jsonify([])

    return jsonify(users)


@app.errorhandler(500)
async def error_500(error: BaseException):
    """
    TODO: Handle the error with our own error handling system.
    """
    log.error(
        "500 - Internal Server Error",
        exc_info=(type(error), error, error.__traceback__),
    )

    return (
        jsonify({"error": "Internal Server Error - Server got itself in trouble"}),
        500,
    )
