from aioredis.client import EncodableT, ChannelT
from fakeredis.aioredis import FakeRedis
from typing import Optional, Union, Any
from aioredis import Redis
import logging
import json


log = logging.getLogger(__name__)


async def dispatch(channel: ChannelT, message: Union[EncodableT, list, dict]) -> Any:
    """Dispatch a pubsub message to the specified channel with the provided message."""
    if pool is None or type(pool) == FakeRedis:
        log.warning("Skipping dispatch call due to missing redis pubsub server.")
        return

    if isinstance(message, (list, dict)):
        message = json.dumps(message)

    return await pool.publish(channel=channel, message=message)


pool: Optional[Union[FakeRedis, Redis]] = None


__all__ = (pool,)
