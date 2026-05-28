from typing import Literal

from pydantic import BaseModel, Field


class WebSocketMessage(BaseModel):
    type: Literal["message"]
    text: str = Field(..., min_length=1)
