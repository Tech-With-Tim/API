"""
Main app file where we (in order):
    - Setup logging
    - Implement error handling
    - Load blueprints
"""

from quart import Quart, jsonify
import logging

import utils


logging.basicConfig(
    level=logging.DEBUG
)  # TODO: Someone setup a better logging config, thanks.
log = logging.getLogger("ROOT")

for logger in ("asyncio", "quart"):
    logging.getLogger(logger).setLevel(logging.CRITICAL)


def setup_app() -> Quart:
    """Separate function to setup the Quart app so that we can implement logging
    before loading the complete app.
    """

    from api.blueprints import auth, cdn, logging, guilds
    from quart_cors import cors
    import utils

    self = Quart(__name__)
    self = cors(self)

    # Add Auth Middleware.
    self.asgi_app = auth.UserMiddleware(app=self, asgi_app=self.asgi_app)

    # Use custom Request class to implement User property
    self.request_class = utils.Request

    # setup Blueprints:
    guilds.setup(app=self, url_prefix="/guilds")
    logging.setup(app=self, url_prefix="/log")
    auth.setup(app=self, url_prefix="/auth")
    cdn.setup(app=self, url_prefix="/cdn")

    return self


app = setup_app()


# Index view.
@app.route("/", methods=["GET"])
async def index():
    """GET @ / -> Testing endpoint"""
    return jsonify({"Hello": "World"})


@app.route("/endpoints", methods=["GET"])
@utils.auth_required
async def testing_endpoints():
    """Automatically generated list of endpoints."""
    from utils import dedent

    response = {}

    def get_method(rule):
        rules = list(rule.methods)
        rules.remove("OPTIONS")
        if "HEAD" in rules:
            rules.remove("HEAD")

        return rules[0]

    for route in app.url_map.iter_rules():
        if (doc := app.view_functions[route.endpoint].__doc__) is not None:
            docstring = dedent(doc)
        else:
            docstring = None

        if response.get(str(route)) is None:
            response[str(route)] = {
                get_method(route): docstring
            }
        else:
            response[str(route)][get_method(route)] = docstring

    return jsonify({"endpoints": response})


""" Error handlers """


@app.errorhandler(404)
async def not_found(_):
    """
    Return a json formatted error instead of default text based reply.

    TODO: Log this ?
    """
    return jsonify({"error": "NotFound", "message": "Nothing matches the given URI"}), 404


@app.errorhandler(405)
async def method_not_allowed(_):
    """
    Return a json formatted error instead of default text based reply.

    TODO: Log this.
    """

    return jsonify(
        {
            "error": "405 Method Not Allowed",
            "message": "Specified method is invalid for this resource"
        }
    )


@app.errorhandler(500)
async def error_500(error: BaseException):
    """
    TODO: Handle the error with our own error handling system.

    TODO: Return the response before handling the error.
            ( To reduce response time )
    """
    log.error("500 - Internal Server Error", exc_info=(type(error), error, error.__traceback__))

    return (
        jsonify({"error": "Internal Server Error - Server got itself in trouble"}),
        500,
    )
