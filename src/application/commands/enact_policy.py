from dataclasses import dataclass
from uuid import UUID

from src.domain.entities.game_state import GamePhase
from src.domain.services.government_formation_service import GovernmentFormationService
from src.domain.services.policy_enactment_service import PolicyEnactmentService
from src.domain.services.win_condition_service import WinConditionService
from src.domain.value_objects.policy import PolicyType
from src.ports.room_repository_port import RoomRepositoryPort


@dataclass
class EnactPolicyCommand:
    room_id: UUID
    player_id: UUID
    policy_type: PolicyType


class EnactPolicyHandler:
    def __init__(self, repository: RoomRepositoryPort) -> None:
        self.repository = repository

    def handle(self, command: EnactPolicyCommand) -> None:
        room = self.repository.find_by_id(command.room_id)
        if not room:
            raise ValueError(f"Room {command.room_id} not found")

        if not room.game_state:
            raise ValueError("Game not started")

        game_state = room.game_state

        if game_state.current_phase != GamePhase.LEGISLATIVE_CHANCELLOR:
            raise ValueError(
                f"Cannot enact policy in phase {game_state.current_phase.value}"
            )

        if game_state.chancellor_id != command.player_id:
            raise ValueError("Only the chancellor can enact a policy")

        policy = next(
            (p for p in game_state.chancellor_policies if p.type == command.policy_type),
            None,
        )
        if not policy:
            raise ValueError(
                f"Policy {command.policy_type.value} not found in chancellor policies"
            )

        enacted_policy = PolicyEnactmentService.chancellor_enacts_policy(
            game_state, game_state.chancellor_policies, policy
        )

        game_state.chancellor_policies = []

        is_game_over, winning_team, reason = WinConditionService.check_game_over(
            game_state
        )

        if is_game_over:
            game_state.current_phase = GamePhase.GAME_OVER
            game_state.game_over_reason = f"{winning_team.value.title()}s win! {reason}"
            room.end_game()
        else:
            from src.domain.value_objects.policy import PolicyType

            presidential_power = game_state.get_presidential_power(
                len(room.active_players())
            )

            if presidential_power and enacted_policy.type == PolicyType.FASCIST:
                game_state.current_phase = GamePhase.EXECUTIVE_ACTION
            else:
                if game_state.next_regular_president_id:
                    next_president = game_state.next_regular_president_id
                    game_state.next_regular_president_id = None
                else:
                    next_president = GovernmentFormationService.advance_president(
                        game_state.president_id, room.active_players()
                    )
                game_state.record_previous_president_and_chancellor()
                game_state.move_to_nomination_phase(next_president)

        self.repository.save(room)
