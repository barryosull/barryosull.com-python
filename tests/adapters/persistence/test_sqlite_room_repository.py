import sqlite3
import tempfile
from pathlib import Path
from uuid import uuid4

import pytest

from src.adapters.persistence.sqlite_room_repository import SqliteRoomRepository
from src.domain.entities.game_room import GameRoom
from src.domain.entities.player import Player


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
        db_path = Path(tmpdir) / "rooms.db"
        assert not db_path.exists()

        conn = sqlite3.connect(str(db_path))
        SqliteRoomRepository(conn)
        conn.close()

        assert db_path.exists()


def test_in_memory_database_works(in_memory_conn):
    repo = SqliteRoomRepository(in_memory_conn)
    repo.init_tables()

    room = GameRoom()
    player = Player(uuid4(), "Alice")
    room.add_player(player)

    repo.save(room)

    retrieved_room = repo.find_by_id(room.room_id)
    assert retrieved_room is not None
    assert retrieved_room.room_id == room.room_id
    assert len(retrieved_room.players) == 1
    assert retrieved_room.players[0].name == "Alice"


def test_database_schema_is_correct(temp_db_path):
    conn = sqlite3.connect(temp_db_path)
    repo = SqliteRoomRepository(conn)
    repo.init_tables()
    conn.close()

    with sqlite3.connect(temp_db_path) as conn:
        cursor = conn.cursor()

        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
        )
        tables = [row[0] for row in cursor.fetchall()]
        assert "rooms" in tables

        cursor.execute("PRAGMA table_info(rooms)")
        columns = {row[1]: row[2] for row in cursor.fetchall()}
        assert columns == {"room_id": "TEXT", "room_data": "BLOB"}


def test_corrupted_data_is_handled_gracefully(in_memory_conn):
    repo = SqliteRoomRepository(in_memory_conn)
    repo.init_tables()
    
    cursor = in_memory_conn.cursor()
    cursor.execute(
        "INSERT INTO rooms (room_id, room_data) VALUES (?, ?)",
        (str(uuid4()), b"corrupted data"),
    )
    in_memory_conn.commit()

    assert repo.list_all() == []

