from typing import List
from pydantic import BaseModel


class UserResponse(BaseModel):
    id: str
    username: str
    discriminator: str
    avatar: str
    app: bool
    roles: List[str]
