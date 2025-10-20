"""Repository port (interface) for game room persistence."""

from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID

from backend.domain.entities.game_room import GameRoom


class RoomRepositoryPort(ABC):
    @abstractmethod
    def save(self, room: GameRoom) -> None:
        pass

    @abstractmethod
    def find_by_id(self, room_id: UUID) -> Optional[GameRoom]:
        pass

    @abstractmethod
    def delete(self, room_id: UUID) -> None:
        pass

    @abstractmethod
    def list_all(self) -> list[GameRoom]:
        pass

    @abstractmethod
    def exists(self, room_id: UUID) -> bool:
        pass
