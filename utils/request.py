from quart import Request as BaseRequest
from typing import Optional

from api.models import User


class Request(BaseRequest):
    """Custom request class to implement authorization."""

    @property
    def user(self) -> Optional[User]:
        return self.scope.get("user", None)
