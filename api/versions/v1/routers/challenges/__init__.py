from . import languages
from .routes import router

router.include_router(languages.router)

__all__ = (router,)
