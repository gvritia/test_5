from typing import Literal

from pydantic import BaseModel, Field


class User(BaseModel):
    id: int = Field(..., ge=1)
    role: Literal["user", "admin"] = "user"
