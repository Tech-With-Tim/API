from fastapi import APIRouter

from .models import UserResponse

from api.models import User, UserRole
from api.dependencies import authorization


router = APIRouter(prefix="/users")


@router.get(
    "/@me",
    response_model=UserResponse,
    responses={401: {"description": "Unauthorized"}},
)
async def get_current_user(user: User = authorization()):
    query = """SELECT role_id FROM userroles WHERE user_id = $1;"""
    roles = [record["role_id"] for record in await UserRole.pool.fetch(query, user.id)]

    return {**user.as_dict(), "roles": roles}
