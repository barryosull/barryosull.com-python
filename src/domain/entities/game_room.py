"""Game room entity for Secret Hitler game."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4

from src.domain.entities.game_state import GameState
from src.domain.entities.player import Player


class RoomStatus(Enum):
    """Enum representing the status of a game room."""

    WAITING = "WAITING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"


@dataclass
class GameRoom:
    """Entity representing a game room (aggregate root).

    A game room is the main aggregate that contains players and manages
    the game lifecycle from creation through completion.

    Attributes:
        room_id: Unique identifier for the room.
        creator_id: ID of the player who created the room.
        status: Current status of the room.
        players: List of players in the room.
        game_state: Current game state (None if game hasn't started).
        created_at: Timestamp when the room was created.
    """

    room_id: UUID = field(default_factory=uuid4)
    creator_id: Optional[UUID] = None
    status: RoomStatus = RoomStatus.WAITING
    players: list[Player] = field(default_factory=list)
    game_state: Optional[GameState] = None
    created_at: datetime = field(default_factory=datetime.utcnow)

    def add_player(self, player: Player) -> None:
        """Add a player to the room.

        Args:
            player: The player to add.

        Raises:
            ValueError: If the player is already in the room or game has started.
        """
        if self.status != RoomStatus.WAITING:
            raise ValueError("Cannot add players to a game in progress")

        if any(p.player_id == player.player_id for p in self.players):
            raise ValueError("Player already in room")

        self.players.append(player)

        # Set creator_id if this is the first player
        if self.creator_id is None:
            self.creator_id = player.player_id

    def remove_player(self, player_id: UUID) -> None:
        """Remove a player from the room.

        Args:
            player_id: ID of the player to remove.

        Raises:
            ValueError: If game has started or player not found.
        """
        if self.status != RoomStatus.WAITING:
            raise ValueError("Cannot remove players from a game in progress")

        self.players = [p for p in self.players if p.player_id != player_id]

        # Transfer creator role if creator left and there are still players
        if self.creator_id == player_id and self.players:
            self.creator_id = self.players[0].player_id

    def get_player(self, player_id: UUID) -> Optional[Player]:
        """Get a player by their ID.

        Args:
            player_id: The ID of the player to find.

        Returns:
            The Player if found, None otherwise.
        """
        return next((p for p in self.players if p.player_id == player_id), None)

    def player_count(self) -> int:
        """Get the number of players in the room.

        Returns:
            Number of players in the room.
        """
        return len(self.players)

    def can_start_game(self) -> bool:
        """Check if the game can be started.

        A game can start if there are at least 5 players and the room is waiting.

        Returns:
            True if the game can start, False otherwise.
        """
        return self.status == RoomStatus.WAITING and self.player_count() >= 5

    def start_game(self, game_state: GameState) -> None:
        """Start the game with the given initial game state.

        Args:
            game_state: The initial game state with roles assigned.

        Raises:
            ValueError: If the game cannot be started.
        """
        if not self.can_start_game():
            raise ValueError(
                "Cannot start game. Need at least 5 players and room must be waiting"
            )

        self.game_state = game_state
        self.status = RoomStatus.IN_PROGRESS

    def end_game(self) -> None:
        """Mark the game as completed."""
        self.status = RoomStatus.COMPLETED

    def is_creator(self, player_id: UUID) -> bool:
        """Check if a player is the room creator.

        Args:
            player_id: The ID of the player to check.

        Returns:
            True if the player is the creator, False otherwise.
        """
        return self.creator_id == player_id

    def active_players(self) -> list[Player]:
        """Get list of players who can participate (alive and connected).

        Returns:
            List of active players.
        """
        return [p for p in self.players if p.can_participate()]

    def __eq__(self, other: object) -> bool:
        """Check equality based on room_id.

        Args:
            other: The object to compare with.

        Returns:
            True if both rooms have the same room_id, False otherwise.
        """
        if not isinstance(other, GameRoom):
            return False
        return self.room_id == other.room_id

    def __hash__(self) -> int:
        """Generate hash based on room_id.

        Returns:
            Hash value based on room_id.
        """
        return hash(self.room_id)
