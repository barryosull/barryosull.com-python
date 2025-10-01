"""Game room entity for Secret Hitler game."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4

from src.domain.entities.game_state import GameState
from src.domain.entities.player import Player


class RoomStatus(Enum):
    WAITING = "WAITING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"


@dataclass
class GameRoom:
    room_id: UUID = field(default_factory=uuid4)
    creator_id: Optional[UUID] = None
    status: RoomStatus = RoomStatus.WAITING
    players: list[Player] = field(default_factory=list)
    game_state: Optional[GameState] = None
    created_at: datetime = field(default_factory=datetime.utcnow)

    def add_player(self, player: Player) -> None:
        if self.status != RoomStatus.WAITING:
            raise ValueError("Cannot add players to a game in progress")

        if any(p.player_id == player.player_id for p in self.players):
            raise ValueError("Player already in room")

        self.players.append(player)

        if self.creator_id is None:
            self.creator_id = player.player_id

    def remove_player(self, player_id: UUID) -> None:
        if self.status != RoomStatus.WAITING:
            raise ValueError("Cannot remove players from a game in progress")

        self.players = [p for p in self.players if p.player_id != player_id]

        if self.creator_id == player_id and self.players:
            self.creator_id = self.players[0].player_id

    def get_player(self, player_id: UUID) -> Optional[Player]:
        return next((p for p in self.players if p.player_id == player_id), None)

    def player_count(self) -> int:
        return len(self.players)

    def can_start_game(self) -> bool:
        return self.status == RoomStatus.WAITING and self.player_count() >= 5

    def start_game(self, game_state: GameState) -> None:
        if not self.can_start_game():
            raise ValueError(
                "Cannot start game. Need at least 5 players and room must be waiting"
            )

        self.game_state = game_state
        self.status = RoomStatus.IN_PROGRESS

    def end_game(self) -> None:
        self.status = RoomStatus.COMPLETED

    def is_creator(self, player_id: UUID) -> bool:
        return self.creator_id == player_id

    def active_players(self) -> list[Player]:
        return [p for p in self.players if p.can_participate()]

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, GameRoom):
            return False
        return self.room_id == other.room_id

    def __hash__(self) -> int:
        return hash(self.room_id)
