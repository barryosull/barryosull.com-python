"""Command for joining an existing game room."""

from dataclasses import dataclass
from uuid import UUID

from src.domain.entities.player import Player
from src.ports.repository_port import RoomRepositoryPort


@dataclass
class JoinRoomCommand:
    """Command to join an existing game room.

    Attributes:
        room_id: ID of the room to join.
        player_name: Name of the player joining.
    """

    room_id: UUID
    player_name: str


@dataclass
class JoinRoomResult:
    """Result of joining a game room.

    Attributes:
        player_id: ID of the player who joined.
    """

    player_id: UUID


class JoinRoomHandler:
    """Handler for the JoinRoomCommand.

    This handler adds a player to an existing game room.
    """

    def __init__(self, repository: RoomRepositoryPort) -> None:
        self._repository = repository

    def handle(self, command: JoinRoomCommand) -> JoinRoomResult:
        if not command.player_name or not command.player_name.strip():
            raise ValueError("Player name cannot be empty")

        room = self._repository.find_by_id(command.room_id)
        if room is None:
            raise ValueError(f"Room {command.room_id} not found")

        player = Player(name=command.player_name.strip())
        room.add_player(player)
        self._repository.save(room)

        return JoinRoomResult(player_id=player.player_id)
