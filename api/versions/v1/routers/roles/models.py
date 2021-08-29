from typing import List, Optional
from pydantic import BaseModel, Field


class RoleResponse(BaseModel):
    id: str
    name: str
    position: int
    permissions: int
    color: Optional[int]


class DetailedRoleResponse(RoleResponse):
    members: List[str]


class NewRoleBody(BaseModel):
    name: str = Field(object, min_length=4, max_length=64)
    color: int = Field(None, le=0xFFFFFF, ge=0)
    permissions: int = Field(0)


class UpdateRoleBody(BaseModel):
    name: str = Field(object, min_length=4, max_length=64)
    color: int = Field(object, le=0xFFFFFF, ge=0)
    permissions: int = Field(object)
    position: int = Field(object)
