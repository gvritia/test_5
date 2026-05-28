from fastapi import WebSocket


class RoomManager:
    def __init__(self) -> None:
        self._rooms: dict[str, dict[str, list[WebSocket]]] = {}

    def clear(self) -> None:
        self._rooms.clear()

    async def connect(self, room_id: str, username: str, websocket: WebSocket) -> None:
        await websocket.accept()
        room = self._rooms.setdefault(room_id, {})
        room.setdefault(username, []).append(websocket)
        await self.broadcast(
            room_id,
            {"type": "join", "room_id": room_id, "username": username},
        )

    def disconnect(self, room_id: str, username: str, websocket: WebSocket) -> None:
        room = self._rooms.get(room_id)
        if room is None:
            return

        connections = room.get(username)
        if connections is None:
            return

        if websocket in connections:
            connections.remove(websocket)
        if not connections:
            del room[username]
        if not room:
            del self._rooms[room_id]

    async def broadcast(self, room_id: str, payload: dict) -> None:
        room = self._rooms.get(room_id, {})
        connections = [
            websocket
            for user_connections in room.values()
            for websocket in user_connections
        ]
        for websocket in connections:
            await websocket.send_json(payload)

    def get_users(self, room_id: str) -> list[str]:
        return sorted(self._rooms.get(room_id, {}).keys())


room_manager = RoomManager()
