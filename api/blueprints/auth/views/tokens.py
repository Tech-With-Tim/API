from urllib.parse import quote_plus, parse_qs
from quart import request, jsonify, redirect
from aiohttp import ClientSession
from typing import List
import datetime
import jwt
import os

import utils
from .. import blueprint

from api.models import Token, User


request: utils.Request


DISCORD_ENDPOINT = "https://discord.com/api"


# TODO: Get these variables from database instead of hard-coded
#       So we can change the config from the website.
# FRONTEND_REDIRECT = "http://localhost:5000"
SCOPES = ["identify"]


async def exchange_code(
    *,
    code: str,
    scope: str,
    redirect_uri: str,
    grant_type: str = "authorization_code",
) -> (dict, int):
    """Exchange discord oauth code for access and refresh tokens."""
    async with ClientSession().post(
        "%s/v6/oauth2/token" % DISCORD_ENDPOINT,
        data=dict(
            code=code,
            scope=scope,
            client_id=int(os.environ["DISCORD_CLIENT_ID"]),
            grant_type=grant_type,
            redirect_uri=redirect_uri,
            client_secret=os.environ["DISCORD_CLIENT_SECRET"],
        ),
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    ) as response:
        return await response.json(), response.status


async def get_user(access_token: str) -> dict:
    """Coroutine to fetch User data from discord using the users `access_token`"""
    async with ClientSession().get(
        "%s/v6/users/@me" % DISCORD_ENDPOINT,
        headers={"Authorization": "Bearer %s" % access_token},
    ) as response:
        return await response.json()


def format_scope(scopes: List[str]) -> str:
    """Format a list of scopes."""
    return " ".join(scopes)


async def get_redirect(frontend_redirect: str, scopes: List[str]):
    """
    Generates the correct oauth link depending on our domain and wanted scopes.
    """
    return (
        f"{DISCORD_ENDPOINT}/oauth2/authorize?response_type=code"
        f"&client_id={int(os.environ['DISCORD_CLIENT_ID'])}&scope={format_scope(scopes)}"
        f"&redirect_uri={frontend_redirect}&prompt=consent"
    )


@blueprint.route("/discord/redirect", methods=["GET"])
async def redirect_to_discord_oauth():
    """
    Redirects to correct oauth link depending on current domain
    and wanted scopes.
    """
    redirect_url = await get_redirect(
        frontend_redirect=quote_plus(request.host_url + "/auth/discord/code"),
        scopes=SCOPES,
    )
    return redirect(redirect_url)


@blueprint.route("/discord/code", methods=["GET"])
async def display_code():
    """Parse url and return code."""
    # TODO: Remove this once frontend will be implemented.

    access_data, status_code = await exchange_code(
        code=parse_qs(request.query_string)[b"code"][0].decode(),
        scope=format_scope(SCOPES),
        redirect_uri=request.host_url + "/auth/discord/code",
    )

    if access_data.get("error"):
        if status_code == 400:
            return jsonify({"error": "400 Bad Request - Discord returned error", "data": access_data}), 400
        raise RuntimeError(str(access_data), str(status_code))

    expires_at = datetime.datetime.utcnow() + datetime.timedelta(
        seconds=access_data["expires_in"]
    )
    expires_at = expires_at - datetime.timedelta(microseconds=expires_at.microsecond)

    discord_data: dict = await get_user(access_token=access_data["access_token"])

    discord_data["id"] = int(discord_data["id"])

    user = await User.fetch(discord_data["id"])

    if user is None:
        user = User(
            id=discord_data["id"],
            username=discord_data["username"],
            discriminator=discord_data["discriminator"],
            avatar=discord_data["avatar"],
        )
        await user.create()

    jwt_token = jwt.encode(
        {
            "uid": user.id,
            "exp": expires_at,
            "iat": datetime.datetime.utcnow(),
        },
        key=os.environ["SECRET_KEY"],
    ).decode()

    await Token(  # Insert or update OAuth2 token in database.
        user_id=user.id,
        token=access_data["access_token"],
        type="OAuth2",
        expires_at=expires_at,
        data=access_data,
    ).update()

    await Token(  # Insert or update jwt token in database.
        user_id=user.id, token=jwt_token, type="JWT", expires_at=expires_at, data={}
    ).update()

    return jsonify(dict(token=jwt_token, exp=expires_at.isoformat()))


@blueprint.route("/discord/callback", methods=["POST"])
@utils.expects_data(
    code=str,
    redirect_uri=str
)
async def get_my_token(data: dict):
    """
    Callback endpoint for finished discord authentication.
    Initial authentication is handled by frontend then they call our endpoint.

    Get or Create a JWT token for the authenticated user.
    """

    access_data, status_code = await exchange_code(
        code=data["code"],
        scope=format_scope(SCOPES),
        redirect_uri=data["redirect_uri"],
    )

    if access_data.get("error"):
        if status_code == 400:
            return jsonify({"error": "400 Bad Request - Discord returned error", "data": access_data}), 400
        raise RuntimeError(str(access_data), str(status_code))

    expires_at = datetime.datetime.utcnow() + datetime.timedelta(
        seconds=access_data["expires_in"]
    )
    expires_at = expires_at - datetime.timedelta(microseconds=expires_at.microsecond)

    discord_data: dict = await get_user(access_token=access_data["access_token"])

    user = await User.fetch(discord_data["id"])

    if user is None:
        user = User(
            id=discord_data["id"],
            username=discord_data["username"],
            discriminator=discord_data["discriminator"],
            avatar=discord_data["avatar"],
        )
        await user.create()

    jwt_token = jwt.encode(
        {
            "uid": user.id,
            "exp": expires_at,
            "iat": datetime.datetime.utcnow(),
        },
        key=os.environ["SECRET_KEY"],
    ).decode()

    await Token(  # Insert or update OAuth2 token in database.
        user_id=user.id,
        token=access_data["access_token"],
        type="OAuth2",
        expires_at=expires_at,
        data=access_data,
    ).update()

    await Token(  # Insert or update jwt token in database.
        user_id=user.id, token=jwt_token, type="JWT", expires_at=expires_at, data={}
    ).update()

    return jsonify(dict(token=jwt_token, exp=expires_at.isoformat()))
