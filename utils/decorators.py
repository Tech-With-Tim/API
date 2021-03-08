from quart import request, Request, exceptions
from typing import Callable, Any
from functools import wraps
from http import HTTPStatus
from postDB import Model


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


def requires_perms(*permissions: int):
    """A decorator to check for users permissions"""

    def outer(func: Callable):
        @wraps(func)
        async def inner(*args: Any, **kwargs: Any):
            if request.user_id is None:
                raise exceptions.Unauthorized

            perms = 0
            for perm in permissions:
                perms |= 1 << perm

            query = """SELECT * FROM has_permissions($1, $2);"""
            record = await Model.pool.fetchrow(query, request.user_id, perms)

            if not record["has_permissions"]:
                http_status = HTTPStatus.FORBIDDEN
                http_status.description = "Missing Permissions."
                raise exceptions.Forbidden(http_status)

            return await func(*args, **kwargs)

        return inner

    return outer
