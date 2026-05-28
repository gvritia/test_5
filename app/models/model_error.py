from typing import Any

from pydantic import BaseModel


class ErrorResponse(BaseModel):
    detail: Any
