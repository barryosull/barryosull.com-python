from uuid import uuid4

import pytest

from backend.adapters.persistence.in_memory_repository import InMemoryRoomRepository
from backend.application.command_bus import CommandBus
from backend.application.commands.nominate_chancellor import NominateChancellorCommand
from backend.domain.entities.game_room import GameRoom, RoomStatus
from backend.domain.entities.game_state import GamePhase, GameState
from backend.domain.entities.player import Player


def test_nominate_chancellor_success():
    repository = InMemoryRoomRepository()
    command_bus = CommandBus(repository)

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
    command_bus.execute(command)

    updated_room = repository.find_by_id(room.room_id)
    assert updated_room.game_state.nominated_chancellor_id == chancellor_id
    assert updated_room.game_state.current_phase == GamePhase.ELECTION


def test_nominate_chancellor_room_not_found():
    repository = InMemoryRoomRepository()
    command_bus = CommandBus(repository)

    command = NominateChancellorCommand(
        room_id=uuid4(), nominating_player_id=uuid4(), chancellor_id=uuid4()
    )

    with pytest.raises(ValueError, match="not found"):
        command_bus.execute(command)


def test_nominate_chancellor_game_not_started():
    repository = InMemoryRoomRepository()
    command_bus = CommandBus(repository)

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
        command_bus.execute(command)


def test_nominate_chancellor_wrong_phase():
    repository = InMemoryRoomRepository()
    command_bus = CommandBus(repository)

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
        command_bus.execute(command)


def test_nominate_chancellor_not_president():
    repository = InMemoryRoomRepository()
    command_bus = CommandBus(repository)

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
        command_bus.execute(command)
