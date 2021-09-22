from fastapi.exceptions import RequestValidationError
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fakeredis.aioredis import FakeRedis
from aiohttp import ClientSession
from aioredis import Redis
import logging

from utils.response import JSONResponse
from api import versions
import config


log = logging.getLogger(__name__)

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
    from api.services import redis, http

    if http.session is None or http.session.closed:
        http.session = ClientSession()
        log.info("Created HTTP ClientSession.")

    if redis.pool is None or redis.pool.connection is None:
        if (redis_uri := config.redis_uri()) is not None:
            redis.pool = Redis.from_url(redis_uri)
            log.info("Connected to redis server: " + str(redis.pool))
        else:
            redis.pool = FakeRedis()
            log.warning(
                "\n"
                "  > Created FakeRedis server, using a real redis server is suggested.\n"
                "  > You can launch a local one using `docker compose up redis` and providing the url in env."
            )


@app.get("/test")
async def dispatch_event():
    from api.services import redis

    n = await redis.dispatch("test", "Hello World")
    return f"Received by {n} clients."


@app.on_event("shutdown")
async def on_shutdown():
    """Closes the app-wide ClientSession"""
    from api.services import redis, http

    if http.session is not None and not http.session.closed:
        await http.session.close()

    if redis.pool is not None:
        await redis.pool.close()


@app.exception_handler(RequestValidationError)
async def validation_handler(_: Request, err: RequestValidationError):
    return JSONResponse(
        status_code=422, content={"error": "Invalid data", "data": err.errors()}
    )


@app.exception_handler(500)
async def error_500(_: Request, error: HTTPException):
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
