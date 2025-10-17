from dataclasses import dataclass
from uuid import UUID

from src.ports.repository_port import RoomRepositoryPort


@dataclass
class ReorderPlayersCommand:
    room_id: UUID
    requester_id: UUID
    player_ids: list[UUID]


class ReorderPlayersHandler:
    def __init__(self, repository: RoomRepositoryPort) -> None:
        self._repository = repository

    def handle(self, command: ReorderPlayersCommand) -> None:
        room = self._repository.find_by_id(command.room_id)
        if room is None:
            raise ValueError(f"Room {command.room_id} not found")

        if not room.is_creator(command.requester_id):
            raise ValueError("Only the room creator can reorder players")

        room.reorder_players(command.player_ids)
        self._repository.save(room)
