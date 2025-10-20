from uuid import UUID

from backend.domain.entities.game_state import GameState
from backend.domain.entities.player import Player


class GovernmentFormationService:
    @staticmethod
    def can_nominate_chancellor(
        game_state: GameState,
        chancellor_id: UUID,
        active_players: list[Player],
    ) -> tuple[bool, str]:
        active_player_ids = {p.player_id for p in active_players}

        if chancellor_id not in active_player_ids:
            return False, "Chancellor must be an active player"

        if chancellor_id == game_state.president_id:
            return False, "President cannot nominate themselves as chancellor"

        alive_count = len(active_players)

        if chancellor_id == game_state.previous_chancellor_id:
            return False, "Cannot nominate previous chancellor"

        if alive_count > 5 and chancellor_id == game_state.previous_president_id:
            return False, "Cannot nominate previous president"

        return True, ""

    @staticmethod
    def is_government_elected(votes: dict[UUID, bool]) -> bool:
        if not votes:
            return False

        yes_votes = sum(1 for vote in votes.values() if vote)
        total_votes = len(votes)

        return yes_votes > total_votes / 2

    @staticmethod
    def advance_president(
        current_president_id: UUID | None, active_players: list[Player]
    ) -> UUID:
        if not active_players:
            raise ValueError("No active players available")

        if current_president_id is None:
            return active_players[0].player_id

        current_index = next(
            (
                i
                for i, p in enumerate(active_players)
                if p.player_id == current_president_id
            ),
            -1,
        )

        if current_index == -1:
            return active_players[0].player_id

        next_index = (current_index + 1) % len(active_players)
        return active_players[next_index].player_id
