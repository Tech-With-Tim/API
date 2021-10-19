from fastapi import APIRouter

from . import auth, challenges, roles, users

router = APIRouter(prefix="/v1")

router.include_router(auth.router)
router.include_router(challenges.router)
router.include_router(roles.router)
router.include_router(users.router)
