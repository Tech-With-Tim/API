from quart import Quart, exceptions, jsonify, request
from datetime import datetime, date
from aiohttp import ClientSession
from typing import Any, Optional
from quart_cors import cors
import logging
import json

import utils


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

        from pprint import pprint
        pprint(request.scope.get("payload"))

        return (
            jsonify({"error": "%s - %s" % (error.name, error.description)}),
            error.status_code,
        )

    async def startup(self) -> None:
        self.http_session = ClientSession()
        return await super().startup()


app = API(__name__)
app.asgi_app = utils.TokenAuthMiddleware(app.asgi_app, app)
app = cors(app, allow_origin="*")  # TODO: Restrict the origin(s) in production.


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
