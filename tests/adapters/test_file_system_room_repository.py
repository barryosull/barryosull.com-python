import tempfile
from pathlib import Path
from uuid import uuid4

import pytest

from backend.adapters.persistence.file_system_repository import FileSystemRoomRepository
from backend.domain.entities.game_room import GameRoom, RoomStatus
from backend.domain.entities.game_state import GamePhase, GameState
from backend.domain.entities.player import Player
from backend.domain.services.role_assignment_service import RoleAssignmentService


@pytest.fixture
def temp_dir():
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture
def repository(temp_dir):
    return FileSystemRoomRepository(base_path=temp_dir)


def test_save_and_find_by_id(repository, temp_dir):
    room = GameRoom()
    player = Player(uuid4(), "TestPlayer")
    room.add_player(player)

    repository.save(room)

    file_path = Path(temp_dir) / f"secret-hitler-{room.room_id}.txt"
    assert file_path.exists()

    retrieved_room = repository.find_by_id(room.room_id)
    assert retrieved_room is not None
    assert retrieved_room.room_id == room.room_id
    assert retrieved_room.creator_id == room.creator_id
    assert len(retrieved_room.players) == 1
    assert retrieved_room.players[0].name == "TestPlayer"


def test_find_by_id_nonexistent(repository):
    fake_room_id = uuid4()
    result = repository.find_by_id(fake_room_id)
    assert result is None


def test_delete(repository, temp_dir):
    room = GameRoom()
    repository.save(room)

    file_path = Path(temp_dir) / f"secret-hitler-{room.room_id}.txt"
    assert file_path.exists()

    repository.delete(room.room_id)
    assert not file_path.exists()
    assert repository.find_by_id(room.room_id) is None


def test_delete_nonexistent(repository):
    fake_room_id = uuid4()
    repository.delete(fake_room_id)


def test_list_all_empty(repository):
    rooms = repository.list_all()
    assert rooms == []


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


def test_exists(repository):
    room = GameRoom()
    assert not repository.exists(room.room_id)

    repository.save(room)
    assert repository.exists(room.room_id)

    repository.delete(room.room_id)
    assert not repository.exists(room.room_id)


def test_save_overwrites_existing(repository):
    room = GameRoom()
    player1 = Player(uuid4(), "Player1")
    room.add_player(player1)

    repository.save(room)

    player2 = Player(uuid4(), "Player2")
    room.add_player(player2)

    repository.save(room)

    retrieved_room = repository.find_by_id(room.room_id)
    assert len(retrieved_room.players) == 2


def test_save_and_retrieve_game_with_state(repository):
    room = GameRoom()
    player_ids = [uuid4() for _ in range(5)]

    for i, player_id in enumerate(player_ids):
        room.add_player(Player(player_id, f"Player{i}"))

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


def test_file_naming_format(repository, temp_dir):
    room = GameRoom()
    repository.save(room)

    expected_filename = f"secret-hitler-{room.room_id}.txt"
    file_path = Path(temp_dir) / expected_filename

    assert file_path.exists()
