from fastapi import HTTPException
from api.services import piston


async def check_piston_language_version(language: str, version: str):
    runtimes = await piston.client.get_runtime(language)
    if not runtimes:
        raise HTTPException(404, "Piston language not found.")

    versions = [runtime.version for runtime in runtimes]
    if version not in versions:
        raise HTTPException(404, "Piston language version not found.")
