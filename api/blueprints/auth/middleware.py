from logging import getLogger
import jwt
import os


log = getLogger("UserMiddleware")


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
            if name == b"authorization":
                token = value.decode()

        if token is None:
            log.debug("No Authorization headers provided.")
            return await self.asgi_app(scope, recieve, send)

        try:
            payload = jwt.decode(
                jwt=token,
                key=os.environ["SECRET_KEY"],
            )
        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError) as e:
            log.exception(
                f"Caught exception in jwt decoding",
                exc_info=(type(e), e, e.__traceback__),
            )
            return await self.asgi_app(scope, recieve, send)
        else:
            user = await self.app.db.get_user(id=payload["uid"])
            if user is None:
                # TODO: Do this through `signals` to reduce response time.
                token = await self.app.db.get_token(
                    user_id=payload["uid"], type="OAuth2"
                )
                await token.delete()
                return await self.asgi_app(scope, recieve, send)

            scope["user"] = user

        return await self.asgi_app(scope, recieve, send)
