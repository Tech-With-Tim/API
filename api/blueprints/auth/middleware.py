from logging import getLogger
import jwt
import os


from api.models import User, Token


log = getLogger("UserMiddleware")


class UserMiddleware:
    """
    Class used to determine the user making the request.

    Authorization headers are used to determine the user.
    """

    def __init__(self, asgi_app, app):
        self.asgi_app = asgi_app
        self.app = app

    async def __call__(self, scope, recieve, send):
        if scope["type"] == "lifespan":
            return await self.asgi_app(scope, recieve, send)

        token = None

        for name, value in scope["headers"]:
            if name == b"authorization":
                token = value.decode()

        if token is None:
            log.debug("No Authorization headers provided.")
            scope["no_auth_reason"] = "No Authorization header provided."
            return await self.asgi_app(scope, recieve, send)

        try:
            payload = jwt.decode(
                jwt=token,
                key=os.environ["SECRET_KEY"],
            )
        except (
            jwt.ExpiredSignatureError,
            jwt.InvalidTokenError,
            jwt.InvalidSignatureError,
        ) as e:
            log.exception(
                "Caught exception in jwt decoding",
                exc_info=(type(e), e, e.__traceback__),
            )
            scope["no_auth_reason"] = "Invalid token."
            return await self.asgi_app(scope, recieve, send)
        else:
            user = await User.fetch(id=payload["uid"])

            if user is None:
                # TODO: Do this through `signals` to reduce response time.
                await Token.delete(user_id=payload["uid"], type="JWT")
                scope["no_auth_reason"] = "No user found for that JWT token?"
                return await self.asgi_app(scope, recieve, send)

            scope["user"] = user

        return await self.asgi_app(scope, recieve, send)
