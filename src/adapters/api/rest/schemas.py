"""Pydantic schemas for REST API request/response models."""

from uuid import UUID

from pydantic import BaseModel, Field


class CreateRoomRequest(BaseModel):
    """Request schema for creating a new game room."""

    player_name: str = Field(..., min_length=1, max_length=50)


class CreateRoomResponse(BaseModel):
    """Response schema for creating a new game room."""

    room_id: UUID
    player_id: UUID


class JoinRoomRequest(BaseModel):
    """Request schema for joining a game room."""

    player_name: str = Field(..., min_length=1, max_length=50)


class JoinRoomResponse(BaseModel):
    """Response schema for joining a game room."""

    player_id: UUID


class PlayerResponse(BaseModel):
    """Response schema for player information."""

    player_id: UUID
    name: str
    is_connected: bool
    is_alive: bool


class RoomStateResponse(BaseModel):
    """Response schema for game room state."""

    room_id: UUID
    status: str
    creator_id: UUID | None
    players: list[PlayerResponse]
    player_count: int
    can_start: bool
    created_at: str


class ErrorResponse(BaseModel):
    """Response schema for error messages."""

    error: str
    detail: str | None = None
