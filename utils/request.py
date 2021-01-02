from quart import Request as BaseRequest
from typing import Optional

from api.models import User


class Request(BaseRequest):
    """Custom request class to implement authorization."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._user = None
        self.__has_fetched = False

    @property
    def is_authorized(self) -> bool:
        return isinstance(self.jwt, dict)

    @property
    async def user(self) -> Optional[User]:
        """
        The User object is no longer fetched in Authorization Middleware.
        This is to reduce avg. response time.
        """
        if not self.is_authorized:
            return None

        if not self.__has_fetched:
            self._user = await User.fetch(id=self.user_id)
            self.__has_fetched = True

        return self._user

    @property
    def user_id(self) -> Optional[int]:
        if not self.is_authorized:
            return None

        return self.jwt["uid"]

    @property
    def jwt(self) -> Optional[dict]:
        return self.scope.get("jwt")
