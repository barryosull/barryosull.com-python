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


@pytest.fixture
def in_memory_conn():
    conn = sqlite3.connect(":memory:", check_same_thread=False)
    yield conn
    conn.close()


def test_database_file_is_created():
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "codes.db"
        assert not db_path.exists()

        conn = sqlite3.connect(str(db_path))
        SqliteCodeRepository(conn)
        conn.close()

        assert db_path.exists()


def test_in_memory_database_works(in_memory_conn):
    repo = SqliteCodeRepository(in_memory_conn)
    room_id = uuid4()

    code = repo.generate_code_for_room(room_id)

    assert repo.find_room_by_code(code) == room_id
    assert repo.get_code_for_room(room_id) == code


def test_data_persists_across_repository_instances(temp_db_path):
    room_id = uuid4()

    conn = sqlite3.connect(temp_db_path)
    repo1 = SqliteCodeRepository(conn)
    code = repo1.generate_code_for_room(room_id)
    conn.close()

    conn = sqlite3.connect(temp_db_path)
    repo2 = SqliteCodeRepository(conn)
    found_room = repo2.find_room_by_code(code)
    found_code = repo2.get_code_for_room(room_id)
    conn.close()

    assert found_room == room_id
    assert found_code == code


def test_counter_persists_across_instances(temp_db_path):
    conn1 = sqlite3.connect(temp_db_path)
    repo1 = SqliteCodeRepository(conn1)
    room1_id = uuid4()
    code1 = repo1.generate_code_for_room(room1_id)
    conn1.close()

    conn2 = sqlite3.connect(temp_db_path)
    repo2 = SqliteCodeRepository(conn2)
    room2_id = uuid4()
    code2 = repo2.generate_code_for_room(room2_id)
    conn2.close()

    assert code1 == "QGLJ"
    assert code2 == "GX72"


def test_database_schema_is_correct(temp_db_path):
    conn = sqlite3.connect(temp_db_path)
    SqliteCodeRepository(conn)
    conn.close()

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
    conn = sqlite3.connect(temp_db_path)
    SqliteCodeRepository(conn)

    cursor = conn.cursor()
    cursor.execute("SELECT counter FROM code_counter WHERE id = 1")
    result = cursor.fetchone()
    conn.close()

    assert result[0] == 1


def test_parent_directory_is_created_if_not_exists():
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "nested" / "dir" / "codes.db"
        assert not db_path.parent.exists()

        db_path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(str(db_path))
        SqliteCodeRepository(conn)
        conn.close()

        assert db_path.parent.exists()
        assert db_path.exists()


def test_room_id_uniqueness_constraint(temp_db_path):
    conn = sqlite3.connect(temp_db_path)
    repo = SqliteCodeRepository(conn)
    room_id = uuid4()

    code1 = repo.generate_code_for_room(room_id)
    code2 = repo.generate_code_for_room(room_id)

    assert code1 == code2

    cursor = conn.cursor()
    cursor.execute(
        "SELECT COUNT(*) FROM code_mappings WHERE room_id = ?", (str(room_id),)
    )
    count = cursor.fetchone()[0]
    conn.close()

    assert count == 1


def test_code_uniqueness_constraint(temp_db_path):
    conn = sqlite3.connect(temp_db_path)
    repo = SqliteCodeRepository(conn)

    room_ids = [uuid4() for _ in range(10)]
    codes = [repo.generate_code_for_room(room_id) for room_id in room_ids]
    conn.close()

    assert len(codes) == len(set(codes))
