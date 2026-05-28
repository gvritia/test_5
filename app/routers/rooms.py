from typing import Annotated

from fastapi import APIRouter, Path

from app.api_responses import VALIDATION_ERROR
from app.models.model_room_users import RoomUsers
from app.room_manager import room_manager

router = APIRouter(prefix="/rooms", tags=["rooms"])

ROOM_USERS_RESPONSES = {**VALIDATION_ERROR}


@router.get(
    "/{room_id}/users",
    response_model=RoomUsers,
    responses=ROOM_USERS_RESPONSES,
)
def get_room_users(
    room_id: Annotated[str, Path(min_length=1, max_length=80)],
) -> RoomUsers:
    return RoomUsers(room_id=room_id, users=room_manager.get_users(room_id))
