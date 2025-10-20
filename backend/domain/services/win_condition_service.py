from uuid import UUID

from backend.domain.entities.game_state import GameState
from backend.domain.value_objects.role import Team


class WinConditionService:
    @staticmethod
    def check_liberal_victory(game_state: GameState) -> tuple[bool, str]:
        if game_state.liberal_policies >= 5:
            return True, "5 liberal policies enacted"
        return False, ""

    @staticmethod
    def check_fascist_victory(game_state: GameState) -> tuple[bool, str]:
        if game_state.fascist_policies >= 6:
            return True, "6 fascist policies enacted"
        return False, ""

    @staticmethod
    def check_hitler_elected(
        game_state: GameState, chancellor_id: UUID
    ) -> tuple[bool, str]:
        if game_state.fascist_policies >= 3:
            role = game_state.get_role(chancellor_id)
            if role and role.is_hitler:
                return True, "Hitler elected chancellor"
        return False, ""

    @staticmethod
    def check_hitler_killed(game_state: GameState, killed_player_id: UUID) -> bool:
        role = game_state.get_role(killed_player_id)
        return role is not None and role.is_hitler

    @staticmethod
    def check_game_over(
        game_state: GameState,
    ) -> tuple[bool, Team | None, str]:
        liberal_won, liberal_msg = WinConditionService.check_liberal_victory(
            game_state
        )
        if liberal_won:
            return True, Team.LIBERAL, liberal_msg

        fascist_won, fascist_msg = WinConditionService.check_fascist_victory(
            game_state
        )
        if fascist_won:
            return True, Team.FASCIST, fascist_msg

        return False, None, ""
