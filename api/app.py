from quart import Quart, exceptions, jsonify
from datetime import datetime, date
from aiohttp import ClientSession
from typing import Any, Optional
from quart_cors import cors
import logging
import json
from bs4 import BeautifulSoup as bs

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

        print(
            jsonify({"error": error.name, "message": error.description}),
            error.status_code,
            headers,
        )

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


# ---------------------- Error Handling ----------------------


# General Error handling - returns error specific functions
def general_error_handler(error, error_code):

    # Get specific error
    returned = bs(error.get_body(), "html.parser")
    error_message = returned.contents[-1].strip()
    error_title = returned.find("h1")
    if error_title is None:
        error_codes_dicts = {
            400: "Bad Request",
            401: "Unauthorized",
            403: "Forbidden",
            404: "Not Found",
            405: "Method Not Allowed",
            406: "Not Acceptable",
            408: "Request Timed Out",
            413: "Request Enity Was Too Large",
            416: "Request Range Was Not Satisfied",
            429: "Too Many Requests",
            500: "Server Error",
            501: "Unimplemented",
        }
        error_title = error_codes_dicts[error_code]

    log.error(
        f"{error_code} - {error_title}: {error_message}",
        exc_info=(type(error), error, error.__traceback__),
    )

    return (
        jsonify(
            {
                "error": error_message,
            }
        ),
        error_code,
    )


@app.errorhandler(400)
async def error_400(error: BaseException):
    return general_error_handler(error, 400)


@app.errorhandler(401)
async def error_401(error: BaseException):
    return general_error_handler(error, 401)


@app.errorhandler(403)
async def error_403(error: BaseException):
    return general_error_handler(error, 403)


@app.errorhandler(404)
async def error_404(error: BaseException):
    return general_error_handler(error, 404)


@app.errorhandler(405)
async def error_405(error: BaseException):
    return general_error_handler(error, 405)


@app.errorhandler(406)
async def error_406(error: BaseException):
    return general_error_handler(error, 406)


@app.errorhandler(408)
async def error_408(error: BaseException):
    return general_error_handler(error, 408)


@app.errorhandler(413)
async def error_413(error: BaseException):
    return general_error_handler(error, 413)


@app.errorhandler(416)
async def error_416(error: BaseException):
    return general_error_handler(error, 416)


@app.errorhandler(429)
async def error_429(error: BaseException):
    return general_error_handler(error, 429)


@app.errorhandler(500)
async def error_500(error: BaseException):
    return general_error_handler(error, 500)


@app.errorhandler(501)
async def error_501(error: BaseException):
    return general_error_handler(error, 501)
