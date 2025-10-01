"""Player entity for Secret Hitler game."""

from dataclasses import dataclass, field
from uuid import UUID, uuid4


@dataclass
class Player:
    """Entity representing a player in the game.

    Attributes:
        player_id: Unique identifier for the player.
        name: Display name of the player.
        is_connected: Whether the player is currently connected.
        is_alive: Whether the player is alive (can be killed by execution).
    """

    player_id: UUID = field(default_factory=uuid4)
    name: str = ""
    is_connected: bool = True
    is_alive: bool = True

    def disconnect(self) -> None:
        self.is_connected = False

    def reconnect(self) -> None:
        self.is_connected = True

    def kill(self) -> None:
        self.is_alive = False

    def can_participate(self) -> bool:
        return self.is_alive and self.is_connected

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Player):
            return False
        return self.player_id == other.player_id

    def __hash__(self) -> int:
        return hash(self.player_id)
