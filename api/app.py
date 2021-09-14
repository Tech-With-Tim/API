from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, HTTPException
from aiohttp import ClientSession

from utils.response import JSONResponse
from api import versions

import logging

log = logging.getLogger()

app = FastAPI(
    title="Tech With Tim",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/docs/openapi.json",
    openapi_tags=[
        {"name": "roles", "description": "Manage roles"},
    ],
)
app.router.prefix = "/api"
app.router.default_response_class = JSONResponse

origins = ["*"]  # TODO: change origins later
app.add_middleware(
    CORSMiddleware,
    allow_methods=["*"],
    allow_headers=["*"],
    allow_origins=origins,
    expose_headers=["Location"],
)
app.include_router(versions.v1.router)


@app.on_event("startup")
async def on_startup():
    """Creates a ClientSession to be used app-wide."""
    from api.services import http, piston

    if http.session is None or http.session.closed:
        http.session = ClientSession()
        log.info("Set HTTP session.")

    piston.init()


@app.on_event("shutdown")
async def on_shutdown():
    """Closes the app-wide ClientSession"""
    from api.services import http, piston

    if http.session is not None and not http.session.closed:
        await http.session.close()

    await piston.close()


@app.exception_handler(RequestValidationError)
async def validation_handler(request, err: RequestValidationError):
    return JSONResponse(
        status_code=422, content={"error": "Invalid data", "data": err.errors()}
    )


@app.exception_handler(500)
async def error_500(request, error: HTTPException):
    """
    TODO: Handle the error with our own error handling system.
    """
    log.error(
        "500 - Internal Server Error",
        exc_info=(type(error), error, error.__traceback__),
    )

    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": "Server got itself in trouble",
        },
    )
