from datetime import datetime
from pydantic import BaseModel


class CallbackResponse(BaseModel):
    token: str
    exp: datetime


class CallbackBody(BaseModel):
    code: str
    callback: str
