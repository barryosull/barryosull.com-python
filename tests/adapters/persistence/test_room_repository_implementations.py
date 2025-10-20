"""
Test suite for RoomRepositoryPort interface.

This file tests all implementations of RoomRepositoryPort to ensure they conform
to the interface contract. Tests are run against all implementations using
parametrized fixtures.
"""

import tempfile
from pathlib import Path
from uuid import uuid4

import pytest

from src.adapters.persistence.in_memory_repository import InMemoryRoomRepository
from src.adapters.persistence.file_system_repository import FileSystemRoomRepository
from src.domain.entities.game_room import GameRoom, RoomStatus
from src.domain.entities.game_state import GamePhase, GameState
from src.domain.entities.player import Player
from src.domain.services.role_assignment_service import RoleAssignmentService


@pytest.fixture(
    params=[
        pytest.param("in_memory", id="InMemoryRoomRepository"),
        pytest.param("file_system", id="FileSystemRoomRepository"),
    ]
)
def repository(request):
    """
    Fixture that provides all repository implementations.
    Each test using this fixture will be run for all implementations.
    """
    if request.param == "in_memory":
        repo = InMemoryRoomRepository()
        yield repo
        repo.clear()

    elif request.param == "file_system":
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = FileSystemRoomRepository(base_path=tmpdir)
            yield repo


def test_save_and_find_by_id(repository):
    room = GameRoom()
    player = Player(uuid4(), "Alice")
    room.add_player(player)

    repository.save(room)

    retrieved_room = repository.find_by_id(room.room_id)
    assert retrieved_room is not None
    assert retrieved_room.room_id == room.room_id
    assert retrieved_room.creator_id == room.creator_id
    assert len(retrieved_room.players) == 1
    assert retrieved_room.players[0].name == "Alice"


def test_find_by_id_nonexistent(repository):
    fake_room_id = uuid4()
    result = repository.find_by_id(fake_room_id)
    assert result is None


def test_save_overwrites_existing(repository):
    room = GameRoom()
    player1 = Player(uuid4(), "Player1")
    room.add_player(player1)

    repository.save(room)

    # Modify and save again
    player2 = Player(uuid4(), "Player2")
    room.add_player(player2)
    repository.save(room)

    # Verify the update
    retrieved_room = repository.find_by_id(room.room_id)
    assert retrieved_room is not None
    assert len(retrieved_room.players) == 2


def test_delete(repository):
    room = GameRoom()
    repository.save(room)

    assert repository.find_by_id(room.room_id) is not None

    repository.delete(room.room_id)

    assert repository.find_by_id(room.room_id) is None


def test_delete_nonexistent(repository):
    fake_room_id = uuid4()
    repository.delete(fake_room_id)


def test_exists_returns_false_for_nonexistent(repository):
    fake_room_id = uuid4()
    assert not repository.exists(fake_room_id)


def test_exists_returns_true_after_save(repository):
    room = GameRoom()
    assert not repository.exists(room.room_id)

    repository.save(room)
    assert repository.exists(room.room_id)


def test_exists_returns_false_after_delete(repository):
    room = GameRoom()
    repository.save(room)
    assert repository.exists(room.room_id)

    repository.delete(room.room_id)
    assert not repository.exists(room.room_id)


def test_list_all_empty(repository):
    rooms = repository.list_all()
    assert rooms == []


def test_list_all_single_room(repository):
    room = GameRoom()
    repository.save(room)

    rooms = repository.list_all()
    assert len(rooms) == 1
    assert rooms[0].room_id == room.room_id


def test_list_all_multiple_rooms(repository):
    room1 = GameRoom()
    room2 = GameRoom()
    room3 = GameRoom()

    repository.save(room1)
    repository.save(room2)
    repository.save(room3)

    rooms = repository.list_all()
    assert len(rooms) == 3

    room_ids = {r.room_id for r in rooms}
    assert room1.room_id in room_ids
    assert room2.room_id in room_ids
    assert room3.room_id in room_ids


def test_list_all_excludes_deleted_rooms(repository):
    room1 = GameRoom()
    room2 = GameRoom()

    repository.save(room1)
    repository.save(room2)

    assert len(repository.list_all()) == 2

    repository.delete(room1.room_id)

    rooms = repository.list_all()
    assert len(rooms) == 1
    assert rooms[0].room_id == room2.room_id


def test_save_and_retrieve_room_with_multiple_players(repository):
    room = GameRoom()

    for i in range(5):
        player = Player(uuid4(), f"Player{i}")
        room.add_player(player)

    repository.save(room)

    retrieved_room = repository.find_by_id(room.room_id)
    assert retrieved_room is not None
    assert len(retrieved_room.players) == 5

    player_names = {p.name for p in retrieved_room.players}
    for i in range(5):
        assert f"Player{i}" in player_names


def test_save_and_retrieve_game_with_state(repository):
    room = GameRoom()
    player_ids = [uuid4() for _ in range(5)]

    for i, player_id in enumerate(player_ids):
        room.add_player(Player(player_id, f"Player{i}"))

    # Start the game
    role_assignments = RoleAssignmentService.assign_roles(player_ids)
    game_state = GameState(
        round_number=1,
        president_id=player_ids[0],
        current_phase=GamePhase.NOMINATION,
        role_assignments=role_assignments,
    )
    room.start_game(game_state)

    repository.save(room)

    retrieved_room = repository.find_by_id(room.room_id)
    assert retrieved_room is not None
    assert retrieved_room.status == RoomStatus.IN_PROGRESS
    assert retrieved_room.game_state is not None
    assert retrieved_room.game_state.round_number == 1
    assert retrieved_room.game_state.president_id == player_ids[0]
    assert retrieved_room.game_state.current_phase == GamePhase.NOMINATION
    assert len(retrieved_room.game_state.role_assignments) == 5


def test_save_room_with_game_progression(repository):
    room = GameRoom()
    player_ids = [uuid4() for _ in range(5)]

    for i, player_id in enumerate(player_ids):
        room.add_player(Player(player_id, f"Player{i}"))

    # Start game
    role_assignments = RoleAssignmentService.assign_roles(player_ids)
    game_state = GameState(
        round_number=1,
        president_id=player_ids[0],
        current_phase=GamePhase.NOMINATION,
        role_assignments=role_assignments,
    )
    room.start_game(game_state)

    room.game_state.nominated_chancellor_id = player_ids[1]
    room.game_state.current_phase = GamePhase.ELECTION
    room.game_state.liberal_policies = 2
    room.game_state.fascist_policies = 1

    repository.save(room)

    retrieved_room = repository.find_by_id(room.room_id)
    assert retrieved_room.game_state.nominated_chancellor_id == player_ids[1]
    assert retrieved_room.game_state.current_phase == GamePhase.ELECTION
    assert retrieved_room.game_state.liberal_policies == 2
    assert retrieved_room.game_state.fascist_policies == 1


def test_save_multiple_rooms_independently(repository):
    rooms = []
    for i in range(10):
        room = GameRoom()
        player = Player(uuid4(), f"Player{i}")
        room.add_player(player)
        rooms.append(room)
        repository.save(room)

    for i, original_room in enumerate(rooms):
        retrieved = repository.find_by_id(original_room.room_id)
        assert retrieved is not None
        assert retrieved.room_id == original_room.room_id
        assert len(retrieved.players) == 1
        assert retrieved.players[0].name == f"Player{i}"


def test_repository_handles_empty_room(repository):
    room = GameRoom()

    repository.save(room)

    retrieved_room = repository.find_by_id(room.room_id)
    assert retrieved_room is not None
    assert retrieved_room.room_id == room.room_id
    assert len(retrieved_room.players) == 0


def test_update_does_not_affect_other_rooms(repository):
    room1 = GameRoom()
    room1.add_player(Player(uuid4(), "Alice"))
    repository.save(room1)

    room2 = GameRoom()
    room2.add_player(Player(uuid4(), "Bob"))
    repository.save(room2)

    room1.add_player(Player(uuid4(), "Charlie"))
    repository.save(room1)

    retrieved_room2 = repository.find_by_id(room2.room_id)
    assert len(retrieved_room2.players) == 1
    assert retrieved_room2.players[0].name == "Bob"
