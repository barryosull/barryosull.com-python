"""REST API routes for game room management."""

from uuid import UUID

from fastapi import APIRouter, HTTPException, status

from src.adapters.api.rest.schemas import (
    CreateRoomRequest,
    CreateRoomResponse,
    ErrorResponse,
    JoinRoomRequest,
    JoinRoomResponse,
    PlayerResponse,
    RoomStateResponse,
)
from src.adapters.persistence.in_memory_repository import InMemoryRoomRepository
from src.application.commands.create_room import CreateRoomCommand, CreateRoomHandler
from src.application.commands.join_room import JoinRoomCommand, JoinRoomHandler
from src.application.queries.get_room_state import (
    GetRoomStateHandler,
    GetRoomStateQuery,
)

# Initialize repository (in production, this would be injected via dependency injection)
repository = InMemoryRoomRepository()

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
        handler = CreateRoomHandler(repository)
        command = CreateRoomCommand(player_name=request.player_name)
        result = handler.handle(command)

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
        handler = JoinRoomHandler(repository)
        command = JoinRoomCommand(room_id=room_id, player_name=request.player_name)
        result = handler.handle(command)

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
