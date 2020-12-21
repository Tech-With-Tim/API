from quart import Quart, Blueprint

blueprint: Blueprint = Blueprint("guilds", __name__)


def setup(app: Quart, url_prefix: str):
    from .views import placeholder
    # Import anything in the file so we load the blueprint routes.

    # Reguster blueprint to Quart instance.
    app.register_blueprint(blueprint=blueprint, url_prefix=url_prefix)
