from dataclasses import dataclass
from uuid import UUID

from src.domain.entities.game_state import GamePhase
from src.domain.services.government_formation_service import GovernmentFormationService
from src.ports.repository_port import RoomRepositoryPort


@dataclass
class NominateChancellorCommand:
    room_id: UUID
    nominating_player_id: UUID
    chancellor_id: UUID


class NominateChancellorHandler:
    def __init__(self, repository: RoomRepositoryPort) -> None:
        self.repository = repository

    def handle(self, command: NominateChancellorCommand) -> None:
        room = self.repository.find_by_id(command.room_id)
        if not room:
            raise ValueError(f"Room {command.room_id} not found")

        if not room.game_state:
            raise ValueError("Game not started")

        game_state = room.game_state

        if game_state.current_phase != GamePhase.NOMINATION:
            raise ValueError(
                f"Cannot nominate chancellor in phase {game_state.current_phase.value}"
            )

        if game_state.president_id != command.nominating_player_id:
            raise ValueError("Only the president can nominate a chancellor")

        can_nominate, error_msg = GovernmentFormationService.can_nominate_chancellor(
            game_state, command.chancellor_id, room.active_players()
        )

        if not can_nominate:
            raise ValueError(error_msg)

        game_state.nominated_chancellor_id = command.chancellor_id
        game_state.current_phase = GamePhase.ELECTION
        game_state.votes = {}

        self.repository.save(room)
