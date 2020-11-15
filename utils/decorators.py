from quart import request, jsonify
from typing import Callable, Any
from functools import wraps


def auth_required(func: Callable) -> Callable:
    """A decorator to restrict route access to authenticated users."""

    @wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> Any:
        if request.user is None:
            return jsonify({
                "error": "403 Forbidden"
            }), 403
        else:
            return await func(*args, **kwargs)

    return wrapper
