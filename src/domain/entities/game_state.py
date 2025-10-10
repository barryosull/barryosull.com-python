"""Game state entity for Secret Hitler game."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional
from uuid import UUID

from src.domain.entities.policy_deck import PolicyDeck
from src.domain.value_objects.role import Role

class GamePhase(Enum):
    NOMINATION = "NOMINATION"
    ELECTION = "ELECTION"
    LEGISLATIVE_PRESIDENT = "LEGISLATIVE_PRESIDENT"
    LEGISLATIVE_CHANCELLOR = "LEGISLATIVE_CHANCELLOR"
    EXECUTIVE_ACTION = "EXECUTIVE_ACTION"
    GAME_OVER = "GAME_OVER"


class PresidentialPower(Enum):
    INVESTIGATE_LOYALTY = "INVESTIGATE_LOYALTY"
    CALL_SPECIAL_ELECTION = "CALL_SPECIAL_ELECTION"
    POLICY_PEEK = "POLICY_PEEK"
    EXECUTION = "EXECUTION"


@dataclass
class GameState:
    round_number: int = 1
    president_id: Optional[UUID] = None
    chancellor_id: Optional[UUID] = None
    nominated_chancellor_id: Optional[UUID] = None
    previous_president_id: Optional[UUID] = None
    previous_chancellor_id: Optional[UUID] = None
    next_regular_president_id: Optional[UUID] = None
    veto_requested: bool = False
    policy_deck: PolicyDeck = field(default_factory=PolicyDeck.create_initial_deck)
    liberal_policies: int = 0
    fascist_policies: int = 0
    election_tracker: int = 0
    current_phase: GamePhase = GamePhase.NOMINATION
    role_assignments: dict[UUID, Role] = field(default_factory=dict)
    votes: dict[UUID, bool] = field(default_factory=dict)
    president_policies: list = field(default_factory=list)
    chancellor_policies: list = field(default_factory=list)
    game_over_reason: Optional[str] = None

    def enact_liberal_policy(self) -> None:
        self.liberal_policies += 1
        self.election_tracker = 0

    def enact_fascist_policy(self) -> None:
        self.fascist_policies += 1
        self.election_tracker = 0

    def increment_election_tracker(self) -> None:
        self.election_tracker += 1

    def reset_election_tracker(self) -> None:
        self.election_tracker = 0

    def is_chaos_threshold(self) -> bool:
        return self.election_tracker >= 3

    def get_presidential_power(self, player_count: int) -> Optional[PresidentialPower]:
        if player_count <= 6:
            power_map = {
                3: PresidentialPower.POLICY_PEEK,
                4: PresidentialPower.EXECUTION,
                5: PresidentialPower.EXECUTION,
            }
        elif player_count <= 8:
            power_map = {
                2: PresidentialPower.INVESTIGATE_LOYALTY,
                3: PresidentialPower.CALL_SPECIAL_ELECTION,
                4: PresidentialPower.EXECUTION,
                5: PresidentialPower.EXECUTION,
            }
        else:
            power_map = {
                1: PresidentialPower.INVESTIGATE_LOYALTY,
                2: PresidentialPower.INVESTIGATE_LOYALTY,
                3: PresidentialPower.CALL_SPECIAL_ELECTION,
                4: PresidentialPower.EXECUTION,
                5: PresidentialPower.EXECUTION,
            }

        return power_map.get(self.fascist_policies)

    def liberals_won(self) -> bool:
        return self.liberal_policies >= 5

    def fascists_won(self) -> bool:
        return self.fascist_policies >= 6

    def get_role(self, player_id: UUID) -> Optional[Role]:
        return self.role_assignments.get(player_id)

    def peek_policies(self) -> list:
        return self.policy_deck.peek(3)
    
    def record_previous_president_and_chancellor(self):
        self.previous_president_id = self.president_id
        self.previous_chancellor_id = self.chancellor_id
    
    def move_to_nomination_phase(self, next_president):
        self.current_phase = GamePhase.NOMINATION
        self.president_id = next_president
        self.nominated_chancellor_id = None
        self.chancellor_id = None
        self.votes = {}
