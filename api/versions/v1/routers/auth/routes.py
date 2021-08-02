import jwt
import utils
import config

from pydantic import HttpUrl
from fastapi import APIRouter, Request
from datetime import datetime, timedelta
from fastapi.responses import RedirectResponse

from api.models import User, Token
from .models import CallbackBody, CallbackResponse
from .helpers import (
    SCOPES,
    get_user,
    get_redirect,
    exchange_code,
    format_scopes,
)

router = APIRouter(prefix="/auth")


@router.get(
    "/discord/redirect",
    tags=["auth"],
    status_code=307,
)
async def redirect_to_discord_oauth_portal(request: Request, callback: HttpUrl = None):
    """Redirect user to correct oauth link depending on specified domain and requested scopes."""
    callback = callback or (str(request.base_url) + "v1/auth/discord/callback")

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
        request: Request, code: str, callback: HttpUrl = None
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

        if status_code < 200 or status_code >= 300:
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
