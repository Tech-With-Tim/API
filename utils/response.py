from datetime import datetime
import typing

from fastapi.responses import JSONResponse as BaseResponse


class JSONResponse(BaseResponse):
    def render(self, content: typing.Any) -> bytes:
        if isinstance(content, datetime):
            return content.replace(microsecond=0).isoformat()

        return super().render(content)
