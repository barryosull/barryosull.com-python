"""REST API routes for game room management."""

import sqlite3
from uuid import UUID
import src.config

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
    ReorderPlayersRequest,
    RoleResponse,
    RoomStateResponse,
    StartGameRequest,
    TriggerNotification,
    UseExecutiveActionRequest,
    VetoAgendaRequest,
)
from src.adapters.persistence.file_system_room_repository import FileSystemRoomRepository
from src.adapters.persistence.sqlite_code_repository import SqliteCodeRepository
from src.adapters.persistence.sqlite_room_repository import SqliteRoomRepository
from src.application.command_bus import CommandBus
from src.application.commands.cast_vote import CastVoteCommand
from src.application.commands.create_room import CreateRoomCommand
from src.application.commands.discard_policy import DiscardPolicyCommand
from src.application.commands.enact_policy import EnactPolicyCommand
from src.application.commands.join_room import JoinRoomCommand
from src.application.commands.nominate_chancellor import NominateChancellorCommand
from src.application.commands.reorder_players import ReorderPlayersCommand
from src.application.commands.start_game import StartGameCommand
from src.application.commands.use_executive_action import UseExecutiveActionCommand
from src.application.commands.veto_agenda import VetoAgendaCommand
from src.application.queries.get_room_state import (
    GetRoomStateHandler,
    GetRoomStateQuery,
)
from src.domain.value_objects.policy import PolicyType
import os

from src.ports.code_repository_port import CodeRepositoryPort
from src.ports.room_repository_port import RoomRepositoryPort


# Update messages
GAME_STATE_UPDATED = {
    'type': 'game_state_updated'
}


# Dependency management
room_manager = RoomManager()
router = APIRouter(prefix="/api", tags=["rooms"])


def make_db_connection() -> sqlite3.Connection:
    return sqlite3.connect(src.config.SQLITE_FILE)

def make_code_repository() -> CodeRepositoryPort:
    return SqliteCodeRepository(make_db_connection())


def make_room_repository() -> RoomRepositoryPort:
    return SqliteRoomRepository(make_db_connection())


def make_command_bus() -> CommandBus:
    return CommandBus(make_room_repository())


# Prep DBs (bad and lazy, but good enough for this simple web app)
SqliteCodeRepository(make_db_connection()).init_tables()
SqliteRoomRepository(make_db_connection()).init_tables()


# Helper methods
def get_room_id_from_code(room_code: str) -> UUID:
    room_id = make_code_repository().find_room_by_code(room_code)
    if room_id is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Room code {room_code} not found"
        )
    return room_id


def handle_value_error(e: ValueError) -> None:
    error_msg = str(e)
    if "not found" in error_msg.lower() or "not started" in error_msg.lower():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=error_msg)
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error_msg)


# Routes
@router.websocket("/ws/{room_code}")
async def websocket_endpoint(websocket: WebSocket, room_code: str):
    room_id = get_room_id_from_code(room_code)
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
async def create_room(request: CreateRoomRequest) -> CreateRoomResponse:
    try:
        command = CreateRoomCommand(player_name=request.player_name)
        result = make_command_bus().execute(command)
        room_code = make_code_repository().generate_code_for_room(result.room_id)
        return CreateRoomResponse(
            room_id=result.room_id,
            player_id=result.player_id,
            room_code=room_code
        )
    except ValueError as e:
        handle_value_error(e)


@router.post(
    "/rooms/{room_code}/join",
    response_model=JoinRoomResponse,
    status_code=status.HTTP_200_OK,
    responses={400: {"model": ErrorResponse}, 404: {"model": ErrorResponse}},
)
async def join_room(room_code: str, request: JoinRoomRequest) -> JoinRoomResponse:
    room_id = get_room_id_from_code(room_code)
    try:
        command = JoinRoomCommand(room_id=room_id, player_name=request.player_name)
        result = make_command_bus().execute(command)

        return JoinRoomResponse(player_id=result.player_id)
    except ValueError as e:
        handle_value_error(e)
    finally:
        await room_manager.broadcast(room_id, GAME_STATE_UPDATED)


@router.post(
    "/rooms/{room_code}/reorder-players",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={400: {"model": ErrorResponse}, 404: {"model": ErrorResponse}},
)
async def reorder_players(room_code: str, request: ReorderPlayersRequest) -> None:
    room_id = get_room_id_from_code(room_code)
    try:
        command = ReorderPlayersCommand(
            room_id=room_id,
            requester_id=request.player_id,
            player_ids=request.player_ids,
        )
        make_command_bus().execute(command)
    except ValueError as e:
        handle_value_error(e)
    finally:
        await room_manager.broadcast(room_id, GAME_STATE_UPDATED)


@router.get(
    "/rooms/{room_code}",
    response_model=RoomStateResponse,
    status_code=status.HTTP_200_OK,
    responses={404: {"model": ErrorResponse}},
)
def get_room_state(room_code: str) -> RoomStateResponse:
    room_id = get_room_id_from_code(room_code)
    try:
        handler = GetRoomStateHandler(make_room_repository())
        query = GetRoomStateQuery(room_id=room_id)
        result = handler.handle(query)

        return ResponseFactory.make_room_state_response(result)
    except ValueError as e:
        handle_value_error(e)


@router.post(
    "/rooms/{room_code}/start",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={400: {"model": ErrorResponse}, 404: {"model": ErrorResponse}},
)
async def start_game(room_code: str, request: StartGameRequest) -> None:
    room_id = get_room_id_from_code(room_code)
    try:
        command = StartGameCommand(room_id=room_id, requester_id=request.player_id)
        make_command_bus().execute(command)
    except ValueError as e:
        handle_value_error(e)
    finally:
        await room_manager.broadcast(room_id, GAME_STATE_UPDATED)


@router.post(
    "/games/{room_code}/nominate",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={400: {"model": ErrorResponse}, 404: {"model": ErrorResponse}},
)
async def nominate_chancellor(room_code: str, request: NominateChancellorRequest) -> None:
    room_id = get_room_id_from_code(room_code)
    try:
        command = NominateChancellorCommand(
            room_id=room_id,
            nominating_player_id=request.player_id,
            chancellor_id=request.chancellor_id,
        )
        make_command_bus().execute(command)
    except ValueError as e:
        handle_value_error(e)
    finally:
        await room_manager.broadcast(room_id, GAME_STATE_UPDATED)


@router.post(
    "/games/{room_code}/vote",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={400: {"model": ErrorResponse}, 404: {"model": ErrorResponse}},
)
async def cast_vote(room_code: str, request: CastVoteRequest) -> None:
    room_id = get_room_id_from_code(room_code)
    try:
        command = CastVoteCommand(
            room_id=room_id, player_id=request.player_id, vote=request.vote
        )
        result = make_command_bus().execute(command)
        if result is not None:
            await room_manager.broadcast(room_id, result)
    except ValueError as e:
        handle_value_error(e)
    finally:
        await room_manager.broadcast(room_id, GAME_STATE_UPDATED)


@router.post(
    "/games/{room_code}/discard-policy",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={400: {"model": ErrorResponse}, 404: {"model": ErrorResponse}},
)
async def discard_policy(room_code: str, request: DiscardPolicyRequest) -> None:
    room_id = get_room_id_from_code(room_code)
    try:
        command = DiscardPolicyCommand(
            room_id=room_id,
            player_id=request.player_id,
            policy_type=PolicyType(request.policy_type),
        )
        make_command_bus().execute(command)
    except ValueError as e:
        handle_value_error(e)
    finally:
        await room_manager.broadcast(room_id, GAME_STATE_UPDATED)


@router.post(
    "/games/{room_code}/enact-policy",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={400: {"model": ErrorResponse}, 404: {"model": ErrorResponse}},
)
async def enact_policy(room_code: str, request: EnactPolicyRequest) -> None:
    room_id = get_room_id_from_code(room_code)
    try:
        command = EnactPolicyCommand(
            room_id=room_id,
            player_id=request.player_id,
            policy_type=PolicyType(request.policy_type),
        )
        make_command_bus().execute(command)
        enacted_message = {
            'type': 'policy_enacted',
            'policy_type': request.policy_type,
        }
        await room_manager.broadcast(room_id, enacted_message)
    except ValueError as e:
        handle_value_error(e)
    finally:
        await room_manager.broadcast(room_id, GAME_STATE_UPDATED)


@router.get(
    "/games/{room_code}/state",
    response_model=GameStateResponse,
    status_code=status.HTTP_200_OK,
    responses={404: {"model": ErrorResponse}},
)
def get_game_state(room_code: str) -> GameStateResponse:
    room_id = get_room_id_from_code(room_code)
    try:
        room = make_room_repository().find_by_id(room_id)
        if not room:
            raise ValueError(f"Room {room_id} not found")

        return ResponseFactory.make_game_state_response(room)
    except ValueError as e:
        handle_value_error(e)


@router.get(
    "/games/{room_code}/my-role",
    response_model=RoleResponse,
    status_code=status.HTTP_200_OK,
    responses={404: {"model": ErrorResponse}},
)
def get_my_role(room_code: str, player_id: UUID) -> RoleResponse:
    room_id = get_room_id_from_code(room_code)
    try:
        room = make_room_repository().find_by_id(room_id)
        if not room:
            raise ValueError(f"Room {room_id} not found")

        return ResponseFactory.make_my_role_response(room, player_id)
    except ValueError as e:
        handle_value_error(e)


@router.get(
    "/games/{room_code}/investigate-loyalty",
    response_model=RoleResponse,
    status_code=status.HTTP_200_OK,
    responses={400: {"model": ErrorResponse}, 404: {"model": ErrorResponse}},
)
def investigate_loyalty(room_code: str, player_id: UUID, target_player_id: UUID) -> RoleResponse:
    room_id = get_room_id_from_code(room_code)
    try:
        room = make_room_repository().find_by_id(room_id)
        if not room:
            raise ValueError(f"Room {room_id} not found")

        return ResponseFactory.make_loyalty_response(room, player_id, target_player_id)
    except ValueError as e:
        handle_value_error(e)


@router.post(
    "/games/{room_code}/use-power",
    response_model=ExecutiveActionResponse,
    status_code=status.HTTP_200_OK,
    responses={400: {"model": ErrorResponse}, 404: {"model": ErrorResponse}},
)
async def use_executive_power(room_code: str, request: UseExecutiveActionRequest) -> ExecutiveActionResponse:
    room_id = get_room_id_from_code(room_code)
    try:
        command = UseExecutiveActionCommand(
            room_id=room_id,
            player_id=request.player_id,
            target_player_id=request.target_player_id,
        )
        result = make_command_bus().execute(command)

        await room_manager.broadcast(room_id, result)

        return ExecutiveActionResponse(**result)
    except ValueError as e:
        handle_value_error(e)
    finally:
        await room_manager.broadcast(room_id, GAME_STATE_UPDATED)


@router.post(
    "/games/{room_code}/veto",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={400: {"model": ErrorResponse}, 404: {"model": ErrorResponse}},
)
async def veto_agenda(room_code: str, request: VetoAgendaRequest) -> None:
    room_id = get_room_id_from_code(room_code)
    try:
        command = VetoAgendaCommand(
            room_id=room_id,
            player_id=request.player_id,
            approve_veto=request.approve_veto,
        )
        result = make_command_bus().execute(command)
        if (result is not None):
            await room_manager.broadcast(room_id, result)
    except ValueError as e:
        handle_value_error(e)
    finally:
        await room_manager.broadcast(room_id, GAME_STATE_UPDATED)

# Used to test notifications, triggers a specific one in the UI
@router.post(
    "/games/{room_code}/trigger_notification",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={400: {"model": ErrorResponse}, 404: {"model": ErrorResponse}},
)
async def trigger_notification(room_code: str, request: TriggerNotification) -> None:
    room_id = get_room_id_from_code(room_code)
    if request.type == "failed_election":
        room = make_room_repository().find_by_id(room_id)
        room.players
        fake_notification = {
            "type": request.type,
            "no_votes": [str(p.player_id) for p in room.players],
            "policy_type": PolicyType.FASCIST.name
        }
        await room_manager.broadcast(room_id, fake_notification)
    return
