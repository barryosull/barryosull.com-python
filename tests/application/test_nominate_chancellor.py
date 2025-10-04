from uuid import uuid4

import pytest

from src.adapters.persistence.in_memory_repository import InMemoryRoomRepository
from src.application.commands.nominate_chancellor import (
    NominateChancellorCommand,
    NominateChancellorHandler,
)
from src.domain.entities.game_room import GameRoom, RoomStatus
from src.domain.entities.game_state import GamePhase, GameState
from src.domain.entities.player import Player


def test_nominate_chancellor_success():
    repository = InMemoryRoomRepository()
    handler = NominateChancellorHandler(repository)

    president_id = uuid4()
    chancellor_id = uuid4()

    room = GameRoom()
    room.add_player(Player(president_id, "President"))
    room.add_player(Player(chancellor_id, "Chancellor"))
    room.status = RoomStatus.IN_PROGRESS
    room.game_state = GameState(
        president_id=president_id, current_phase=GamePhase.NOMINATION
    )

    repository.save(room)

    command = NominateChancellorCommand(
        room_id=room.room_id,
        nominating_player_id=president_id,
        chancellor_id=chancellor_id,
    )
    handler.handle(command)

    updated_room = repository.find_by_id(room.room_id)
    assert updated_room.game_state.nominated_chancellor_id == chancellor_id
    assert updated_room.game_state.current_phase == GamePhase.ELECTION


def test_nominate_chancellor_room_not_found():
    repository = InMemoryRoomRepository()
    handler = NominateChancellorHandler(repository)

    command = NominateChancellorCommand(
        room_id=uuid4(), nominating_player_id=uuid4(), chancellor_id=uuid4()
    )

    with pytest.raises(ValueError, match="not found"):
        handler.handle(command)


def test_nominate_chancellor_game_not_started():
    repository = InMemoryRoomRepository()
    handler = NominateChancellorHandler(repository)

    room = GameRoom()
    president_id = uuid4()
    chancellor_id = uuid4()

    room.add_player(Player(president_id, "President"))
    room.add_player(Player(chancellor_id, "Chancellor"))

    repository.save(room)

    command = NominateChancellorCommand(
        room_id=room.room_id,
        nominating_player_id=president_id,
        chancellor_id=chancellor_id,
    )

    with pytest.raises(ValueError, match="Game not started"):
        handler.handle(command)


def test_nominate_chancellor_wrong_phase():
    repository = InMemoryRoomRepository()
    handler = NominateChancellorHandler(repository)

    president_id = uuid4()
    chancellor_id = uuid4()

    room = GameRoom()
    room.add_player(Player(president_id, "President"))
    room.add_player(Player(chancellor_id, "Chancellor"))
    room.status = RoomStatus.IN_PROGRESS
    room.game_state = GameState(
        president_id=president_id, current_phase=GamePhase.ELECTION
    )

    repository.save(room)

    command = NominateChancellorCommand(
        room_id=room.room_id,
        nominating_player_id=president_id,
        chancellor_id=chancellor_id,
    )

    with pytest.raises(ValueError, match="Cannot nominate chancellor in phase"):
        handler.handle(command)


def test_nominate_chancellor_not_president():
    repository = InMemoryRoomRepository()
    handler = NominateChancellorHandler(repository)

    president_id = uuid4()
    chancellor_id = uuid4()
    other_player_id = uuid4()

    room = GameRoom()
    room.add_player(Player(president_id, "President"))
    room.add_player(Player(chancellor_id, "Chancellor"))
    room.add_player(Player(other_player_id, "Other"))
    room.status = RoomStatus.IN_PROGRESS
    room.game_state = GameState(
        president_id=president_id, current_phase=GamePhase.NOMINATION
    )

    repository.save(room)

    command = NominateChancellorCommand(
        room_id=room.room_id,
        nominating_player_id=other_player_id,
        chancellor_id=chancellor_id,
    )

    with pytest.raises(ValueError, match="Only the president"):
        handler.handle(command)
