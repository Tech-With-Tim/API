import os
import typing
import logging

log = logging.getLogger("Config")

DB_URI: str
SECRET_KEY: typing.Optional[str]
TEST_DB_URI: typing.Optional[str]
DISCORD_CLIENT_ID: typing.Optional[str]
DISCORD_CLIENT_SECRET: typing.Optional[str]


def load_env():
    for config, annotation in __annotations__.copy().items():
        if typing.get_origin(annotation) is None:
            if not (val := os.environ.get(config, None)):
                log.error(f"Required environment variable {config!r} is missing")
                raise EnvironmentError(
                    f"Required environment variable {config!r} is missing"
                )

            globals()[config] = val
            log.debug(f"Loaded {config!r} from environment variables")
        elif typing.get_origin(annotation) is typing.Union and None in typing.get_args(
            annotation
        ):
            if not (val := os.environ.get(config, None)):
                log.warning(f"Optional environment variable {config!r} is missing")

            globals()[config] = val
            log.debug(f"Loaded {config!r} from environment variables")
