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


class StartGameRequest(BaseModel):
    player_id: UUID


class NominateChancellorRequest(BaseModel):
    player_id: UUID
    chancellor_id: UUID


class CastVoteRequest(BaseModel):
    player_id: UUID
    vote: bool


class DiscardPolicyRequest(BaseModel):
    player_id: UUID
    policy_type: str


class EnactPolicyRequest(BaseModel):
    player_id: UUID
    policy_type: str


class GameStateResponse(BaseModel):
    round_number: int
    president_id: UUID | None
    chancellor_id: UUID | None
    nominated_chancellor_id: UUID | None
    previous_president_id: UUID | None
    previous_chancellor_id: UUID | None
    veto_requested: bool
    liberal_policies: int
    fascist_policies: int
    election_tracker: int
    current_phase: str
    votes: dict[str, bool]
    president_policies: list[dict[str, str]]
    chancellor_policies: list[dict[str, str]]
    peeked_policies: list[dict[str, str]] | None = None
    game_over_reason: str | None = None
    eligible_chancellor_nominees: list[UUID] | None = None
    presidential_power: str | None = None


class RoleResponse(BaseModel):
    team: str
    is_hitler: bool


class UseExecutiveActionRequest(BaseModel):
    player_id: UUID
    target_player_id: UUID | None = None


class ExecutiveActionResponse(BaseModel):
    policies: list[dict[str, str]] | None = None
    executed_player_id: str | None = None
    game_over: bool | None = None
    winning_team: str | None = None


class VetoAgendaRequest(BaseModel):
    player_id: UUID
    approve_veto: bool


class ErrorResponse(BaseModel):
    error: str
    detail: str | None = None
