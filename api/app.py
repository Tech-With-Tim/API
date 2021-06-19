from fastapi import FastAPI, HTTPException, Request
from utils.response import JSONResponse
import logging


log = logging.getLogger()


class API(FastAPI):
    """FastAPI subclass to implement more API like handling."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def handle_request(self, request: Request):
        response = await super().handle_request(request)
        log.info(f"{request.method} @ {request.base_url} -> {response.status_code}")
        return response

    async def handle_http_exception(self, error: HTTPException):
        """
        Returns errors as JSON instead of default HTML
        Uses custom error handler if one exists.
        """

        handler = self._find_exception_handler(error=error)

        if handler is not None:
            return await handler(error)

        headers = error.get_headers()
        headers["Content-Type"] = "application/json"

        return JSONResponse(
            headers=headers,
            status_code=error.status_code,
            content={"error": error.name, "message": error.description}
        )


app = API()
app.router.default_response_class = JSONResponse
app.add_exception_handler(HTTPException, app.handle_http_exception)


@app.get("/")
async def index():
    """Index endpoint used for testing."""
    return {"status": "ok"}


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
        content={"error": "Internal Server Error", "message": "Server got itself in trouble"}
    )
