"""REST API routes for game room management."""

from uuid import UUID

from fastapi import APIRouter, HTTPException, status

from src.adapters.api.rest.schemas import (
    CastVoteRequest,
    CreateRoomRequest,
    CreateRoomResponse,
    DiscardPolicyRequest,
    EnactPolicyRequest,
    ErrorResponse,
    ExecutiveActionResponse,
    GameStateResponse,
    JoinRoomRequest,
    JoinRoomResponse,
    NominateChancellorRequest,
    PlayerResponse,
    RoleResponse,
    RoomStateResponse,
    StartGameRequest,
    UseExecutiveActionRequest,
    VetoAgendaRequest,
)
from src.adapters.persistence.file_system_repository import FileSystemRoomRepository
from src.application.command_bus import CommandBus
from src.application.commands.cast_vote import CastVoteCommand
from src.application.commands.create_room import CreateRoomCommand
from src.application.commands.discard_policy import DiscardPolicyCommand
from src.application.commands.enact_policy import EnactPolicyCommand
from src.application.commands.join_room import JoinRoomCommand
from src.application.commands.nominate_chancellor import NominateChancellorCommand
from src.application.commands.start_game import StartGameCommand
from src.application.commands.use_executive_action import UseExecutiveActionCommand
from src.application.commands.veto_agenda import VetoAgendaCommand
from src.application.queries.get_room_state import (
    GetRoomStateHandler,
    GetRoomStateQuery,
)
from src.domain.entities.game_state import GamePhase, PresidentialPower
from src.domain.services.government_formation_service import (
    GovernmentFormationService,
)

repository = FileSystemRoomRepository()
command_bus = CommandBus(repository)

# Create router
router = APIRouter(prefix="/api", tags=["rooms"])


@router.post(
    "/rooms",
    response_model=CreateRoomResponse,
    status_code=status.HTTP_201_CREATED,
    responses={400: {"model": ErrorResponse}},
)
def create_room(request: CreateRoomRequest) -> CreateRoomResponse:
    try:
        command = CreateRoomCommand(player_name=request.player_name)
        result = command_bus.execute(command)

        return CreateRoomResponse(room_id=result.room_id, player_id=result.player_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post(
    "/rooms/{room_id}/join",
    response_model=JoinRoomResponse,
    status_code=status.HTTP_200_OK,
    responses={400: {"model": ErrorResponse}, 404: {"model": ErrorResponse}},
)
def join_room(room_id: UUID, request: JoinRoomRequest) -> JoinRoomResponse:
    try:
        command = JoinRoomCommand(room_id=room_id, player_name=request.player_name)
        result = command_bus.execute(command)

        return JoinRoomResponse(player_id=result.player_id)
    except ValueError as e:
        error_msg = str(e)
        if "not found" in error_msg.lower():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=error_msg)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error_msg)


@router.get(
    "/rooms/{room_id}",
    response_model=RoomStateResponse,
    status_code=status.HTTP_200_OK,
    responses={404: {"model": ErrorResponse}},
)
def get_room_state(room_id: UUID) -> RoomStateResponse:
    try:
        handler = GetRoomStateHandler(repository)
        query = GetRoomStateQuery(room_id=room_id)
        result = handler.handle(query)

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
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post(
    "/rooms/{room_id}/start",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={400: {"model": ErrorResponse}, 404: {"model": ErrorResponse}},
)
def start_game(room_id: UUID, request: StartGameRequest) -> None:
    try:
        command = StartGameCommand(room_id=room_id, requester_id=request.player_id)
        command_bus.execute(command)
    except ValueError as e:
        error_msg = str(e)
        if "not found" in error_msg.lower():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=error_msg)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error_msg)


@router.post(
    "/games/{room_id}/nominate",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={400: {"model": ErrorResponse}, 404: {"model": ErrorResponse}},
)
def nominate_chancellor(room_id: UUID, request: NominateChancellorRequest) -> None:
    try:
        command = NominateChancellorCommand(
            room_id=room_id,
            nominating_player_id=request.player_id,
            chancellor_id=request.chancellor_id,
        )
        command_bus.execute(command)
    except ValueError as e:
        error_msg = str(e)
        if "not found" in error_msg.lower():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=error_msg)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error_msg)


@router.post(
    "/games/{room_id}/vote",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={400: {"model": ErrorResponse}, 404: {"model": ErrorResponse}},
)
def cast_vote(room_id: UUID, request: CastVoteRequest) -> None:
    try:
        command = CastVoteCommand(
            room_id=room_id, player_id=request.player_id, vote=request.vote
        )
        command_bus.execute(command)
    except ValueError as e:
        error_msg = str(e)
        if "not found" in error_msg.lower():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=error_msg)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error_msg)


@router.post(
    "/games/{room_id}/discard-policy",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={400: {"model": ErrorResponse}, 404: {"model": ErrorResponse}},
)
def discard_policy(room_id: UUID, request: DiscardPolicyRequest) -> None:
    try:
        command = DiscardPolicyCommand(
            room_id=room_id,
            player_id=request.player_id,
            policy_type=request.policy_type,
        )
        command_bus.execute(command)
    except ValueError as e:
        error_msg = str(e)
        if "not found" in error_msg.lower():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=error_msg)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error_msg)


@router.post(
    "/games/{room_id}/enact-policy",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={400: {"model": ErrorResponse}, 404: {"model": ErrorResponse}},
)
def enact_policy(room_id: UUID, request: EnactPolicyRequest) -> None:
    try:
        room = repository.find_by_id(room_id)
        if not room:
            raise ValueError(f"Room {room_id} not found")

        if not room.game_state:
            raise ValueError("Game not started")

        policy = next(
            (p for p in room.game_state.chancellor_policies if p.type.value == request.policy_type),
            None
        )
        if not policy:
            raise ValueError(f"Policy {request.policy_type} not found in chancellor policies")

        command = EnactPolicyCommand(
            room_id=room_id,
            player_id=request.player_id,
            enacted_policy=policy,
        )
        command_bus.execute(command)
    except ValueError as e:
        error_msg = str(e)
        if "not found" in error_msg.lower():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=error_msg)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error_msg)


@router.get(
    "/games/{room_id}/state",
    response_model=GameStateResponse,
    status_code=status.HTTP_200_OK,
    responses={404: {"model": ErrorResponse}},
)
def get_game_state(room_id: UUID) -> GameStateResponse:
    try:
        room = repository.find_by_id(room_id)
        if not room:
            raise ValueError(f"Room {room_id} not found")

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

        return GameStateResponse(
            round_number=game_state.round_number,
            president_id=game_state.president_id,
            chancellor_id=game_state.chancellor_id,
            nominated_chancellor_id=game_state.nominated_chancellor_id,
            previous_president_id=game_state.previous_president_id,
            previous_chancellor_id=game_state.previous_chancellor_id,
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
                and game_state.get_presidential_power(len(room.active_players())) == PresidentialPower.POLICY_PEEK
                else None
            ),
            game_over_reason=game_state.game_over_reason,
            eligible_chancellor_nominees=eligible_chancellor_nominees,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get(
    "/games/{room_id}/my-role",
    response_model=RoleResponse,
    status_code=status.HTTP_200_OK,
    responses={404: {"model": ErrorResponse}},
)
def get_my_role(room_id: UUID, player_id: UUID) -> RoleResponse:
    try:
        room = repository.find_by_id(room_id)
        if not room:
            raise ValueError(f"Room {room_id} not found")

        game_state = room.game_state
        if not game_state:
            raise ValueError("Game has not started yet")

        role = game_state.role_assignments.get(player_id)
        if not role:
            raise ValueError(f"Player {player_id} not found in game")

        return RoleResponse(team=role.team, is_hitler=role.is_hitler)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post(
    "/games/{room_id}/use-power",
    response_model=ExecutiveActionResponse,
    status_code=status.HTTP_200_OK,
    responses={400: {"model": ErrorResponse}, 404: {"model": ErrorResponse}},
)
def use_executive_power(room_id: UUID, request: UseExecutiveActionRequest) -> ExecutiveActionResponse:
    try:
        command = UseExecutiveActionCommand(
            room_id=room_id,
            player_id=request.player_id,
            target_player_id=request.target_player_id,
        )
        result = command_bus.execute(command)
        return ExecutiveActionResponse(**result)
    except ValueError as e:
        error_msg = str(e)
        if "not found" in error_msg.lower():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=error_msg)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error_msg)


@router.post(
    "/games/{room_id}/veto",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={400: {"model": ErrorResponse}, 404: {"model": ErrorResponse}},
)
def veto_agenda(room_id: UUID, request: VetoAgendaRequest) -> None:
    try:
        command = VetoAgendaCommand(
            room_id=room_id,
            player_id=request.player_id,
            approve_veto=request.approve_veto,
        )
        command_bus.execute(command)
    except ValueError as e:
        error_msg = str(e)
        if "not found" in error_msg.lower():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=error_msg)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error_msg)

