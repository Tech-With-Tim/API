import logging
from typing import Any, Dict, List

import config
from api.services import http


__all__ = ("get_runtimes", "get_runtimes_dict", "get_runtime", "Runtime")

log = logging.getLogger()

_base_url: str = config.piston_url().rstrip("/") + "/"  # make sure there's a / at the end


async def _make_request(method: str, endpoint: str, data: Any = None) -> Any:
    async with http.session.request(
        method,
        _base_url + endpoint,
        json=data,
        raise_for_status=True,
    ) as response:
        return await response.json()


async def get_runtimes() -> List["Runtime"]:
    """Get a list of all available runtimes."""
    runtimes = await _make_request("GET", "runtimes")
    return [Runtime(runtime) for runtime in runtimes]


async def get_runtimes_dict() -> Dict[str, List["Runtime"]]:
    """Get a dictionary of language names and aliases mapped to a list of
    all the runtimes with that name or alias.
    """

    runtimes = await get_runtimes()
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


async def get_runtime(language: str) -> List["Runtime"]:
    """Get a runtime with a language or an alias."""

    runtimes_dict = await get_runtimes_dict()
    return runtimes_dict.get(language, [])


class Runtime:
    def __init__(self, data: dict):
        self.language = data["language"]
        self.version = data["version"]
        self.aliases = data["aliases"]
        self.runtime = data.get("runtime")
