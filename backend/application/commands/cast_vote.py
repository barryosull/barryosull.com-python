from dataclasses import dataclass
from uuid import UUID

from backend.domain.entities.game_state import GamePhase
from backend.domain.services.government_formation_service import GovernmentFormationService
from backend.domain.services.increment_election_service import IncrementElectionService
from backend.domain.services.policy_enactment_service import PolicyEnactmentService
from backend.ports.room_repository_port import RoomRepositoryPort


@dataclass
class CastVoteCommand:
    room_id: UUID
    player_id: UUID
    vote: bool


class CastVoteHandler:
    def __init__(self, repository: RoomRepositoryPort) -> None:
        self.repository = repository

    def handle(self, command: CastVoteCommand) -> None:
        room = self.repository.find_by_id(command.room_id)
        if not room:
            raise ValueError(f"Room {command.room_id} not found")

        if not room.game_state:
            raise ValueError("Game not started")

        game_state = room.game_state

        if game_state.current_phase != GamePhase.ELECTION:
            raise ValueError(
                f"Cannot vote in phase {game_state.current_phase.value}"
            )

        player = room.get_player(command.player_id)
        if not player or not player.can_participate():
            raise ValueError("Player cannot vote")

        if command.player_id == game_state.president_id:
            raise ValueError("President cannot vote on their own nomination")

        if command.player_id in game_state.votes:
            raise ValueError("Player has already voted")

        game_state.votes[command.player_id] = command.vote

        active_player_count = len(room.active_players())
        expected_vote_count = active_player_count - 1
        result = None
        if len(game_state.votes) == expected_vote_count:
            result = self._process_election_results(room)

        self.repository.save(room)

        return result

    def _process_election_results(self, room) -> None | dict:
        game_state = room.game_state
        if not game_state:
            return

        is_elected = GovernmentFormationService.is_government_elected(
            game_state.votes
        )

        if is_elected:
            game_state.chancellor_id = game_state.nominated_chancellor_id

            chancellor_role = game_state.get_role(game_state.chancellor_id)
            if chancellor_role and chancellor_role.is_hitler and game_state.fascist_policies >= 3:
                game_state.current_phase = GamePhase.GAME_OVER
                game_state.game_over_reason = "Fascists win! Hitler was elected Chancellor after 3 fascist policies were enacted."
                room.end_game()
                return

            game_state.current_phase = GamePhase.LEGISLATIVE_PRESIDENT

            policies = PolicyEnactmentService.draw_policies(game_state)
            game_state.president_policies = policies
            game_state.chancellor_policies = []
            game_state.veto_rejected = False

            return {
                'type': 'elected',
                'president_id': str(game_state.president_id),
                'chancellor_id': str(game_state.chancellor_id)
            }
        
        return IncrementElectionService.handle_failed_government(room)
        
