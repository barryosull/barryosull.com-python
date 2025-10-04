from dataclasses import dataclass
from uuid import UUID

from src.domain.entities.game_state import GamePhase
from src.domain.services.government_formation_service import GovernmentFormationService
from src.domain.services.policy_enactment_service import PolicyEnactmentService
from src.domain.services.win_condition_service import WinConditionService
from src.domain.value_objects.policy import Policy
from src.ports.repository_port import RoomRepositoryPort


@dataclass
class EnactPolicyCommand:
    room_id: UUID
    player_id: UUID
    enacted_policy: Policy


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

        PolicyEnactmentService.chancellor_enacts_policy(
            game_state, game_state.chancellor_policies, command.enacted_policy
        )

        game_state.chancellor_policies = []

        is_game_over, winning_team, _ = WinConditionService.check_game_over(
            game_state
        )

        if is_game_over:
            game_state.current_phase = GamePhase.GAME_OVER
            room.end_game()
        else:
            presidential_power = game_state.get_presidential_power(
                len(room.active_players())
            )

            if presidential_power:
                game_state.current_phase = GamePhase.EXECUTIVE_ACTION
            else:
                game_state.current_phase = GamePhase.NOMINATION

                active_players = room.active_players()
                next_president = GovernmentFormationService.advance_president(
                    game_state.president_id, active_players
                )

                game_state.previous_president_id = game_state.president_id
                game_state.previous_chancellor_id = game_state.chancellor_id

                game_state.president_id = next_president
                game_state.chancellor_id = None
                game_state.nominated_chancellor_id = None

        self.repository.save(room)
