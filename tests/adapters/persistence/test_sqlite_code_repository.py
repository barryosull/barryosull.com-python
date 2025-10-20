import sqlite3
import tempfile
from pathlib import Path
from uuid import uuid4

import pytest

from src.adapters.persistence.sqlite_code_repository import SqliteCodeRepository


@pytest.fixture
def temp_db_path():
    with tempfile.TemporaryDirectory() as tmpdir:
        yield str(Path(tmpdir) / "test.db")


def test_database_file_is_created():
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "codes.db"
        assert not db_path.exists()

        SqliteCodeRepository(db_path=str(db_path))

        assert db_path.exists()


def test_in_memory_database_works():
    repo = SqliteCodeRepository(db_path=":memory:")
    room_id = uuid4()

    code = repo.generate_code_for_room(room_id)

    assert repo.find_room_by_code(code) == room_id
    assert repo.get_code_for_room(room_id) == code


def test_data_persists_across_repository_instances(temp_db_path):
    room_id = uuid4()

    repo1 = SqliteCodeRepository(db_path=temp_db_path)
    code = repo1.generate_code_for_room(room_id)

    repo2 = SqliteCodeRepository(db_path=temp_db_path)
    found_room = repo2.find_room_by_code(code)
    found_code = repo2.get_code_for_room(room_id)

    assert found_room == room_id
    assert found_code == code


def test_counter_persists_across_instances(temp_db_path):
    repo1 = SqliteCodeRepository(db_path=temp_db_path)
    room1_id = uuid4()
    code1 = repo1.generate_code_for_room(room1_id)

    repo2 = SqliteCodeRepository(db_path=temp_db_path)
    room2_id = uuid4()
    code2 = repo2.generate_code_for_room(room2_id)

    assert code1 == "QGLJ"
    assert code2 == "GX72"


def test_database_schema_is_correct(temp_db_path):
    SqliteCodeRepository(db_path=temp_db_path)

    with sqlite3.connect(temp_db_path) as conn:
        cursor = conn.cursor()

        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
        )
        tables = [row[0] for row in cursor.fetchall()]
        assert "code_counter" in tables
        assert "code_mappings" in tables

        cursor.execute("PRAGMA table_info(code_counter)")
        counter_columns = {row[1]: row[2] for row in cursor.fetchall()}
        assert counter_columns == {"id": "INTEGER", "counter": "INTEGER"}

        cursor.execute("PRAGMA table_info(code_mappings)")
        mappings_columns = {row[1]: row[2] for row in cursor.fetchall()}
        assert mappings_columns == {"code": "TEXT", "room_id": "TEXT"}


def test_counter_starts_at_one(temp_db_path):
    repo = SqliteCodeRepository(db_path=temp_db_path)

    with sqlite3.connect(temp_db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT counter FROM code_counter WHERE id = 1")
        result = cursor.fetchone()

        assert result[0] == 1


def test_parent_directory_is_created_if_not_exists():
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "nested" / "dir" / "codes.db"
        assert not db_path.parent.exists()

        SqliteCodeRepository(db_path=str(db_path))

        assert db_path.parent.exists()
        assert db_path.exists()


def test_room_id_uniqueness_constraint(temp_db_path):
    repo = SqliteCodeRepository(db_path=temp_db_path)
    room_id = uuid4()

    code1 = repo.generate_code_for_room(room_id)
    code2 = repo.generate_code_for_room(room_id)

    assert code1 == code2

    with sqlite3.connect(temp_db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM code_mappings WHERE room_id = ?", (str(room_id),))
        count = cursor.fetchone()[0]
        assert count == 1


def test_code_uniqueness_constraint(temp_db_path):
    repo = SqliteCodeRepository(db_path=temp_db_path)

    room_ids = [uuid4() for _ in range(10)]
    codes = [repo.generate_code_for_room(room_id) for room_id in room_ids]

    assert len(codes) == len(set(codes))
