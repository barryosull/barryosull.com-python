"""
Test suite for implementation details of the file system implementation of
the room repository.
"""

import tempfile
from pathlib import Path
from uuid import uuid4

import pytest

from src.adapters.persistence.file_system_room_repository import FileSystemRoomRepository
from src.domain.entities.game_room import GameRoom, RoomStatus
from src.domain.entities.game_state import GamePhase, GameState
from src.domain.entities.player import Player
from src.domain.services.role_assignment_service import RoleAssignmentService


@pytest.fixture
def temp_dir():
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture
def repository(temp_dir):
    return FileSystemRoomRepository(base_path=temp_dir)


def test_save_writes_to_file(repository, temp_dir):
    room = GameRoom()
    player = Player(uuid4(), "TestPlayer")
    room.add_player(player)

    repository.save(room)

    file_path = Path(temp_dir) / f"secret-hitler-{room.room_id}.txt"
    assert file_path.exists()

def test_delete_deletes_file(repository, temp_dir):
    room = GameRoom()
    repository.save(room)

    file_path = Path(temp_dir) / f"secret-hitler-{room.room_id}.txt"

    repository.delete(room.room_id)
    assert not file_path.exists()
    assert repository.find_by_id(room.room_id) is None

