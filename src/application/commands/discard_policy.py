from dataclasses import dataclass
from uuid import UUID

from src.domain.entities.game_state import GamePhase
from src.domain.services.policy_enactment_service import PolicyEnactmentService
from src.domain.value_objects.policy import PolicyType
from src.ports.room_repository_port import RoomRepositoryPort


@dataclass
class DiscardPolicyCommand:
    room_id: UUID
    player_id: UUID
    policy_type: PolicyType

class DiscardPolicyHandler:
    def __init__(self, repository: RoomRepositoryPort) -> None:
        self.repository = repository

    def handle(self, command: DiscardPolicyCommand) -> None:
        room = self.repository.find_by_id(command.room_id)
        if not room:
            raise ValueError(f"Room {command.room_id} not found")

        if not room.game_state:
            raise ValueError("Game not started")

        game_state = room.game_state

        if game_state.current_phase != GamePhase.LEGISLATIVE_PRESIDENT:
            raise ValueError(
                f"Cannot discard policy in phase {game_state.current_phase.value}"
            )

        if game_state.president_id != command.player_id:
            raise ValueError("Only the president can discard a policy")

        policy = next(
            (p for p in game_state.president_policies if p.type == command.policy_type),
            None
        )
        if not policy:
            raise ValueError(f"Policy {command.policy_type.value} not found in president policies")

        print("Pre-discard: ", game_state.president_policies, policy)
        remaining = PolicyEnactmentService.president_discards_policy(
            game_state.president_policies, policy
        )
        print("Post-discard: ", remaining)

        game_state.policy_deck.discard([policy])
        game_state.chancellor_policies = remaining
        game_state.president_policies = []
        game_state.current_phase = GamePhase.LEGISLATIVE_CHANCELLOR

        self.repository.save(room)
