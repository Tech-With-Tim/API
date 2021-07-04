from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, HTTPException
from utils.response import JSONResponse
from api import versions
import logging
import config


log = logging.getLogger()


app = FastAPI()
config.set_debug(app.debug)
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
