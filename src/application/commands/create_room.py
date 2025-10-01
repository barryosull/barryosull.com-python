"""Command for creating a new game room."""

from dataclasses import dataclass
from uuid import UUID

from src.domain.entities.game_room import GameRoom
from src.domain.entities.player import Player
from src.ports.repository_port import RoomRepositoryPort


@dataclass
class CreateRoomCommand:
    """Command to create a new game room.

    Attributes:
        player_name: Name of the player creating the room.
    """

    player_name: str


@dataclass
class CreateRoomResult:
    """Result of creating a game room.

    Attributes:
        room_id: ID of the created room.
        player_id: ID of the creator player.
    """

    room_id: UUID
    player_id: UUID


class CreateRoomHandler:
    """Handler for the CreateRoomCommand.

    This handler creates a new game room with the creator as the first player.
    """

    def __init__(self, repository: RoomRepositoryPort) -> None:
        """Initialize the handler with a repository.

        Args:
            repository: The room repository for persistence.
        """
        self._repository = repository

    def handle(self, command: CreateRoomCommand) -> CreateRoomResult:
        """Handle the create room command.

        Args:
            command: The create room command.

        Returns:
            Result containing the room ID and creator player ID.

        Raises:
            ValueError: If player name is empty.
        """
        if not command.player_name or not command.player_name.strip():
            raise ValueError("Player name cannot be empty")

        # Create the room
        room = GameRoom()

        # Create the creator player
        creator = Player(name=command.player_name.strip())

        # Add creator to the room
        room.add_player(creator)

        # Save the room
        self._repository.save(room)

        return CreateRoomResult(room_id=room.room_id, player_id=creator.player_id)
