import jwt
import utils
import config

from api.models import User, Token

from fastapi.params import Param
from fastapi import APIRouter, Request
from datetime import datetime, timedelta
from fastapi.responses import RedirectResponse
from .models import CallbackBody, CallbackResponse
from .helpers import (
    SCOPES,
    get_user,
    get_redirect,
    is_valid_url,
    exchange_code,
    format_scopes,
)

router = APIRouter(prefix="/auth")


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
