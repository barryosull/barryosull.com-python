from dataclasses import dataclass
from uuid import UUID

from backend.domain.entities.game_state import GamePhase
from backend.domain.services.government_formation_service import GovernmentFormationService
from backend.domain.services.increment_election_service import IncrementElectionService
from backend.ports.room_repository_port import RoomRepositoryPort


@dataclass
class VetoAgendaCommand:
    room_id: UUID
    player_id: UUID
    approve_veto: bool


class VetoAgendaHandler:
    def __init__(self, repository: RoomRepositoryPort) -> None:
        self.repository = repository

    def handle(self, command: VetoAgendaCommand) -> dict | None:
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
        
        result = None

        if is_chancellor:
            if not command.approve_veto:
                raise ValueError("Chancellor cannot reject their own veto request")

            game_state.veto_requested = True

        elif is_president:
            if not game_state.veto_requested:
                raise ValueError("No veto request to respond to")

            if command.approve_veto:
                game_state.policy_deck.discard(game_state.chancellor_policies)
                game_state.chancellor_policies = []
                game_state.president_policies = []
                game_state.veto_requested = False

                result = IncrementElectionService.handle_failed_government(room)
                if (result['type'] != 'chaos'):
                    result['type'] = 'vetoed'
            else:
                game_state.veto_requested = False
                game_state.veto_rejected = True
                result = {
                    'type': 'veto_rejected',
                }

        self.repository.save(room)

        return result
