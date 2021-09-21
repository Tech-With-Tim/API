from aioredis import Redis
from typing import Optional


pool: Optional[Redis] = None

__all__ = (pool,)
