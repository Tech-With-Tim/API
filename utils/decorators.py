from typing import Callable, Any, Dict, Type, Union, Tuple
from quart import request, jsonify, Request
from functools import wraps


request: Request


def auth_required(func: Callable) -> Callable:
    """A decorator to restrict route access to authenticated users."""

    @wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> Any:
        if request.user is None:
            return jsonify({"error": "403 Forbidden"}), 403
        else:
            return await func(*args, **kwargs)

    return wrapper


def expects_data(**arguments: Dict[str, Union[Tuple[Type], Type]]) -> Callable:
    """
    A decorator to ensure the user enters provided `arguments`

    If request data is not a dict, function is ran normally.
    """

    def outer(func: Callable) -> Callable:
        @wraps(func)
        async def inner(*args: Any, **kwargs: Any) -> Any:
            error = {}

            data = await request.json

            if not isinstance(data, dict):
                return await func(*args, data=data, **kwargs)

            for arg, _type in arguments.items():
                if arg not in data:
                    error[arg] = "This field is required."
                else:
                    if not isinstance(data[arg], _type):
                        error[arg] = "Expected argument of type `{}`, got `{}`".format(
                            _type.__name__, type(data[arg]).__name__
                        )

            if error:
                return jsonify({"error": "400 Bad Request", "data": error}), 400

            return await func(*args, data=data, **kwargs)

        return inner

    return outer
