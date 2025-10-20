import sqlite3
import tempfile
from pathlib import Path
from uuid import uuid4

import pytest

from src.adapters.persistence.file_system_code_repository import (
    FileSystemCodeRepository,
)
from src.adapters.persistence.sqlite_code_repository import SqliteCodeRepository


@pytest.fixture
def temp_dir():
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture(
    params=[
        pytest.param("file_system", id="FileSystemCodeRepository"),
        pytest.param("sqlite", id="SqliteCodeRepository"),
    ]
)
def repository(request):
    """
    Fixture that provides all repository implementations.
    Each test using this fixture will be run for all implementations.
    """
    if request.param == "file_system":
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = FileSystemCodeRepository(base_path=tmpdir)
            yield repo
    elif request.param == "sqlite":
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            conn = sqlite3.connect(str(db_path))
            repo = SqliteCodeRepository(conn)
            yield repo
            conn.close()


def test_generate_code_for_room_creates_valid_code(repository):
    room_id = uuid4()
    code = repository.generate_code_for_room(room_id)

    assert isinstance(code, str)
    assert len(code) == 4


def test_find_room_by_code_returns_correct_room(repository):
    room_id = uuid4()
    code = repository.generate_code_for_room(room_id)

    found_room_id = repository.find_room_by_code(code)

    assert found_room_id == room_id


def test_find_room_by_code_returns_none_for_nonexistent_code(repository):
    result = repository.find_room_by_code("XXXX")

    assert result is None


def test_get_code_for_room_returns_correct_code(repository):
    room_id = uuid4()
    code = repository.generate_code_for_room(room_id)

    found_code = repository.get_code_for_room(room_id)

    assert found_code == code


def test_get_code_for_room_returns_none_for_nonexistent_room(repository):
    room_id = uuid4()
    result = repository.get_code_for_room(room_id)

    assert result is None


def test_generate_code_for_same_room_returns_same_code(repository):
    room_id = uuid4()
    code1 = repository.generate_code_for_room(room_id)
    code2 = repository.generate_code_for_room(room_id)

    assert code1 == code2


def test_generate_code_for_different_rooms_returns_different_codes(repository):
    room1_id = uuid4()
    room2_id = uuid4()

    code1 = repository.generate_code_for_room(room1_id)
    code2 = repository.generate_code_for_room(room2_id)

    assert code1 != code2


def test_sequential_rooms_get_sequential_counter_values(repository):
    room1_id = uuid4()
    room2_id = uuid4()
    room3_id = uuid4()

    code1 = repository.generate_code_for_room(room1_id)
    code2 = repository.generate_code_for_room(room2_id)
    code3 = repository.generate_code_for_room(room3_id)

    assert code1 == "QGLJ"
    assert code2 == "GX72"
    assert code3 == "7DSL"

def test_multiple_rooms_can_be_looked_up(repository):
    rooms = [uuid4() for _ in range(5)]
    codes = [repository.generate_code_for_room(room_id) for room_id in rooms]

    for room_id, code in zip(rooms, codes):
        found_room_id = repository.find_room_by_code(code)
        assert found_room_id == room_id


def test_bidirectional_lookup(repository):
    room_id = uuid4()

    code = repository.generate_code_for_room(room_id)
    found_room = repository.find_room_by_code(code)
    found_code = repository.get_code_for_room(room_id)

    assert found_room == room_id
    assert found_code == code


def test_empty_repository_starts_at_counter_zero(repository):
    room_id = uuid4()
    code = repository.generate_code_for_room(room_id)

    assert code == "QGLJ"
