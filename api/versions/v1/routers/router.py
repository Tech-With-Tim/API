from fastapi import APIRouter

from . import auth
from . import roles

router = APIRouter(prefix="/v1")

router.include_router(auth.router)
router.include_router(roles.router)
