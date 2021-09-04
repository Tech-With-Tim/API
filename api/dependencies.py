import jwt
import utils
import config

from typing import List, Optional, Union
from fastapi import Depends, HTTPException, Request

from api.models import Role
from api.models.permissions import BasePermission


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
        )
    except (jwt.PyJWTError, jwt.InvalidSignatureError):
        raise HTTPException(status_code=401, detail="Invalid token.")

    data["uid"] = int(data["uid"])

    return data


async def has_permissions(permissions: List[Union[int, BasePermission]]):
    async def inner(token=Depends(access_token)):
        query = """
            WITH user_roles AS (
                SELECT role_id FROM userroles WHERE user_id = $1
            )
                SELECT position, permissions FROM roles WHERE id IN (SELECT * FROM user_roles);
        """

        records = await Role.pool.fetch(query, token["uid"])
        if not records:
            raise HTTPException(403, "Missing Permissions")

        user_permissions = 0
        for record in records:
            user_permissions |= record["permissions"]

        return utils.has_permissions(user_permissions, permissions)

    return Depends(inner)
