from fastapi import APIRouter
from . import auth

router = APIRouter(prefix="/v1")

router.include_router(auth.router)
