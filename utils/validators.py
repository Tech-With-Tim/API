from quart import request, Request, jsonify, exceptions
from functools import wraps
import typing


request: Request


def find_excess(valid_keys: typing.Iterable[str], data: dict) -> typing.List[str]:
    """
    Finds excess data in the json `data` provided.
    Returns any found arguments.
    """
    return [key for key in data.keys() if key not in valid_keys]


def is_optional(field: typing.Any) -> bool:
    """Returns boolean describing if the provided `field` is optional."""
    return typing.get_origin(field) is typing.Union and type(None) in typing.get_args(
        field
    )


def is_iterable(field: typing.Any) -> bool:
    """
    Returns boolean describing if the provided `field` is iterable.
    (Excludes strings, bytes)
    """
    return isinstance(field, typing.Iterable) and not isinstance(field, (str, bytes))


def find_missing(
    scheme: typing.Dict[str, typing.Union[typing.Tuple[typing.Type], typing.Type]],
    data: dict,
) -> typing.List[str]:
    """
    Finds missing data in the json `data` provided.
    Returns any missing arguments.
    """
    return [
        arg
        for arg, arg_type in scheme.items()
        if arg not in data and not is_optional(arg_type)
    ]


def validate_list(expected, lst: list) -> typing.Union[str, bool]:
    """
    Validate a list against our expected schema.

    Returns False if the list is valid.
    Returns error in string format if invalid.
    """

    if not isinstance(lst, list):
        return "Expected argument of type `%s`, got `%s`" % (
            str(expected).replace("typing.", ""),
            type(lst).__name__,
        )

    each_arg_type = typing.get_args(expected)[0]

    for item in lst:
        if not isinstance(item, each_arg_type):
            return "Not all list items are of expected value, `%s`, found `%s`" % (
                each_arg_type.__name__,
                type(item).__name__,
            )

    return False  # The list is valid.


supported_validation_types = [
    typing.Union,
    typing.List,
    typing.Dict,
    float,
    list,
    dict,
    str,
    int,
]


def validate(
    scheme: typing.Dict[str, typing.Union[typing.Tuple[typing.Type], typing.Type]],
    data: dict,
) -> typing.Union[dict, bool]:
    """
    Validate a dict against the defined scheme.

    Expects find_missing to be ran first

    Returns False if the data matches schema.
    Returns error in dict format if invalid.
    """

    errors = {}
    for arg, arg_type in scheme.items():

        if arg not in data:
            if is_optional(arg_type):
                continue

        if typing.get_origin(arg_type) == list:
            if result := validate_list(expected=arg_type, lst=data[arg]):
                errors[arg] = result

        elif typing.get_origin(arg_type) == dict:
            arg_type = dict

        elif typing.get_origin(arg_type) == typing.Union:
            # Handles both Union and Optional.
            arg_type = typing.get_args(arg_type)

        if is_iterable(arg_type):
            for t in arg_type:
                if t not in supported_validation_types:
                    raise RuntimeWarning(
                        "Type `%s` is not a supported validation type." % str(t)
                    )
        else:
            if arg_type not in supported_validation_types:
                raise RuntimeWarning(
                    "Type `%s` is not a supported validation type." % str(arg_type)
                )

        if not isinstance(data[arg], arg_type):
            errors[arg] = "Expected argument of type `%s`, got `%s`" % (
                str(arg_type).replace("typing.", ""),
                type(data[arg]).__name__,
            )

    if errors:
        return errors

    return False


def expects_data(
    __data_type: typing.Literal["json", "form"] = "json",
    **scheme: typing.Union[typing.Tuple[typing.Type], typing.Type],
) -> typing.Callable:
    """
    A decorator poorly made to ensure the request data fits our validation scheme.
    """

    if not isinstance(scheme, dict):
        raise RuntimeWarning(
            "expects_data does not support validating other data models than dicts."
        )

    if __data_type not in ("json", "form"):
        raise RuntimeWarning("data_type can only be `json` or `form`.")

    def outer(func: typing.Callable) -> typing.Callable:
        @wraps(func)
        async def inner(*args: typing.Any, **kwargs: typing.Any) -> typing.Any:

            if not isinstance(scheme, dict):
                raise exceptions.BadRequest

            data = await getattr(request, __data_type)

            if data is None:
                return (
                    jsonify(error="Bad Request", message="No json data provided."),
                    400,
                )

            if any(excess := find_excess(valid_keys=scheme.keys(), data=data)):
                return (
                    jsonify(
                        error="Bad Request",
                        message="Unexpected keyword arguments provided.",
                        data=excess,
                    ),
                    400,
                )

            if any(missing := find_missing(scheme=scheme, data=data)):
                return (
                    jsonify(
                        error="Bad Request",
                        message="Missing keyword arguments.",
                        data=missing,
                    ),
                    400,
                )

            if out := validate(scheme=scheme, data=data):
                # validate returns `False` if data matches scheme.
                return jsonify(**out), 400

            kwargs.update(out)

            return await func(*args, **kwargs)

        return inner

    return outer


def expects_files(*filenames: typing.Tuple[str]) -> typing.Callable:
    """
    A decorator to ensure the request files include the provided `filenames`.
    """

    def outer(func: typing.Callable) -> typing.Callable:
        @wraps(func)
        async def inner(*args: typing.Any, **kwargs: typing.Any) -> typing.Any:
            files = await request.files
            error = {}

            if files is None:
                return (
                    jsonify(
                        error="Bad Request",
                        message="No files in form data.",
                        data={"expected_files": filenames},
                    ),
                    400,
                )

            for filename in filenames:
                if filename not in files.keys():
                    error[filename] = "This file is required."

            if error:
                return jsonify({"error": "400 Bad Request", "data": error}), 400

            return await func(*args, files=files, **kwargs)

        return inner

    return outer
