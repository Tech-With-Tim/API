from aiohttp import ClientSession
from typing import Optional


__all__ = ("session",)

session: Optional[ClientSession] = None
