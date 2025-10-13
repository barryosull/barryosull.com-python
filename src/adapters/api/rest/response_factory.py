from src.adapters.api.rest.schemas import (
    GameStateResponse,
    PlayerResponse,
    RoomStateResponse,
)
from src.application.queries.get_room_state import RoomStateDTO
from src.domain.entities.game_room import GameRoom
from src.domain.entities.game_state import GamePhase, PresidentialPower
from src.domain.services.government_formation_service import (
    GovernmentFormationService,
)


class ResponseFactory:

    @staticmethod
    def make_room_state_response(result: RoomStateDTO) -> RoomStateResponse:
        return RoomStateResponse(
            room_id=result.room_id,
            status=result.status,
            creator_id=result.creator_id,
            players=[
                PlayerResponse(
                    player_id=p.player_id,
                    name=p.name,
                    is_connected=p.is_connected,
                    is_alive=p.is_alive,
                )
                for p in result.players
            ],
            player_count=result.player_count,
            can_start=result.can_start,
            created_at=result.created_at,
        )

    @staticmethod
    def make_game_state_response(room: GameRoom) -> GameStateResponse:
        game_state = room.game_state
        if not game_state:
            raise ValueError("Game has not started yet")

        eligible_chancellor_nominees = None
        if game_state.current_phase == GamePhase.NOMINATION:
            eligible = []
            for player in room.active_players():
                can_nominate, _ = GovernmentFormationService.can_nominate_chancellor(
                    game_state, player.player_id, room.active_players()
                )
                if can_nominate:
                    eligible.append(player.player_id)
            eligible_chancellor_nominees = eligible

        presidential_power = None
        if game_state.current_phase == GamePhase.EXECUTIVE_ACTION:
            power = game_state.get_presidential_power(len(room.active_players()))
            if power:
                presidential_power = power.value

        return GameStateResponse(
            round_number=game_state.round_number,
            president_id=game_state.president_id,
            chancellor_id=game_state.chancellor_id,
            nominated_chancellor_id=game_state.nominated_chancellor_id,
            previous_president_id=game_state.previous_president_id,
            previous_chancellor_id=game_state.previous_chancellor_id,
            veto_requested=game_state.veto_requested,
            liberal_policies=game_state.liberal_policies,
            fascist_policies=game_state.fascist_policies,
            election_tracker=game_state.election_tracker,
            current_phase=game_state.current_phase.value,
            votes={str(k): v for k, v in game_state.votes.items()},
            president_policies=[
                {"type": p.type} for p in game_state.president_policies
            ],
            chancellor_policies=[
                {"type": p.type} for p in game_state.chancellor_policies
            ],
            peeked_policies=(
                [{"type": p.type.value} for p in game_state.peek_policies()]
                if game_state.current_phase == GamePhase.EXECUTIVE_ACTION
                and game_state.get_presidential_power(len(room.active_players()))
                == PresidentialPower.POLICY_PEEK
                else None
            ),
            game_over_reason=game_state.game_over_reason,
            eligible_chancellor_nominees=eligible_chancellor_nominees,
            presidential_power=presidential_power,
            investigated_players=list(game_state.investigated_players),
        )
