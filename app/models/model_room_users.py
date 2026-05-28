from pydantic import BaseModel, Field


class RoomUsers(BaseModel):
    room_id: str = Field(..., min_length=1, max_length=80)
    users: list[str]
