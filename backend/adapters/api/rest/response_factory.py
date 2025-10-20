from uuid import UUID

from backend.adapters.api.rest.schemas import (
    GameStateResponse,
    PlayerResponse,
    RoleResponse,
    RoomStateResponse,
    TeammateInfo,
)
from backend.application.queries.get_room_state import RoomStateDTO
from backend.domain.entities.game_room import GameRoom
from backend.domain.entities.game_state import GamePhase, PresidentialPower
from backend.domain.services.government_formation_service import (
    GovernmentFormationService,
)
from backend.domain.value_objects.role import Team


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
            veto_rejected=game_state.veto_rejected,
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

    @staticmethod
    def make_my_role_response(room: GameRoom, player_id: UUID) -> RoleResponse:
        game_state = room.game_state
        if not game_state:
            raise ValueError("Game has not started yet")

        role = game_state.role_assignments.get(player_id)
        if not role:
            raise ValueError(f"Player {player_id} not found in game")

        teammates = []
        player_count = len(room.players)

        if role.team == Team.FASCIST:
            if 5 <= player_count <= 6:
                for other_player_id, other_role in game_state.role_assignments.items():
                    if other_player_id != player_id and other_role.team == Team.FASCIST:
                        teammate_player = room.get_player(other_player_id)
                        if teammate_player:
                            teammates.append(
                                TeammateInfo(
                                    player_id=other_player_id,
                                    name=teammate_player.name,
                                    is_hitler=other_role.is_hitler,
                                )
                            )
            elif player_count >= 7 and not role.is_hitler:
                for other_player_id, other_role in game_state.role_assignments.items():
                    if other_player_id != player_id and other_role.team == Team.FASCIST:
                        teammate_player = room.get_player(other_player_id)
                        if teammate_player:
                            teammates.append(
                                TeammateInfo(
                                    player_id=other_player_id,
                                    name=teammate_player.name,
                                    is_hitler=other_role.is_hitler,
                                )
                            )

        return RoleResponse(team=role.team, is_hitler=role.is_hitler, teammates=teammates)

    @staticmethod
    def make_loyalty_response(
        room: GameRoom, player_id: UUID, target_player_id: UUID
    ) -> RoleResponse:
        if not room.game_state:
            raise ValueError("Game not started")

        game_state = room.game_state

        if game_state.current_phase != GamePhase.EXECUTIVE_ACTION:
            raise ValueError(
                f"Cannot investigate loyalty in phase {game_state.current_phase.value}"
            )

        if game_state.president_id != player_id:
            raise ValueError("Only the president can investigate loyalty")

        if target_player_id == player_id:
            raise ValueError("Cannot investigate yourself")

        presidential_power = game_state.get_presidential_power(
            len(room.active_players())
        )

        if presidential_power != PresidentialPower.INVESTIGATE_LOYALTY:
            raise ValueError("Investigate loyalty power not available")

        target_role = game_state.role_assignments.get(target_player_id)
        if not target_role:
            raise ValueError("Target player not found in game")

        return RoleResponse(team=target_role.team, is_hitler=False, teammates=[])
