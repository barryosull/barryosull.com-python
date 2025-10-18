"""Command for joining an existing game room."""

from dataclasses import dataclass
from uuid import UUID

from src.domain.entities.player import Player
from src.ports.room_repository_port import RoomRepositoryPort


@dataclass
class JoinRoomCommand:
    room_id: UUID
    player_name: str


@dataclass
class JoinRoomResult:
    player_id: UUID


class JoinRoomHandler:
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
