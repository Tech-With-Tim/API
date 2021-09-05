import jwt
import utils
import config

from api.models import User
from typing import List, Union
from fastapi import Depends, HTTPException, Request

from api.models import Role
from api.models.permissions import BasePermission


def authorization(app_only: bool = False, user_only: bool = False):
    if app_only and user_only:
        raise ValueError("can't set both app_only and user_only to True")

    async def inner(request: Request):
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

        user = await User.fetch(data["uid"])
        if not user:
            raise HTTPException(status_code=401, detail="Invalid token.")

        if app_only and not user.app:
            raise HTTPException(status_code=403, detail="Users can't use this endpoint")

        if user_only and user.app:
            raise HTTPException(status_code=403, detail="Bots can't use this endpoint")

        return data

    return Depends(inner)


def has_permissions(permissions: List[Union[int, BasePermission]]):
    async def inner(token=authorization()):
        query = """
            WITH userroles AS (
                SELECT ur.role_id
                  FROM userroles ur
                 WHERE ur.user_id = $1
             )
            SELECT r.position,
                   r.permissions
              FROM roles r
             WHERE r.id IN (
                SELECT role_id
                  FROM userroles
            )
        """

        records = await Role.pool.fetch(query, token["uid"])
        if not records:
            raise HTTPException(403, "Missing Permissions")

        user_permissions = 0
        for record in records:
            user_permissions |= record["permissions"]

        return utils.has_permissions(user_permissions, permissions)

    return Depends(inner)
