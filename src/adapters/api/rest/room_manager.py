
from uuid import UUID
from fastapi import WebSocket


class RoomManager:

    rooms: dict[str, list[WebSocket]]

    def __init__(self):
        self.rooms = {}

    async def connect(self, websocket: WebSocket, room_id: UUID):
        await websocket.accept()
        self.rooms[room_id] = self.rooms[room_id] if room_id in self.rooms else []
        self.rooms[room_id].append(websocket)
        print(f"WebSocket Connected to room {room_id}")

    def disconnect(self, websocket: WebSocket, room_id: UUID):
        print(f"WebSocket disconnected for room {room_id}")
        self.rooms[room_id].remove(websocket)
        if len(self.rooms[room_id]) == 0:
            del self.rooms[room_id]
    

    async def broadcast(self, room_id: UUID, payload: dict):
        connections = self.rooms.get(room_id)
        if (connections is None):
            return
        
        for connection in connections:
            await connection.send_json(payload)