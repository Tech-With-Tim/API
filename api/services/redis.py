from aioredis import Redis
from typing import Optional, Union
from fakeredis.aioredis import FakeRedis

pool: Optional[Union[FakeRedis, Redis]] = None

__all__ = (pool,)
