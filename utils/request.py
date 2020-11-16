from quart import Request as BaseRequest


class Request(BaseRequest):
    """Custom request class to implement the user kwarg."""

    @property
    def user(self):
        """Getting the user is handled by our `UserMiddleware`"""
        return self.scope.get("user", None)
