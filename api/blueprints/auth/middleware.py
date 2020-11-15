from quart import current_app

import jwt

from logging import getLogger
from pprint import pprint


from db.models import User


log = getLogger('UserMiddleware')


class UserMiddleware:
    """
    Class used to determine the user making the request

    Authentication headers are used to determine the user.
    """

    def __init__(self, asgi_app, app):
        self.asgi_app = asgi_app
        self.app = app

    async def __call__(self, scope, recieve, send):
        if scope["type"] == "lifespan":
            return await self.asgi_app(scope, recieve, send)

        token = None

        for name, value in scope["headers"]:
            if name == "Authorization":
                token = value

        if token is None:
            log.debug("No Authorization headers provided.")
            return await self.asgi_app(scope, recieve, send)

        try:
            payload = jwt.decode(
                jwt=token,
                key=current_app.config["SECRET_KEY"],
            )
        except (
            jwt.ExpiredSignatureError,
            jwt.InvalidTokenError
        ):
            return await self.asgi_app(scope, recieve, send)
        else:
            pprint(payload)

        return await self.asgi_app(scope, recieve, send)
