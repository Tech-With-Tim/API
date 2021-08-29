import jwt
import config

from typing import Optional
from fastapi import HTTPException, Request


async def access_token(request: Request) -> Optional[dict]:
    """Attempts to locate and decode JWT token."""
    token = request.headers.get("authorization")

    if token is None:
        raise HTTPException(status_code=401)

    try:
        data = jwt.decode(
            jwt=token,
            algorithms=["HS256"],
            key=config.secret_key(),
            options=dict(verify_exp=True),
        )
    except (jwt.PyJWTError, jwt.InvalidSignatureError):
        raise HTTPException(status_code=403, detail="Invalid token.")

    data["uid"] = int(data["uid"])

    return data
