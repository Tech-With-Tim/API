import os
import typing
import logging

log = logging.getLogger("Config")

DB_URI: str
SECRET_KEY: typing.Optional[str]


def load_env(path: str):
    try:
        with open(path) as f:
            env_file = {
                key.strip(): arg.strip()
                for (key, arg) in [
                    line.strip().split("=") for line in f.readlines() if line.strip()
                ]
            }
    except FileNotFoundError:
        env_file = {}

    for key, val in env_file.items():
        if not os.environ.get(key, None):
            os.environ[key] = env_file.get(key, None)

    for k, v in __annotations__.copy().items():
        if typing.get_origin(v) is None:
            if not (val := os.environ.get(k, None)):
                log.error(f"Required environment variable {k!r} is missing")
                raise EnvironmentError(f"Required environment variable {k!r} is missing")

            globals()[k] = val
            log.debug(f"Loaded {k!r} from environment variables")
        elif typing.get_origin(v) is typing.Union and None in typing.get_args(v):
            if not (val := os.environ.get(k, None)):
                log.warning(f"Optional environment variable {k!r} is missing")
 
            globals()[k] = val
            log.debug(f"Loaded {k!r} from environment variables")
