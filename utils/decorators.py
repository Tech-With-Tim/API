from quart import request, Request, exceptions
from typing import Callable, Any
from functools import wraps


request: Request


def app_only(func: Callable) -> Callable:
    """A decorator that restricts view access to "APP" users."""

    @wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> Any:
        if request.user_id is None:
            raise exceptions.Unauthorized

        user = await request.user

        if not getattr(user, "type", "USER") == "APP":
            raise exceptions.Forbidden

        return await func(*args, **kwargs)

    return wrapper


def auth_required(func: Callable) -> Callable:
    """A decorator to restrict view access to authorized users."""

    @wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> Any:
        if request.user_id is None:
            raise exceptions.Unauthorized

        return await func(*args, **kwargs)

    return wrapper


# TODO
#  Permission required decorators.
#   > Will be used like: `@requires_perm("admin")` or `@requires_perms("admin", "edit_site_settings")`
