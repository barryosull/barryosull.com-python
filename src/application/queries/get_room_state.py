"""Query for retrieving game room state."""

from dataclasses import dataclass
from typing import Optional
from uuid import UUID

from src.domain.entities.game_room import GameRoom, RoomStatus
from src.ports.repository_port import RoomRepositoryPort


@dataclass
class PlayerDTO:
    """Data transfer object for player information.

    Attributes:
        player_id: ID of the player.
        name: Name of the player.
        is_connected: Whether the player is connected.
        is_alive: Whether the player is alive.
    """

    player_id: UUID
    name: str
    is_connected: bool
    is_alive: bool


@dataclass
class RoomStateDTO:
    """Data transfer object for room state information.

    Attributes:
        room_id: ID of the room.
        status: Current status of the room.
        creator_id: ID of the room creator.
        players: List of players in the room.
        player_count: Number of players in the room.
        can_start: Whether the game can be started.
        created_at: When the room was created.
    """

    room_id: UUID
    status: str
    creator_id: Optional[UUID]
    players: list[PlayerDTO]
    player_count: int
    can_start: bool
    created_at: str


@dataclass
class GetRoomStateQuery:
    """Query to get the state of a game room.

    Attributes:
        room_id: ID of the room to retrieve.
    """

    room_id: UUID


class GetRoomStateHandler:
    """Handler for the GetRoomStateQuery.

    This handler retrieves the current state of a game room.
    """

    def __init__(self, repository: RoomRepositoryPort) -> None:
        self._repository = repository

    def handle(self, query: GetRoomStateQuery) -> RoomStateDTO:
        room = self._repository.find_by_id(query.room_id)
        if room is None:
            raise ValueError(f"Room {query.room_id} not found")

        return self._to_dto(room)

    def _to_dto(self, room: GameRoom) -> RoomStateDTO:
        player_dtos = [
            PlayerDTO(
                player_id=player.player_id,
                name=player.name,
                is_connected=player.is_connected,
                is_alive=player.is_alive,
            )
            for player in room.players
        ]

        return RoomStateDTO(
            room_id=room.room_id,
            status=room.status.value,
            creator_id=room.creator_id,
            players=player_dtos,
            player_count=room.player_count(),
            can_start=room.can_start_game(),
            created_at=room.created_at.isoformat(),
        )
