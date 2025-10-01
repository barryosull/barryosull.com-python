"""Pydantic schemas for REST API request/response models."""

from uuid import UUID

from pydantic import BaseModel, Field


class CreateRoomRequest(BaseModel):
    player_name: str = Field(..., min_length=1, max_length=50)


class CreateRoomResponse(BaseModel):
    room_id: UUID
    player_id: UUID


class JoinRoomRequest(BaseModel):
    player_name: str = Field(..., min_length=1, max_length=50)


class JoinRoomResponse(BaseModel):
    player_id: UUID


class PlayerResponse(BaseModel):
    player_id: UUID
    name: str
    is_connected: bool
    is_alive: bool


class RoomStateResponse(BaseModel):
    room_id: UUID
    status: str
    creator_id: UUID | None
    players: list[PlayerResponse]
    player_count: int
    can_start: bool
    created_at: str


class ErrorResponse(BaseModel):
    error: str
    detail: str | None = None
