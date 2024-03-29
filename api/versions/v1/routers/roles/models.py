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
    name: str = Field(..., min_length=4, max_length=32)
    color: Optional[int] = Field(None, le=0xFFFFFF, ge=0)
    permissions: Optional[int] = Field(0, ge=0)


class UpdateRoleBody(BaseModel):
    name: str = Field("", min_length=4, max_length=64)
    color: Optional[int] = Field(None, le=0xFFFFFF, ge=0)
    permissions: int = Field(0, ge=0)
    position: int = Field(0, ge=0)
