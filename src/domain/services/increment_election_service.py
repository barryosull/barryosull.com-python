from uuid import UUID
from src.domain.entities.game_room import GameRoom
from src.domain.entities.game_state import GamePhase
from src.domain.services.government_formation_service import GovernmentFormationService
from src.domain.services.policy_enactment_service import PolicyEnactmentService
from src.domain.services.win_condition_service import WinConditionService


class IncrementElectionService:
    @staticmethod
    def handle_failed_government(room: GameRoom) -> None | dict:
        game_state = room.game_state
        game_state.increment_election_tracker()
        votes = game_state.votes

        if not game_state.is_chaos_threshold():
            game_state.previous_president_id = game_state.president_id

            if game_state.next_regular_president_id:
                next_president = game_state.next_regular_president_id
                game_state.next_regular_president_id = None
            else:
                next_president = GovernmentFormationService.advance_president(
                    game_state.president_id, room.active_players()
                )
            votes = game_state.votes
            game_state.move_to_nomination_phase(next_president)

            return {
                "type": "failed_election",
                "no_votes": IncrementElectionService._extract_no_votes(votes),
            }

        chaos_policy = PolicyEnactmentService.enact_chaos_policy(game_state)
        game_state.reset_election_tracker()
        game_state.previous_chancellor_id = None
        game_state.previous_president_id = None

        is_game_over, winning_team, reason = WinConditionService.check_game_over(
            game_state
        )

        result = {
            "type": "failed_election",
            "no_votes": IncrementElectionService._extract_no_votes(votes),
            "policy": chaos_policy.type.value
        }

        if is_game_over:
            game_state.current_phase = GamePhase.GAME_OVER
            game_state.game_over_reason = f"{winning_team}s win! {reason}"
            room.end_game()
            return result

        if game_state.next_regular_president_id:
            next_president = game_state.next_regular_president_id
            game_state.next_regular_president_id = None
        else:
            next_president = GovernmentFormationService.advance_president(
                game_state.president_id, room.active_players()
            )
        game_state.move_to_nomination_phase(next_president)

        return result

    # TODO: Move to HTTP layer, as this is a JSON encoding issue for WS, not a domain concept 
    @staticmethod
    def _extract_no_votes(votes: dict[UUID, bool]) -> list[str]:
        no_votes = []
        for uuid, vote in votes.items():
            if vote == False:
                no_votes.append(str(uuid))
        
        return no_votes
