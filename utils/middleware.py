from functools import partial
import jwt
import os


class TokenAuthMiddleware:
    """
    Class used to authorize requests.

    Authorization headers are used to determine the ID of the user.
    If the request was authorized, you can use "await request.user" to get the user that made the request.
    Delaying this request is to reduce the average response time.
    """
    def __init__(self, asgi_app, app):
        self.asgi_app = asgi_app
        self.app = app

    async def __call__(self, scope, recieve, send):
        run = partial(self.asgi_app, scope, recieve, send)

        if scope["type"] == "lifespan":
            return await run()

        token = None

        for name, value in scope["headers"]:
            if name == b"authorization":
                token = value.decode()

        if token is None:
            return await run()

        try:
            payload = jwt.decode(
                jwt=token,
                algorithms=["HS256"],
                key=os.environ["SECRET_KEY"]
            )

        except jwt.PyJWTError:
            return await run()

        scope["jwt"] = payload

        return await run()
