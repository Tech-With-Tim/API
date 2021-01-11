from quart import current_app, request, redirect, jsonify
from urllib.parse import quote_plus, parse_qs, urlparse
from quart.exceptions import MethodNotAllowed
from datetime import datetime, timedelta
from typing import List
import jwt
import os

from api.models import Token, User
from api.app import API
from .. import bp
import utils


DISCORD_ENDPOINT = "https://discord.com/api"
request: utils.Request
SCOPES = ["identify"]
current_app: API


async def exchange_code(
    *, code: str, scope: str, redirect_uri: str, grant_type: str = "authorization_code"
) -> (dict, int):
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
    qs = parse_qs(request.query_string.decode())

    callback = qs.get(
        "callback", (request.scheme + "://" + request.host + "/auth/discord/callback")
    )

    if isinstance(callback, list):  #
        callback = callback[0]

    if not is_valid_url(callback):
        return (
            jsonify(
                {"error": "Bad Request", "message": "Not a well formed redirect URL."}
            ),
            400,
        )

    return redirect(get_redirect(callback=callback, scopes=SCOPES))


@bp.route("/discord/callback", methods=["GET", "POST"])
async def discord_oauth_callback():
    """
    Callback endpoint for finished discord authorization flow.

    GET ->  Only used in DEBUG mode.
            Gets code from querystring.

    POST -> Gets code from request data.
    """

    if request.method == "GET":
        if not current_app.debug:
            # A GET request to this endpoint should only be used in testing.
            raise MethodNotAllowed(("POST",))

        qs = parse_qs(request.query_string.decode())
        code = qs.get("code")
        if code is not None:
            code = code[0]
        callback = request.scheme + "://" + request.host + "/auth/discord/callback"
    elif request.method == "POST":
        data = await request.json

        code = data["code"]
        callback = data["callback"]
    else:
        raise RuntimeWarning("Unexpected request method. (%s)" % request.method)

    if code is None:
        return (
            jsonify(
                {
                    "error": "Bad Request",
                    "message": "Missing code in %s." % "querystring arguments"
                    if request.method == "GET"
                    else "JSON data",
                }
            ),
            400,
        )

    if not is_valid_url(callback):
        return (
            jsonify(
                {"error": "Bad Request", "message": "Not a well formed redirect URL."}
            ),
            400,
        )

    access_data, status_code = await exchange_code(
        code=code, scope=format_scopes(SCOPES), redirect_uri=callback
    )

    if access_data.get("error", False):
        if status_code == 400:
            return (
                jsonify(
                    {
                        "error": "Bad Request",
                        "message": "Discord returned 400 status.",
                        "data": access_data,
                    }
                ),
                400,
            )

        raise RuntimeWarning(
            "Unpredicted status_code.\n%s\n%s" % (str(access_data), status_code)
        )

    expires_at = datetime.utcnow() + timedelta(seconds=access_data["expires_in"])
    expires_at.replace(microsecond=0)

    user_data = await get_user(access_token=access_data["access_token"])
    user_data["id"] = uid = int(user_data["id"])

    user = await User.fetch(id=uid)

    if user is None:
        user = await User.create(
            id=user_data["id"],
            username=user_data["username"],
            discriminator=user_data["discriminator"],
            avatar=user_data["avatar"],
        )

    await Token(
        user_id=user.id,
        data=access_data,
        expires_at=expires_at,
        token=access_data["access_token"],
    ).update()

    token = jwt.encode(
        {"uid": user.id, "exp": expires_at, "iat": datetime.utcnow()},
        key=os.environ["SECRET_KEY"],
    )

    return jsonify({"token": token, "exp": expires_at})
