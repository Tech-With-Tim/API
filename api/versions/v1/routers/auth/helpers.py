import config
import typing

from api.services import http
from urllib.parse import quote_plus


DISCORD_ENDPOINT = "https://discord.com/api"
SCOPES = ["identify"]


async def exchange_code(
    *, code: str, scope: str, redirect_uri: str, grant_type: str = "authorization_code"
) -> typing.Tuple[dict, int]:
    """Exchange discord oauth code for access and refresh tokens."""
    async with http.session.post(
        "%s/v6/oauth2/token" % DISCORD_ENDPOINT,
        data=dict(
            code=code,
            scope=scope,
            grant_type=grant_type,
            redirect_uri=redirect_uri,
            client_id=config.discord_client_id(),
            client_secret=config.discord_client_secret(),
        ),
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    ) as response:
        return await response.json(), response.status


async def get_user(access_token: str) -> dict:
    """Coroutine to fetch User data from discord using the users `access_token`"""
    async with http.session.get(
        "%s/v6/users/@me" % DISCORD_ENDPOINT,
        headers={"Authorization": "Bearer %s" % access_token},
    ) as response:
        return await response.json()


def format_scopes(scopes: typing.List[str]) -> str:
    """Format a list of scopes."""
    return " ".join(scopes)


def get_redirect(callback: str, scopes: typing.List[str]) -> str:
    """Generates the correct oauth link depending on our provided arguments."""
    return (
        "{BASE}/oauth2/authorize?response_type=code"
        "&client_id={client_id}"
        "&scope={scopes}"
        "&redirect_uri={redirect_uri}"
        "&prompt=consent"
    ).format(
        BASE=DISCORD_ENDPOINT,
        scopes=format_scopes(scopes),
        redirect_uri=quote_plus(callback),
        client_id=config.discord_client_id(),
    )
