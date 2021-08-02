from datetime import datetime
from pydantic import BaseModel, HttpUrl


class CallbackResponse(BaseModel):
    token: str
    exp: datetime


class CallbackBody(BaseModel):
    code: str
    callback: HttpUrl
