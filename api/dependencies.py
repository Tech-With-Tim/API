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
        raise ValueError("app_only and user_only are mutually exclusive")

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
        except jwt.PyJWTError:
            raise HTTPException(status_code=401, detail="Invalid token.")

        data["uid"] = int(data["uid"])

        user = await User.fetch(data["uid"])
        if not user:
            raise HTTPException(status_code=401, detail="Invalid token.")

        if app_only and not user.app:
            raise HTTPException(status_code=403, detail="Users can't use this endpoint")

        if user_only and user.app:
            raise HTTPException(status_code=403, detail="Bots can't use this endpoint")

        return user

    return Depends(inner)


def has_permissions(permissions: List[Union[int, BasePermission]]):
    async def inner(user=authorization()):
        query = """
            SELECT *
              FROM roles r
             WHERE r.id IN (
                SELECT ur.role_id
                  FROM userroles ur
                 WHERE ur.user_id = $1
            )
        """
        records = await Role.pool.fetch(query, user.id)
        if not records:
            raise HTTPException(403, "Missing Permissions")

        user_permissions = 0
        for record in records:
            user_permissions |= record["permissions"]

        if not utils.has_permissions(user_permissions, permissions):
            raise HTTPException(403, "Missing Permissions")

        return [Role(**record) for record in records]

    return Depends(inner)
