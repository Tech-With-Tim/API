import logging
from typing import Any, Dict, List, Optional

from aiohttp import ClientSession

__all__ = ("client", "init", "close", "PistonClient", "Runtime")

client: Optional["PistonClient"] = None

log = logging.getLogger()


def init():
    global client

    if client is None or client.closed:
        client = PistonClient()
        log.info("Set Piston client.")


async def close():
    if client is not None and not client.closed:
        await client.close()


class PistonClient:
    base_url: str = "https://emkc.org/api/v2/piston/"

    def __init__(self):
        self._session: ClientSession = ClientSession(raise_for_status=True)

    @property
    def closed(self) -> bool:
        return self._session.closed

    async def close(self):
        await self._session.close()

    async def _make_request(self, method: str, endpoint: str, data: Any = None) -> Any:
        async with self._session.request(
            method, self.base_url + endpoint, json=data
        ) as response:
            return await response.json()

    async def get_runtimes(self) -> List["Runtime"]:
        """Get a list of all available runtimes."""
        runtimes = await self._make_request("GET", "runtimes")
        return [Runtime(runtime) for runtime in runtimes]

    async def get_runtimes_dict(self) -> Dict[str, List["Runtime"]]:
        """Get a dictionary of language names and aliases mapped to a list of
        all the runtimes with that name or alias.
        """

        runtimes = await self.get_runtimes()
        runtimes_dict = {}

        for runtime in runtimes:
            if runtime.language in runtimes_dict:
                runtimes_dict[runtime.language].append(runtime)
            else:
                runtimes_dict[runtime.language] = [runtime]

            for alias in runtime.aliases:
                if alias in runtimes_dict:
                    runtimes_dict[alias].append(runtime)
                else:
                    runtimes_dict[alias] = [runtime]

        return runtimes_dict

    async def get_runtime(self, language: str) -> List["Runtime"]:
        """Get a runtime with a language or an alias."""

        runtimes_dict = await self.get_runtimes_dict()
        return runtimes_dict.get(language, [])


class Runtime:
    def __init__(self, data: dict):
        self.language = data["language"]
        self.version = data["version"]
        self.aliases = data["aliases"]
        self.runtime = data.get("runtime")
