from quart import Quart, Blueprint


bp: Blueprint = Blueprint("challenges", __name__)


def setup(app: Quart, url_prefix: str) -> None:
    from . import views  # noqa F401

    # Import the views package to load routes.

    # register the blueprint to our Quart instance.
    app.register_blueprint(bp, url_prefix=url_prefix)
