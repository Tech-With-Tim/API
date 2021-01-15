from postDB.model.model import Model
from quart import Quart, exceptions, jsonify, request
from datetime import datetime, date
from aiohttp import ClientSession
from typing import Any, Optional
from quart_cors import cors
import logging
import json
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
    username: str = request.args.get("username", default="%")
    discriminator: str = request.args.get("discriminator", default="%")
    type: str = request.args.get("type", default="%")

    query = f"""
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
                WHERE username LIKE $1 AND discriminator LIKE $2 AND type LIKE $3
                GROUP BY {sort_by}
                ORDER BY {sort_by} {order}
            ) as users;
        """

    users = await Model.pool.fetchval(
        query, username + "%", discriminator + "%", type + "%"
    )

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
