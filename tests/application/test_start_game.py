from uuid import uuid4

import pytest

from src.adapters.persistence.in_memory_repository import InMemoryRoomRepository
from src.application.command_bus import CommandBus
from src.application.commands.start_game import StartGameCommand
from src.domain.entities.game_room import GameRoom, RoomStatus
from src.domain.entities.game_state import GamePhase
from src.domain.entities.player import Player


def test_start_game_success():
    repository = InMemoryRoomRepository()
    command_bus = CommandBus(repository)

    room = GameRoom()
    creator_id = uuid4()

    for i in range(5):
        player_id = creator_id if i == 0 else uuid4()
        room.add_player(Player(player_id, f"Player{i}"))

    repository.save(room)

    command = StartGameCommand(room_id=room.room_id, requester_id=creator_id)
    command_bus.execute(command)

    updated_room = repository.find_by_id(room.room_id)
    assert updated_room.status == RoomStatus.IN_PROGRESS
    assert updated_room.game_state is not None
    assert updated_room.game_state.current_phase == GamePhase.NOMINATION
    assert updated_room.game_state.president_id is not None
    assert len(updated_room.game_state.role_assignments) == 5


def test_start_game_room_not_found():
    repository = InMemoryRoomRepository()
    command_bus = CommandBus(repository)

    command = StartGameCommand(room_id=uuid4(), requester_id=uuid4())

    with pytest.raises(ValueError, match="not found"):
        command_bus.execute(command)


def test_start_game_not_creator():
    repository = InMemoryRoomRepository()
    command_bus = CommandBus(repository)

    room = GameRoom()
    creator_id = uuid4()
    other_player_id = uuid4()

    for i in range(5):
        player_id = creator_id if i == 0 else uuid4()
        room.add_player(Player(player_id, f"Player{i}"))

    repository.save(room)

    command = StartGameCommand(room_id=room.room_id, requester_id=other_player_id)

    with pytest.raises(ValueError, match="Only the room creator"):
        command_bus.execute(command)


def test_start_game_not_enough_players():
    repository = InMemoryRoomRepository()
    command_bus = CommandBus(repository)

    room = GameRoom()
    creator_id = uuid4()

    for i in range(3):
        player_id = creator_id if i == 0 else uuid4()
        room.add_player(Player(player_id, f"Player{i}"))

    repository.save(room)

    command = StartGameCommand(room_id=room.room_id, requester_id=creator_id)

    with pytest.raises(ValueError, match="at least 5 players"):
        command_bus.execute(command)


def test_start_game_with_specific_first_president():
    repository = InMemoryRoomRepository()
    command_bus = CommandBus(repository)

    room = GameRoom()
    creator_id = uuid4()
    chosen_president_id = uuid4()

    room.add_player(Player(creator_id, "Creator"))
    room.add_player(Player(chosen_president_id, "ChosenPresident"))
    for i in range(3):
        room.add_player(Player(uuid4(), f"Player{i}"))

    repository.save(room)

    command = StartGameCommand(
        room_id=room.room_id,
        requester_id=creator_id,
        first_president_id=chosen_president_id,
    )
    command_bus.execute(command)

    updated_room = repository.find_by_id(room.room_id)
    assert updated_room.game_state.president_id == chosen_president_id


def test_start_game_with_invalid_first_president():
    repository = InMemoryRoomRepository()
    command_bus = CommandBus(repository)

    room = GameRoom()
    creator_id = uuid4()
    invalid_president_id = uuid4()

    for i in range(5):
        player_id = creator_id if i == 0 else uuid4()
        room.add_player(Player(player_id, f"Player{i}"))

    repository.save(room)

    command = StartGameCommand(
        room_id=room.room_id,
        requester_id=creator_id,
        first_president_id=invalid_president_id,
    )

    with pytest.raises(ValueError, match="first_president_id must be a player"):
        command_bus.execute(command)
