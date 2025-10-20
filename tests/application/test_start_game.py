from uuid import uuid4

import pytest

from src.adapters.persistence.in_memory_repository import InMemoryRoomRepository
from src.application.command_bus import CommandBus
from src.application.commands.start_game import StartGameCommand
from src.domain.entities.game_room import GameRoom, RoomStatus
from src.domain.entities.game_state import GamePhase
from src.domain.entities.player import Player
from src.domain.entities.policy_deck import PolicyDeck
from src.domain.value_objects.policy import Policy, PolicyType


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


def test_start_game_with_custom_policy_deck():
    repository = InMemoryRoomRepository()
    command_bus = CommandBus(repository)

    room = GameRoom()
    creator_id = uuid4()

    for i in range(5):
        player_id = creator_id if i == 0 else uuid4()
        room.add_player(Player(player_id, f"Player{i}"))

    repository.save(room)

    custom_deck = PolicyDeck(
        draw_pile=[
            Policy(PolicyType.LIBERAL),
            Policy(PolicyType.LIBERAL),
            Policy(PolicyType.FASCIST),
        ],
        discard_pile=[],
    )

    command = StartGameCommand(
        room_id=room.room_id,
        requester_id=creator_id,
        policy_deck=custom_deck,
    )
    command_bus.execute(command)

    updated_room = repository.find_by_id(room.room_id)
    assert updated_room.status == RoomStatus.IN_PROGRESS
    assert updated_room.game_state.policy_deck.cards_remaining() == 3
    assert updated_room.game_state.policy_deck.draw_pile == [
        Policy(PolicyType.LIBERAL),
        Policy(PolicyType.LIBERAL),
        Policy(PolicyType.FASCIST),
    ]


def test_start_game_without_shuffling_players():
    repository = InMemoryRoomRepository()
    command_bus = CommandBus(repository)

    room = GameRoom()
    creator_id = uuid4()
    player_ids = [creator_id] + [uuid4() for _ in range(4)]

    for i, player_id in enumerate(player_ids):
        room.add_player(Player(player_id, f"Player{i}"))

    repository.save(room)

    command = StartGameCommand(
        room_id=room.room_id,
        requester_id=creator_id,
        shuffle_players=False,
    )
    command_bus.execute(command)

    updated_room = repository.find_by_id(room.room_id)
    assert updated_room.status == RoomStatus.IN_PROGRESS

    role_assignments = updated_room.game_state.role_assignments
    assigned_roles = [role_assignments[player_id] for player_id in player_ids]

    assert len(assigned_roles) == 5
    assert sum(1 for r in assigned_roles if r.is_liberal()) == 3
    assert (
        sum(1 for r in assigned_roles if r.is_fascist() and not r.is_hitler) == 1
    )
    assert sum(1 for r in assigned_roles if r.is_hitler) == 1
