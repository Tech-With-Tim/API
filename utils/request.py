from quart import Request as BaseRequest
from typing import Optional

from api.models import User


class Request(BaseRequest):
    """Custom request class to implement authorization."""

    @property
    async def user(self) -> Optional[User]:
        coro = self.scope.get("user")
        if coro is None:
            return None

        return await coro

    @property
    def payload(self) -> Optional[dict]:
        return self.scope.get("payload")
