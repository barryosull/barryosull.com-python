"""Game state entity for Secret Hitler game."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional
from uuid import UUID

from src.domain.entities.player import Player
from src.domain.entities.policy_deck import PolicyDeck
from src.domain.value_objects.role import Role


class GamePhase(Enum):
    """Enum representing the current phase of the game."""

    NOMINATION = "NOMINATION"
    ELECTION = "ELECTION"
    LEGISLATIVE_PRESIDENT = "LEGISLATIVE_PRESIDENT"
    LEGISLATIVE_CHANCELLOR = "LEGISLATIVE_CHANCELLOR"
    EXECUTIVE_ACTION = "EXECUTIVE_ACTION"
    GAME_OVER = "GAME_OVER"


class PresidentialPower(Enum):
    """Enum representing presidential powers triggered by fascist policies."""

    INVESTIGATE_LOYALTY = "INVESTIGATE_LOYALTY"
    CALL_SPECIAL_ELECTION = "CALL_SPECIAL_ELECTION"
    POLICY_PEEK = "POLICY_PEEK"
    EXECUTION = "EXECUTION"


@dataclass
class GameState:
    """Entity representing the current state of an active game.

    Attributes:
        round_number: Current round number.
        president_id: ID of the current president.
        chancellor_id: ID of the current chancellor (None if not yet elected).
        nominated_chancellor_id: ID of the nominated chancellor during election.
        previous_president_id: ID of the previous president.
        previous_chancellor_id: ID of the previous chancellor.
        policy_deck: The policy deck for the game.
        liberal_policies: Number of liberal policies enacted (0-5).
        fascist_policies: Number of fascist policies enacted (0-6).
        election_tracker: Number of consecutive failed elections (0-3).
        current_phase: The current phase of the game.
        role_assignments: Mapping of player IDs to their roles.
        votes: Mapping of player IDs to their votes (during election phase).
        president_policies: Policies held by president during legislative session.
        chancellor_policies: Policies held by chancellor during legislative session.
    """

    round_number: int = 1
    president_id: Optional[UUID] = None
    chancellor_id: Optional[UUID] = None
    nominated_chancellor_id: Optional[UUID] = None
    previous_president_id: Optional[UUID] = None
    previous_chancellor_id: Optional[UUID] = None
    policy_deck: PolicyDeck = field(default_factory=PolicyDeck.create_initial_deck)
    liberal_policies: int = 0
    fascist_policies: int = 0
    election_tracker: int = 0
    current_phase: GamePhase = GamePhase.NOMINATION
    role_assignments: dict[UUID, Role] = field(default_factory=dict)
    votes: dict[UUID, bool] = field(default_factory=dict)
    president_policies: list = field(default_factory=list)
    chancellor_policies: list = field(default_factory=list)

    def enact_liberal_policy(self) -> None:
        """Enact a liberal policy.

        Increments the liberal policy track and resets the election tracker.
        """
        self.liberal_policies += 1
        self.election_tracker = 0

    def enact_fascist_policy(self) -> None:
        """Enact a fascist policy.

        Increments the fascist policy track and resets the election tracker.
        """
        self.fascist_policies += 1
        self.election_tracker = 0

    def increment_election_tracker(self) -> None:
        """Increment the failed election tracker.

        If the tracker reaches 3, a chaos policy should be enacted.
        """
        self.election_tracker += 1

    def reset_election_tracker(self) -> None:
        """Reset the failed election tracker to 0."""
        self.election_tracker = 0

    def is_chaos_threshold(self) -> bool:
        """Check if the election tracker has reached the chaos threshold.

        Returns:
            True if election tracker is 3, False otherwise.
        """
        return self.election_tracker >= 3

    def get_presidential_power(self, player_count: int) -> Optional[PresidentialPower]:
        """Get the presidential power triggered by the current fascist policy count.

        The power triggered depends on both the fascist policy position and player count.

        Args:
            player_count: Total number of players in the game.

        Returns:
            The PresidentialPower to be used, or None if no power is triggered.
        """
        if player_count <= 6:
            power_map = {
                3: PresidentialPower.POLICY_PEEK,
                4: PresidentialPower.EXECUTION,
                5: PresidentialPower.EXECUTION,
            }
        elif player_count <= 8:
            power_map = {
                1: PresidentialPower.INVESTIGATE_LOYALTY,
                2: PresidentialPower.CALL_SPECIAL_ELECTION,
                3: PresidentialPower.POLICY_PEEK,
                4: PresidentialPower.EXECUTION,
                5: PresidentialPower.EXECUTION,
            }
        else:  # 9-10 players
            power_map = {
                1: PresidentialPower.INVESTIGATE_LOYALTY,
                2: PresidentialPower.INVESTIGATE_LOYALTY,
                3: PresidentialPower.CALL_SPECIAL_ELECTION,
                4: PresidentialPower.EXECUTION,
                5: PresidentialPower.EXECUTION,
            }

        return power_map.get(self.fascist_policies)

    def liberals_won(self) -> bool:
        """Check if the liberals have won.

        Returns:
            True if 5 liberal policies enacted, False otherwise.
        """
        return self.liberal_policies >= 5

    def fascists_won(self) -> bool:
        """Check if the fascists have won.

        Returns:
            True if 6 fascist policies enacted, False otherwise.
        """
        return self.fascist_policies >= 6

    def get_role(self, player_id: UUID) -> Optional[Role]:
        """Get the role of a specific player.

        Args:
            player_id: The ID of the player.

        Returns:
            The Role of the player, or None if not found.
        """
        return self.role_assignments.get(player_id)
