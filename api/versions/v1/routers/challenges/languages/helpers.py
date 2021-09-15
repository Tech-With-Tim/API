from fastapi import HTTPException

from api.services import piston


async def check_piston_language_version(language: str, version: str):
    """Checks if a language and its version are installed on the Piston service.

    Raises an :class:`fastapi.HTTPException` otherwise with a 404 status code.
    """

    runtimes = await piston.client.get_runtime(language)
    if not runtimes:
        raise HTTPException(404, "Piston language not found")

    versions = [runtime.version for runtime in runtimes]
    if version not in versions:
        raise HTTPException(404, "Piston language version not found")
