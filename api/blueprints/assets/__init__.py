from quart import Quart, Blueprint


blueprint: Blueprint = Blueprint("assets", __name__)


def setup(app: Quart, url_prefix: str):

    # Register blueprint to Quart instance.
    app.register_blueprint(blueprint=blueprint, url_prefix=url_prefix)
