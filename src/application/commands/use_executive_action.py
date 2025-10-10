from dataclasses import dataclass
from uuid import UUID

from src.domain.entities.game_state import GamePhase, PresidentialPower
from src.domain.services.government_formation_service import GovernmentFormationService
from src.ports.repository_port import RoomRepositoryPort


@dataclass
class UseExecutiveActionCommand:
    room_id: UUID
    player_id: UUID
    target_player_id: UUID | None = None


class UseExecutiveActionHandler:
    def __init__(self, repository: RoomRepositoryPort) -> None:
        self.repository = repository

    def handle(self, command: UseExecutiveActionCommand) -> dict:
        room = self.repository.find_by_id(command.room_id)
        if not room:
            raise ValueError(f"Room {command.room_id} not found")

        if not room.game_state:
            raise ValueError("Game not started")

        game_state = room.game_state

        if game_state.current_phase != GamePhase.EXECUTIVE_ACTION:
            raise ValueError(
                f"Cannot use executive action in phase {game_state.current_phase.value}"
            )

        if game_state.president_id != command.player_id:
            raise ValueError("Only the president can use executive actions")

        presidential_power = game_state.get_presidential_power(
            len(room.active_players())
        )

        if not presidential_power:
            raise ValueError("No presidential power available")

        result = {}

        if presidential_power == PresidentialPower.INVESTIGATE_LOYALTY:
            if not command.target_player_id:
                raise ValueError("Target player required for loyalty investigation")

            if command.target_player_id == command.player_id:
                raise ValueError("Cannot investigate yourself")

            if command.target_player_id in game_state.investigated_players:
                raise ValueError("This player has already been investigated")

            target_role = game_state.role_assignments.get(command.target_player_id)
            if not target_role:
                raise ValueError("Target player not found in game")

            game_state.investigated_players.add(command.target_player_id)
            result = {}

        elif presidential_power == PresidentialPower.POLICY_PEEK:
            result = {}

        elif presidential_power == PresidentialPower.EXECUTION:
            if not command.target_player_id:
                raise ValueError("Target player required for execution")

            target_player = room.get_player(command.target_player_id)
            if not target_player:
                raise ValueError("Target player not found")

            if not target_player.is_alive:
                raise ValueError("Target player is already dead")

            target_player.kill()

            target_role = game_state.role_assignments.get(command.target_player_id)
            result = {"executed_player_id": str(command.target_player_id)}

            if target_role and target_role.is_hitler:
                game_state.current_phase = GamePhase.GAME_OVER
                game_state.game_over_reason = "Liberals win! Hitler was executed."
                room.end_game()
                result["game_over"] = True
                result["winning_team"] = "LIBERAL"
                self.repository.save(room)
                return result

        elif presidential_power == PresidentialPower.CALL_SPECIAL_ELECTION:
            if not command.target_player_id:
                raise ValueError("Target player required for special election")

            target_player = room.get_player(command.target_player_id)
            if not target_player:
                raise ValueError("Target player not found")

            if not target_player.can_participate():
                raise ValueError("Target player cannot participate")

            next_regular_president = GovernmentFormationService.advance_president(
                game_state.president_id, room.active_players()
            )
            game_state.next_regular_president_id = next_regular_president
            game_state.move_to_nomination_phase(command.target_player_id)

            self.repository.save(room)
            return result

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
        return result
