from dataclasses import dataclass
from uuid import UUID

from src.domain.entities.game_state import GamePhase
from src.domain.services.government_formation_service import GovernmentFormationService
from src.ports.repository_port import RoomRepositoryPort


@dataclass
class VetoAgendaCommand:
    room_id: UUID
    player_id: UUID
    approve_veto: bool


class VetoAgendaHandler:
    def __init__(self, repository: RoomRepositoryPort) -> None:
        self.repository = repository

    def handle(self, command: VetoAgendaCommand) -> None:
        room = self.repository.find_by_id(command.room_id)
        if not room:
            raise ValueError(f"Room {command.room_id} not found")

        if not room.game_state:
            raise ValueError("Game not started")

        game_state = room.game_state

        if game_state.current_phase != GamePhase.LEGISLATIVE_CHANCELLOR:
            raise ValueError(
                f"Cannot veto in phase {game_state.current_phase.value}"
            )

        if game_state.fascist_policies < 5:
            raise ValueError("Veto power is not available until 5 fascist policies are enacted")

        is_chancellor = game_state.chancellor_id == command.player_id
        is_president = game_state.president_id == command.player_id

        if not (is_chancellor or is_president):
            raise ValueError("Only the president or chancellor can respond to veto")

        if is_chancellor and not command.approve_veto:
            raise ValueError("Chancellor initiated veto, cannot reject")

        if is_chancellor:
            
            game_state.chancellor_policies = []
            game_state.president_policies = []
            game_state.increment_election_tracker()

            next_president = GovernmentFormationService.advance_president(
                game_state.president_id, room.active_players()
            )
            game_state.record_previous_president_and_chancellor()
            game_state.move_to_nomination_phase(next_president)

        elif is_president:
            if not command.approve_veto:
                raise ValueError("President rejected veto - chancellor must enact policy")

            game_state.policy_deck.discard(game_state.chancellor_policies)
            game_state.chancellor_policies = []
            game_state.president_policies = []
            game_state.increment_election_tracker()

            next_president = GovernmentFormationService.advance_president(
                game_state.president_id, room.active_players()
            )
            game_state.record_previous_president_and_chancellor()
            game_state.move_to_nomination_phase(next_president)

        self.repository.save(room)
