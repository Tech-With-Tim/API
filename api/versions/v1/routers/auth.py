import jwt
import utils
import typing
import config
import aiohttp

from api.models import User, Token

from pydantic import BaseModel
from fastapi.params import Param
from fastapi import APIRouter, Request
from datetime import datetime, timedelta
from urllib.parse import quote_plus, urlparse
from fastapi.responses import RedirectResponse

router = APIRouter(prefix="/auth")


DISCORD_ENDPOINT = "https://discord.com/api"
SCOPES = ["identify"]


class CallbackResponse(BaseModel):
    token: str
    exp: datetime


class CallbackBody(BaseModel):
    code: str
    callback: str


async def exchange_code(
    *, code: str, scope: str, redirect_uri: str, grant_type: str = "authorization_code"
) -> typing.Tuple[dict, int]:
    """Exchange discord oauth code for access and refresh tokens."""
    async with aiohttp.ClientSession() as session:
        async with session.post(
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
    async with aiohttp.ClientSession() as session:
        async with session.get(
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


def is_valid_url(string: str) -> bool:
    """Returns boolean describing if the provided string is a url"""
    result = urlparse(string)
    return all((result.scheme, result.netloc))


@router.get(
    "/discord/redirect",
    tags=["auth"],
    status_code=307,
    responses={
        307: {"description": "Successful Redirect", "content": {"text/html": {}}},
        400: {
            "description": "Invalid Callback url",
            "content": {"application/json": {}},
        },
    },
)
async def redirect_to_discord_oauth_portal(
    request: Request, callback: str = Param(None)
):
    """Redirect user to correct oauth link depending on specified domain and requested scopes."""
    callback = callback or (str(request.base_url) + "v1/auth/discord/callback")

    if isinstance(callback, list):
        callback = callback[0]

    if not is_valid_url(callback):
        return utils.JSONResponse(
            {"error": "Bad Request", "message": "Not a well formed redirect URL."}, 400
        )

    return RedirectResponse(
        get_redirect(callback=callback, scopes=SCOPES), status_code=307
    )


if config.debug():

    @router.get(
        "/discord/callback",
        tags=["auth"],
        response_model=CallbackResponse,
        response_description="GET Discord OAuth Callback",
    )
    async def get_discord_oauth_callback(
        request: Request, code: str = Param(...), callback: str = Param(None)
    ):
        """
        Callback endpoint for finished discord authorization flow.
        """
        callback = callback or (str(request.base_url) + "v1/auth/discord/callback")
        return await post_discord_oauth_callback(code, callback)


@router.post(
    "/discord/callback",
    tags=["auth"],
    response_model=CallbackResponse,
    response_description="POST Discord OAuth Callback",
)
async def post_discord_oauth_callback(data: CallbackBody):
    """
    Callback endpoint for finished discord authorization flow.
    """
    if not is_valid_url(data.callback):
        return utils.JSONResponse(
            {"error": "Bad Request", "message": "Not a well formed redirect URL."}, 400
        )

    access_data, status_code = await exchange_code(
        code=data.code, scope=format_scopes(SCOPES), redirect_uri=data.callback
    )

    if access_data.get("error", False):
        if status_code == 400:
            return utils.JSONResponse(
                {
                    "error": "Bad Request",
                    "message": "Discord returned 400 status.",
                    "data": access_data,
                },
                400,
            )

        if 200 < status_code >= 300:
            return utils.JSONResponse(
                {
                    "error": "Bad Gateway",
                    "message": "Discord returned non 2xx status code",
                },
                502,
            )

    expires_at = datetime.utcnow() + timedelta(seconds=access_data["expires_in"])
    expires_at = expires_at.replace(microsecond=0)

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
        key=config.secret_key(),
    )

    return {"token": token, "exp": expires_at}
