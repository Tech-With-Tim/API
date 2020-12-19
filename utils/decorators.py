from typing import Callable, Any, Dict, Type, Union, Tuple, get_args, get_origin
from quart import request, jsonify, Request
from functools import wraps


request: Request


def app_only(func: Callable) -> Callable:
    """A decorator that restricts view access to authorized "APP" users."""

    @wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> Any:
        if request.user is None:
            return (
                jsonify(
                    {"error": "401 Unauthorized - %s" % request.scope["no_auth_reason"]}
                ),
                401,
            )

        if request.user.type != "APP":
            return (
                jsonify({"error": "403 Forbidden - Authorization will not help."}),
                403,
            )

        return await func(*args, **kwargs)

    return wrapper


def auth_required(func: Callable) -> Callable:
    """A decorator to restrict view access to authorized users."""

    @wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> Any:
        if request.user is None:
            return (
                jsonify(
                    {"error": "401 Unauthorized - %s" % request.scope["no_auth_reason"]}
                ),
                401,
            )
        else:
            return await func(*args, **kwargs)

    return wrapper


def is_optional(field):
    return get_origin(field) is Union and \
           type(None) in get_args(field)


def flatten_types(original: Any) -> Any:
    types = []
    if get_origin(original) is Union:
        for type in get_args(original):
            types.extend(flatten_types(type))
    else:
        if args := get_args(original):
            types.append(args)
        else:
            types.append(original)

    return types


def expects_data(**arguments: Union[Tuple[Type], Type]) -> Callable:
    """
    A decorator to ensure the user enters provided `arguments`
    If no request data is present, 400 error is returned.
    If request data is not a dict, function is ran normally.
    """

    def outer(func: Callable) -> Callable:
        @wraps(func)
        async def inner(*args: Any, **kwargs: Any) -> Any:
            error = {}

            data = await request.json

            if data is None:
                return jsonify({"error": "400 Bad Request", "data": "No data"}), 400

            for arg, _type in arguments.items():
                if arg not in data:
                    if is_optional(_type):
                        continue

                    error[arg] = "This field is required."
                else:
                    if not isinstance(data[arg], tuple(types := flatten_types(_type))):
                        if len(types) > 1:
                            for __type in types:
                                try:
                                    converted = __type(data[arg])
                                except Exception as _:
                                    if error.get(arg) is None:
                                        error[arg] = {}
                                    error[arg][__type.__name__] = "Failed to convert to `%s`" % __type.__name__
                                else:
                                    arguments[arg] = converted
                                    break
                        else:
                            error[arg] = "Expected argument of type `%s`, got `%s`" % (
                                _type.__name__, type(data[arg]).__name__
                            )

            if error:
                return jsonify({"error": "400 Bad Request", "data": error}), 400

            return await func(*args, data=data, **kwargs)

        return inner
    return outer


def expects_form_data(**arguments: Dict[str, Union[Tuple[Type], Type]]) -> Callable:
    """
    A decorator to ensure the user enters provided `arguments` in form request.
    If no request data is present, 400 error is returned.
    If request data is not a dict, function is ran normally.
    """
    def outer(func: Callable) -> Callable:
        @wraps(func)
        async def inner(*args: Any, **kwargs: Any) -> Any:
            error = {}

            data = await request.form

            if data is None:
                return jsonify({"error": "400 Bad Request", "data": "No data"}), 400

            if not isinstance(data, dict):
                return await func(*args, data=data, **kwargs)

            for arg, _type in arguments.items():
                if arg not in data:
                    if is_optional(_type):
                        continue

                    error[arg] = "This field is required."
                else:
                    if not isinstance(data[arg], tuple(types := flatten_types(_type))):
                        if len(types) > 1:
                            for __type in types:
                                try:
                                    converted = __type(data[arg])
                                except Exception as _:
                                    if error.get(arg) is None:
                                        error[arg] = {}
                                    error[arg][__type.__name__] = "Failed to convert to `%s`" % __type.__name__
                                else:
                                    arguments[arg] = converted
                                    break
                        else:
                            error[arg] = "Expected argument of type `%s`, got `%s`" % (
                                _type.__name__, type(data[arg]).__name__
                            )

            if error:
                return jsonify({"error": "400 Bad Request", "data": error}), 400

            return await func(*args, data=data, **kwargs)
        return inner
    return outer


def expects_files(*filenames: Tuple[str]) -> Callable:
    """
    A decorator to ensure the user enters provided `filenames`.
    """
    def outer(func: Callable) -> Callable:
        @wraps(func)
        async def inner(*args: Any, **kwargs: Any) -> Any:
            error = {}

            files = await request.files

            if files is None:
                error = "No data"
                return jsonify({"error": "400 Bad Request", "data": error}), 400

            for filename in filenames:
                if filename not in files.keys():
                    error[filename] = "This file is required."

            if error:
                return jsonify({"error": "400 Bad Request", "data": error}), 400

            return await func(*args, files=files, **kwargs)
        return inner
    return outer
