"""REST API routes for game room management."""

from uuid import UUID

from fastapi import APIRouter, HTTPException, status, WebSocket, WebSocketDisconnect

from src.adapters.api.rest.response_factory import ResponseFactory
from src.adapters.api.rest.room_manager import RoomManager
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
from src.domain.value_objects.policy import PolicyType


repository = FileSystemRoomRepository()
command_bus = CommandBus(repository)

# Update messages
GAME_STATE_UPDATED = 'game_state_updated'

# Create router
router = APIRouter(prefix="/api", tags=["rooms"])

room_manager = RoomManager()


def handle_value_error(e: ValueError) -> None:
    error_msg = str(e)
    if "not found" in error_msg.lower() or "not started" in error_msg.lower():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=error_msg)
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error_msg)


@router.websocket("/ws/{room_id}")
async def websocket_endpoint(websocket: WebSocket, room_id: UUID):
    await room_manager.connect(websocket, room_id)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        room_manager.disconnect(websocket, room_id)


@router.get("/")
def root() -> dict[str, str]:
    return {"name": "Secret Hitler API", "version": "0.1.0"}


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


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
        handle_value_error(e)


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

        room_manager.broadcast(room_id, GAME_STATE_UPDATED)

        return JoinRoomResponse(player_id=result.player_id)
    except ValueError as e:
        handle_value_error(e)


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

        return ResponseFactory.make_room_state_response(result)
    except ValueError as e:
        handle_value_error(e)


@router.post(
    "/rooms/{room_id}/start",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={400: {"model": ErrorResponse}, 404: {"model": ErrorResponse}},
)
async def start_game(room_id: UUID, request: StartGameRequest) -> None:
    try:
        command = StartGameCommand(room_id=room_id, requester_id=request.player_id)
        command_bus.execute(command)

        await room_manager.broadcast(room_id, GAME_STATE_UPDATED)
    except ValueError as e:
        handle_value_error(e)


@router.post(
    "/games/{room_id}/nominate",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={400: {"model": ErrorResponse}, 404: {"model": ErrorResponse}},
)
async def nominate_chancellor(room_id: UUID, request: NominateChancellorRequest) -> None:
    try:
        command = NominateChancellorCommand(
            room_id=room_id,
            nominating_player_id=request.player_id,
            chancellor_id=request.chancellor_id,
        )
        command_bus.execute(command)

        await room_manager.broadcast(room_id, GAME_STATE_UPDATED)
    except ValueError as e:
        handle_value_error(e)


@router.post(
    "/games/{room_id}/vote",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={400: {"model": ErrorResponse}, 404: {"model": ErrorResponse}},
)
async def cast_vote(room_id: UUID, request: CastVoteRequest) -> None:
    try:
        command = CastVoteCommand(
            room_id=room_id, player_id=request.player_id, vote=request.vote
        )
        command_bus.execute(command)

        await room_manager.broadcast(room_id, GAME_STATE_UPDATED)
    except ValueError as e:
        handle_value_error(e)


@router.post(
    "/games/{room_id}/discard-policy",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={400: {"model": ErrorResponse}, 404: {"model": ErrorResponse}},
)
async def discard_policy(room_id: UUID, request: DiscardPolicyRequest) -> None:
    try:
        command = DiscardPolicyCommand(
            room_id=room_id,
            player_id=request.player_id,
            policy_type=PolicyType(request.policy_type),
        )
        command_bus.execute(command)

        await room_manager.broadcast(room_id, GAME_STATE_UPDATED)
    except ValueError as e:
        handle_value_error(e)


@router.post(
    "/games/{room_id}/enact-policy",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={400: {"model": ErrorResponse}, 404: {"model": ErrorResponse}},
)
async def enact_policy(room_id: UUID, request: EnactPolicyRequest) -> None:
    try:
        command = EnactPolicyCommand(
            room_id=room_id,
            player_id=request.player_id,
            policy_type=PolicyType(request.policy_type),
        )
        command_bus.execute(command)

        await room_manager.broadcast(room_id, GAME_STATE_UPDATED)
    except ValueError as e:
        handle_value_error(e)


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

        return ResponseFactory.make_game_state_response(room)
    except ValueError as e:
        handle_value_error(e)


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

        return ResponseFactory.make_my_role_response(room, player_id)
    except ValueError as e:
        handle_value_error(e)


@router.get(
    "/games/{room_id}/investigate-loyalty",
    response_model=RoleResponse,
    status_code=status.HTTP_200_OK,
    responses={400: {"model": ErrorResponse}, 404: {"model": ErrorResponse}},
)
def investigate_loyalty(room_id: UUID, player_id: UUID, target_player_id: UUID) -> RoleResponse:
    try:
        room = repository.find_by_id(room_id)
        if not room:
            raise ValueError(f"Room {room_id} not found")

        return ResponseFactory.make_loyalty_response(room, player_id, target_player_id)
    except ValueError as e:
        handle_value_error(e)


@router.post(
    "/games/{room_id}/use-power",
    response_model=ExecutiveActionResponse,
    status_code=status.HTTP_200_OK,
    responses={400: {"model": ErrorResponse}, 404: {"model": ErrorResponse}},
)
async def use_executive_power(room_id: UUID, request: UseExecutiveActionRequest) -> ExecutiveActionResponse:
    try:
        command = UseExecutiveActionCommand(
            room_id=room_id,
            player_id=request.player_id,
            target_player_id=request.target_player_id,
        )
        result = command_bus.execute(command)

        await room_manager.broadcast(room_id, GAME_STATE_UPDATED)

        return ExecutiveActionResponse(**result)
    except ValueError as e:
        handle_value_error(e)


@router.post(
    "/games/{room_id}/veto",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={400: {"model": ErrorResponse}, 404: {"model": ErrorResponse}},
)
async def veto_agenda(room_id: UUID, request: VetoAgendaRequest) -> None:
    try:
        command = VetoAgendaCommand(
            room_id=room_id,
            player_id=request.player_id,
            approve_veto=request.approve_veto,
        )
        command_bus.execute(command)

        await room_manager.broadcast(room_id, GAME_STATE_UPDATED)
    except ValueError as e:
        handle_value_error(e)
