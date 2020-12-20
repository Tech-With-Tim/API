from quart import Quart, Blueprint

blueprint: Blueprint = Blueprint("logging", __name__)


def setup(app: Quart, url_prefix: str):
    from .views import placeholder

    # Reguster blueprint to Quart instance.
    app.register_blueprint(blueprint=blueprint, url_prefix=url_prefix)
