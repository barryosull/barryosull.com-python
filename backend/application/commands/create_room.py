"""Command for creating a new game room."""

from dataclasses import dataclass
from uuid import UUID

from backend.domain.entities.game_room import GameRoom
from backend.domain.entities.player import Player
from backend.ports.room_repository_port import RoomRepositoryPort


@dataclass
class CreateRoomCommand:
    player_name: str


@dataclass
class CreateRoomResult:
    room_id: UUID
    player_id: UUID


class CreateRoomHandler:
    def __init__(self, repository: RoomRepositoryPort) -> None:
        self._repository = repository

    def handle(self, command: CreateRoomCommand) -> CreateRoomResult:
        if not command.player_name or not command.player_name.strip():
            raise ValueError("Player name cannot be empty")

        room = GameRoom()
        creator = Player(name=command.player_name.strip())
        room.add_player(creator)
        self._repository.save(room)

        return CreateRoomResult(room_id=room.room_id, player_id=creator.player_id)
