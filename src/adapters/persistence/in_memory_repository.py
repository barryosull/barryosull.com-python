"""In-memory implementation of the room repository."""

from typing import Optional
from uuid import UUID

from src.domain.entities.game_room import GameRoom
from src.ports.repository_port import RoomRepositoryPort


class InMemoryRoomRepository(RoomRepositoryPort):
    """In-memory implementation of the room repository.

    This adapter stores game rooms in memory using a dictionary.
    Suitable for development and testing.
    """

    def __init__(self) -> None:
        """Initialize the in-memory repository with an empty dictionary."""
        self._rooms: dict[UUID, GameRoom] = {}

    def save(self, room: GameRoom) -> None:
        """Save or update a game room in memory.

        Args:
            room: The game room to save.
        """
        self._rooms[room.room_id] = room

    def find_by_id(self, room_id: UUID) -> Optional[GameRoom]:
        """Find a game room by its ID.

        Args:
            room_id: The unique identifier of the room.

        Returns:
            The GameRoom if found, None otherwise.
        """
        return self._rooms.get(room_id)

    def delete(self, room_id: UUID) -> None:
        """Delete a game room by its ID.

        Args:
            room_id: The unique identifier of the room to delete.
        """
        self._rooms.pop(room_id, None)

    def list_all(self) -> list[GameRoom]:
        """List all game rooms.

        Returns:
            List of all game rooms in the repository.
        """
        return list(self._rooms.values())

    def exists(self, room_id: UUID) -> bool:
        """Check if a room exists.

        Args:
            room_id: The unique identifier of the room.

        Returns:
            True if the room exists, False otherwise.
        """
        return room_id in self._rooms

    def clear(self) -> None:
        """Clear all rooms from the repository.

        Useful for testing and cleanup.
        """
        self._rooms.clear()
