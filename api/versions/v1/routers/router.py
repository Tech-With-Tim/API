from fastapi import APIRouter
from .auth.routes import router as auth_router

router = APIRouter(prefix="/v1")

router.include_router(auth_router)
