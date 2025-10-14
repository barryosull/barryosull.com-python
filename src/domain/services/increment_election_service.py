from src.domain.entities.game_room import GameRoom
from src.domain.entities.game_state import GamePhase
from src.domain.services.government_formation_service import GovernmentFormationService
from src.domain.services.policy_enactment_service import PolicyEnactmentService
from src.domain.services.win_condition_service import WinConditionService


class IncrementElectionService:
    @staticmethod
    def handle_failed_government(room: GameRoom):
        game_state = room.game_state
        game_state.increment_election_tracker()

        if not game_state.is_chaos_threshold():
            game_state.previous_president_id = game_state.president_id

            if game_state.next_regular_president_id:
                next_president = game_state.next_regular_president_id
                game_state.next_regular_president_id = None
            else:
                next_president = GovernmentFormationService.advance_president(
                    game_state.president_id, room.active_players()
                )
            game_state.move_to_nomination_phase(next_president)
            return
        
        PolicyEnactmentService.enact_chaos_policy(game_state)
        game_state.reset_election_tracker()
        game_state.previous_chancellor_id = None
        game_state.previous_president_id = None

        is_game_over, winning_team, reason = WinConditionService.check_game_over(
            game_state
        )

        if is_game_over:
            game_state.current_phase = GamePhase.GAME_OVER
            game_state.game_over_reason = f"{winning_team}s win! {reason}"
            room.end_game()
            return
        
        if game_state.next_regular_president_id:
            next_president = game_state.next_regular_president_id
            game_state.next_regular_president_id = None
        else:
            next_president = GovernmentFormationService.advance_president(
                game_state.president_id, room.active_players()
            )
        game_state.move_to_nomination_phase(next_president)
        

