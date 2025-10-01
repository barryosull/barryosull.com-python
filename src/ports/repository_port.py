"""Repository port (interface) for game room persistence."""

from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID

from src.domain.entities.game_room import GameRoom


class RoomRepositoryPort(ABC):
    """Abstract base class defining the repository interface for game rooms.

    This port defines the contract for persisting and retrieving game rooms,
    following the ports and adapters (hexagonal) architecture pattern.
    """

    @abstractmethod
    def save(self, room: GameRoom) -> None:
        """Save or update a game room.

        Args:
            room: The game room to save.
        """
        pass

    @abstractmethod
    def find_by_id(self, room_id: UUID) -> Optional[GameRoom]:
        """Find a game room by its ID.

        Args:
            room_id: The unique identifier of the room.

        Returns:
            The GameRoom if found, None otherwise.
        """
        pass

    @abstractmethod
    def delete(self, room_id: UUID) -> None:
        """Delete a game room by its ID.

        Args:
            room_id: The unique identifier of the room to delete.
        """
        pass

    @abstractmethod
    def list_all(self) -> list[GameRoom]:
        """List all game rooms.

        Returns:
            List of all game rooms in the repository.
        """
        pass

    @abstractmethod
    def exists(self, room_id: UUID) -> bool:
        """Check if a room exists.

        Args:
            room_id: The unique identifier of the room.

        Returns:
            True if the room exists, False otherwise.
        """
        pass
