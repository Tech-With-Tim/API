from typing import Optional
from pydantic import BaseModel, HttpUrl


class ChallengeLanguageResponse(BaseModel):
    id: str
    name: str
    download_url: Optional[HttpUrl]
    disabled: bool = False
    piston_lang: str
    piston_lang_ver: str


class NewChallengeLanguageBody(BaseModel):
    name: str
    download_url: Optional[HttpUrl] = None
    disabled: bool = False
    piston_lang: str
    piston_lang_ver: str


class UpdateChallengeLanguageBody(BaseModel):
    name: str = ""
    download_url: Optional[HttpUrl] = None
    disabled: bool = False
    piston_lang: str = ""
    piston_lang_ver: str = ""
