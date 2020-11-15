from quart import Request as BaseRequest

from typing import Optional


from db.models import User


class Request(BaseRequest):
    """Custom request class to implement the user kwarg."""

    @property
    def user(self) -> Optional[User]:
        """Getting the user is handled by our `UserMiddleware`"""
        return self.scope.get("user", None)
