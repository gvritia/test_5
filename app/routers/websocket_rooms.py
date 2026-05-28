from typing import Annotated

from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect, status
from pydantic import ValidationError

from app.models.model_websocket_message import WebSocketMessage
from app.room_manager import room_manager

router = APIRouter(tags=["websocket"])


@router.websocket("/ws/rooms/{room_id}")
async def room_websocket(
    websocket: WebSocket,
    room_id: str,
    username: Annotated[str | None, Query()] = None,
) -> None:
    if username is None or username.strip() == "":
        await websocket.accept()
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    normalized_username = username.strip()
    await room_manager.connect(room_id, normalized_username, websocket)

    try:
        while True:
            payload = await websocket.receive_json()
            try:
                message = WebSocketMessage.model_validate(payload)
            except ValidationError:
                await websocket.send_json(
                    {"type": "error", "detail": "Invalid message format"}
                )
                continue

            if len(message.text) > 300:
                await websocket.send_json(
                    {"type": "error", "detail": "Message is too long"}
                )
                continue

            await room_manager.broadcast(
                room_id,
                {
                    "type": "message",
                    "room_id": room_id,
                    "username": normalized_username,
                    "text": message.text,
                },
            )
    except WebSocketDisconnect:
        room_manager.disconnect(room_id, normalized_username, websocket)
