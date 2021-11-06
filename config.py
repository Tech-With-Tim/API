import logging
import typing
import os


log = logging.getLogger("Config")

__debug = False


def debug() -> bool:
    return __debug


def set_debug(value: bool):
    global __debug
    __debug = value


def postgres_uri() -> str:
    """Connection URI for PostgreSQL database."""
    value = os.environ.get("POSTGRES_URI")

    if value:
        return value

    raise EnvironmentError('Required environment variable "POSTGRES_URI" is missing')


def secret_key() -> typing.Optional[str]:
    """Key for validating and creating JWT tokens"""
    value = os.environ.get("SECRET_KEY", None)

    if not value:
        log.warning('Optional environment variable "SECRET_KEY" is missing')

    return value


def discord_client_id() -> typing.Optional[str]:
    """The client id of the application used for authentication"""
    value = os.environ.get("DISCORD_CLIENT_ID", 0)

    if not value:
        log.warning('Optional environment variable "DISCORD_CLIENT_ID" is missing')

    return value


def discord_client_secret() -> typing.Optional[str]:
    """The client secret of the application used for authentication"""
    value = os.environ.get("DISCORD_CLIENT_SECRET", "")

    if not value:
        log.warning('Optional environment variable "DISCORD_CLIENT_SECRET" is missing')

    return value


def test_postgres_uri() -> typing.Optional[str]:
    """Connection URI for PostgreSQL database for testing."""
    value = os.environ.get("TEST_POSTGRES_URI", "")

    if not value:
        log.warning('Optional environment variable "TEST_POSTGRES_URI" is missing')

    return value


def redis_uri() -> typing.Optional[str]:
    """Connection URI for Redis server."""
    value = os.environ.get("REDIS_URI")

    if not value:
        log.warning('Optional environment variable "REDIS_URI" is missing')

    return value


def test_redis_uri() -> typing.Optional[str]:
    """Connection URI for Redis testing server."""
    value = os.environ.get("TEST_REDIS_URI")

    if not value:
        log.warning('Optional environment variable "TEST_REDIS_URI" is missing')

    return value


def piston_url() -> str:
    """URL of the Piston API."""
    default = "https://emkc.org/api/v2/piston/"
    value = os.environ.get("PISTON_URL")

    if not value:
        log.info(
            f'Optional environment variable "PISTON_URL" is missing, defaults to {default}'
        )

    return value or default
