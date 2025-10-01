"""In-memory implementation of the room repository."""

from typing import Optional
from uuid import UUID

from src.domain.entities.game_room import GameRoom
from src.ports.repository_port import RoomRepositoryPort


class InMemoryRoomRepository(RoomRepositoryPort):
    def __init__(self) -> None:
        self._rooms: dict[UUID, GameRoom] = {}

    def save(self, room: GameRoom) -> None:
        self._rooms[room.room_id] = room

    def find_by_id(self, room_id: UUID) -> Optional[GameRoom]:
        return self._rooms.get(room_id)

    def delete(self, room_id: UUID) -> None:
        self._rooms.pop(room_id, None)

    def list_all(self) -> list[GameRoom]:
        return list(self._rooms.values())

    def exists(self, room_id: UUID) -> bool:
        return room_id in self._rooms

    def clear(self) -> None:
        self._rooms.clear()
