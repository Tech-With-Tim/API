"""
Main app file where we (in order):
    - Setup logging
    - Implement error handling
    - Load blueprints
"""

from quart.exceptions import HTTPStatus
from traceback import print_exception
from quart import Quart, jsonify
import logging


logging.basicConfig(
    level=logging.DEBUG
)  # TODO: Someone setup a better logging config, thanks.
log = logging.getLogger("ROOT")

for logger in ("asyncio", "quart"):
    logging.getLogger(logger).setLevel(logging.CRITICAL)


def setup_app() -> Quart:
    """Separate function to setup the Quart app so that we can implement logging before loading the complete app."""
    from api.blueprints import auth
    import utils

    _app = Quart(__name__)

    # Add Auth Middleware.
    _app.asgi_app = auth.UserMiddleware(app=_app, asgi_app=_app.asgi_app)

    # Use custom Request class to implement User property
    _app.request_class = utils.Request

    # setup Blueprints:
    auth.setup(app=_app, url_prefix="/auth")

    return _app


app = setup_app()


# Index view.
@app.route("/", methods=["GET"])
async def index():
    """GET @ / -> Testing endpoint"""
    return jsonify({"Hello": "World", "method": "GET"})


@app.route("/endpoints", methods=["GET"])
async def testing_endpoints():
    """Automatically generated list of endpoints."""
    from utils import dedent

    response = {}

    for rule in app.url_map.iter_rules():
        if rule.endpoint != "static":
            if rule.rule in response:
                print("WARNING: {} already in response -> skipping".format(rule.rule))

            response[rule.rule] = {"methods": list(rule.methods)}
            if (doc := app.view_functions[rule.endpoint].__doc__) is not None:
                response[rule.rule]["docstring"] = dedent(doc)
            else:
                response[rule.rule]["docstring"] = None

    return jsonify({"status": "Success!", "endpoints": response})


""" Error handlers """


@app.errorhandler(404)
async def not_found(_):
    """
    Return a json formatted error instead of default text based reply.

    TODO: Log this ?
    """
    return jsonify({"error": "NotFound - Nothing matches the given URI"}), 404


@app.errorhandler(405)
async def method_not_allowed(_):
    """
    Return a json formatted error instead of default text based reply.

    TODO: Log this.
    """

    return jsonify(
        {
            "error": "405 Method Not Allowed - Specified method is invalid for this resource"
        }
    )


@app.errorhandler(500)
async def error_500(error: BaseException):
    """
    TODO: Handle the error with our own error handling system.

    TODO: Return the response before handling the error.
            ( To reduce response time )
    """
    print_exception(type(error), error, error.__traceback__)

    return (
        jsonify({"error": "Internal Server Error - Server got itself in trouble"}),
        500,
    )
