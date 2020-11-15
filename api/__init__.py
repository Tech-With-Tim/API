"""
Main app file where we (in order):
    - Setup logging
    - Implement error handling
    - Load blueprints
"""

from quart import Quart, jsonify
from traceback import print_exception
import logging


logging.basicConfig(
    level=logging.DEBUG
)  # TODO: Someone setup a better logging config, thanks.
log = logging.getLogger('ROOT')


def setup_app() -> Quart:
    """Separate function to setup the Quart app so that we can implement logging before loading the complete app."""
    from api.blueprints import (
        auth
    )
    import utils

    _app = Quart(
        __name__
    )

    # Add Auth Middleware.
    _app.asgi_app = auth.UserMiddleware(
        app=_app,
        asgi_app=_app.asgi_app
    )

    # Use custom Request class to implement User property
    _app.request_class = utils.Request

    # setup Blueprints:
    auth.setup(
        app=_app,
        url_prefix="/auth"
    )

    return _app


app = setup_app()


# Index view.
@app.route('/', methods=["GET"])
async def index():
    """GET @ / -> Testing endpoint"""
    return jsonify({
        "Hello": "World",
        "method": "GET"
    })


@app.route('/test', methods=["GET"])
async def testing():
    """List all endpoints."""

    func_list = {}

    for rule in app.url_map.iter_rules():
        if rule.endpoint != "static":
            func_list[f"{rule.methods} @ {rule.rule}"] = app.view_functions[rule.endpoint].__doc__.strip()

    return jsonify({
        "status": "Success!",
        "endpoints": func_list
    })


""" Error handlers """


@app.errorhandler(404)
async def not_found(_):
    """
    Return a json formatted error instead of default text based reply.

    TODO: Log this ?
    """
    return jsonify({
        "error": "NotFound - Nothing matches the given URI"
    }), 404


@app.errorhandler(500)
async def error_500(error: BaseException):
    """
    TODO: Handle the error with our own error handling system.

    TODO: Return the response before handling the error.
            ( To reduce response time )
    """
    print_exception(
        type(error),
        error,
        error.__traceback__
    )

    return jsonify({
        "error": "Internal Server Error - Server got itself in trouble"
    }), 500
