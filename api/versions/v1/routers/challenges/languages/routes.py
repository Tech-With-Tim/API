from typing import List

import asyncpg
from fastapi import APIRouter, HTTPException, Response

import utils
from api.dependencies import has_permissions
from api.models import ChallengeLanguage
from api.models.permissions import ManageWeeklyChallengeLanguages

from .helpers import check_piston_language_version
from .models import (
    ChallengeLanguageResponse,
    NewChallengeLanguageBody,
    UpdateChallengeLanguageBody,
)

router = APIRouter(prefix="/languages")


@router.get(
    "",
    tags=["challenge languages"],
    response_model=List[ChallengeLanguageResponse],
)
async def fetch_all_languages():
    """Fetch all the weekly challenge languages, ordered alphabetically."""

    query = """
        SELECT *,
               l.id::TEXT
        FROM challengelanguages l
        ORDER BY name
    """
    records = await ChallengeLanguage.pool.fetch(query)

    return [dict(record) for record in records]


@router.get(
    "/{id}",
    tags=["challenge languages"],
    response_model=ChallengeLanguageResponse,
    responses={
        404: {"description": "Language not found"},
    },
)
async def fetch_language(id: int):
    """Fetch a weekly challenge language by its id."""

    query = """
        SELECT *,
               l.id::TEXT
        FROM challengelanguages l
        WHERE l.id = $1
    """
    record = await ChallengeLanguage.pool.fetchrow(query, id)

    if not record:
        raise HTTPException(404, "Language not found")

    return dict(record)


@router.post(
    "",
    tags=["challenge languages"],
    response_model=ChallengeLanguageResponse,
    responses={
        201: {"description": "Language Created Successfully"},
        401: {"description": "Unauthorized"},
        403: {"description": "Missing Permissions"},
        404: {"description": "Piston language or version not found"},
        409: {"description": "Language with that name already exists"},
    },
    status_code=201,
    response_class=utils.JSONResponse,
    dependencies=[has_permissions([ManageWeeklyChallengeLanguages()])],
)
async def create_language(body: NewChallengeLanguageBody):
    """Create a weekly challenge language."""

    await check_piston_language_version(body.piston_lang, body.piston_lang_ver)

    query = """
        INSERT INTO challengelanguages (id, name, download_url, disabled, piston_lang, piston_lang_ver)
            VALUES (create_snowflake(), $1, $2, $3, $4, $5)
            RETURNING *;
    """

    try:
        record = await ChallengeLanguage.pool.fetchrow(
            query,
            body.name,
            body.download_url,
            body.disabled,
            body.piston_lang,
            body.piston_lang_ver,
        )
    except asyncpg.exceptions.UniqueViolationError:
        raise HTTPException(409, "Language with that name already exists")

    return dict(record)


@router.patch(
    "/{id}",
    tags=["challenge languages"],
    responses={
        204: {"description": "Language Updated Successfully"},
        401: {"description": "Unauthorized"},
        403: {"description": "Missing Permissions"},
        404: {"description": "Language, piston language or version not found"},
        409: {"description": "Language with that name already exists"},
    },
    status_code=204,
    dependencies=[has_permissions([ManageWeeklyChallengeLanguages()])],
)
async def update_language(id: int, body: UpdateChallengeLanguageBody):
    """Update a weekly challenge language."""

    query = "SELECT * FROM challengelanguages WHERE id = $1"
    record = await ChallengeLanguage.pool.fetchrow(query, id)

    if not record:
        raise HTTPException(404, "Language not found")

    language = ChallengeLanguage(**record)
    data = body.dict(exclude_unset=True)

    if name := data.get("name", None):
        record = await ChallengeLanguage.pool.fetchrow(
            "SELECT * FROM challengelanguages WHERE name = $1", name
        )

        if record:
            raise HTTPException(409, "Language with that name already exists")

    if "piston_lang" in data or "piston_lang_ver" in data:
        await check_piston_language_version(
            data.get("piston_lang", language.piston_lang),
            data.get("piston_lang_ver", language.piston_lang_ver),
        )

    if data:
        query = "UPDATE challengelanguages SET "
        query += ", ".join(f"{key} = ${i}" for i, key in enumerate(data, 2))
        query += " WHERE id = $1"

        await ChallengeLanguage.pool.execute(query, id, *data.values())

    return Response(status_code=204, content="")


@router.delete(
    "/{id}",
    tags=["challenge languages"],
    responses={
        204: {"description": "Language Deleted Successfully"},
        401: {"description": "Unauthorized"},
        403: {"description": "Missing Permissions or language used in a challenge"},
        404: {"description": "Language not found"},
    },
    status_code=204,
    dependencies=[has_permissions([ManageWeeklyChallengeLanguages()])],
)
async def delete_language(id: int):
    """Delete a weekly challenge language, if it hasn't been used in any challenges."""
    query = "SELECT * FROM challengelanguages WHERE id = $1"
    record = await ChallengeLanguage.pool.fetchrow(query, id)

    if not record:
        raise HTTPException(404, "Language not found")

    # language = ChallengeLanguage(**record)

    query = """
        SELECT * FROM challenges WHERE $1 = ANY(language_ids)
    """
    records = await ChallengeLanguage.pool.fetch(query, id)
    if records:
        raise HTTPException(403, "Language used in a challenge")

    await ChallengeLanguage.pool.execute(
        "DELETE FROM challengelanguages WHERE id = $1", id
    )

    return Response(status_code=204, content="")
