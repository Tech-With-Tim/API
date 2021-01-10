from quart import current_app, request, redirect, jsonify
from urllib.parse import quote_plus, parse_qs, urlparse
from typing import List, Tuple
import os


from api.app import API
from .. import bp
import utils


DISCORD_ENDPOINT = "https://discord.com/api"
request: utils.Request
SCOPES = ["identify"]
current_app: API


async def exchange_code(
    *, code: str, scope: str, redirect_uri: str, grant_type: str = "authorization_code"
) -> Tuple[dict, int]:
    """Exchange discord oauth code for access and refresh tokens."""
    async with current_app.http_session.post(
        "%s/v6/oauth2/token" % DISCORD_ENDPOINT,
        data=dict(
            code=code,
            scope=scope,
            grant_type=grant_type,
            redirect_uri=redirect_uri,
            client_id=os.environ["DISCORD_CLIENT_ID"],
            client_secret=os.environ["DISCORD_CLIENT_SECRET"],
        ),
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    ) as response:
        return await response.json(), response.status


async def get_user(access_token: str) -> dict:
    """Coroutine to fetch User data from discord using the users `access_token`"""
    async with current_app.http_session.get(
        "%s/v6/users/@me" % DISCORD_ENDPOINT,
        headers={"Authorization": "Bearer %s" % access_token},
    ) as response:
        return await response.json()


def format_scopes(scopes: List[str]) -> str:
    """Format a list of scopes."""
    return " ".join(scopes)


def get_redirect(callback: str, scopes: List[str]) -> str:
    """Generates the correct oauth link depending on our provided arguments."""
    return (
        "{BASE}/oauth2/authorize?response_type=code"
        "&client_id={client_id}"
        "&scope={scopes}"
        "&redirect_uri={redirect_uri}"
        "&prompt=consent"
    ).format(
        BASE=DISCORD_ENDPOINT,
        client_id=os.environ["DISCORD_CLIENT_ID"],
        scopes=format_scopes(scopes),
        redirect_uri=quote_plus(callback),
    )


def is_valid_url(string: str) -> bool:
    """Returns boolean describing if the provided string is a url"""
    result = urlparse(string)
    return all((result.scheme, result.netloc))


@bp.route("/discord/redirect", methods=["GET"])
async def redirect_to_discord_oauth_portal():
    """Redirect user to correct oauth link depending on specified domain and requested scopes."""
    querystring_args = parse_qs(request.query_string)

    callback = querystring_args.get(
        b"callback", (request.scheme + "://" + request.host + "/auth/discord/callback")
    )

    if isinstance(callback, list):  #
        callback = callback[0].decode()

    if not is_valid_url(callback):
        return (
            jsonify(
                {"error": "Bad Request", "message": "Not a well formed redirect URL."}
            ),
            400,
        )

    return redirect(get_redirect(callback=callback, scopes=SCOPES))
