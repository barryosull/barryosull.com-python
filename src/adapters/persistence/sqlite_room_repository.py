import pickle
import sqlite3
from typing import Optional
from uuid import UUID

from src.domain.entities.game_room import GameRoom
from src.ports.room_repository_port import RoomRepositoryPort


class SqliteRoomRepository(RoomRepositoryPort):
    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn
        self._init_database()

    def _init_database(self) -> None:
        cursor = self._conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS rooms (
                room_id TEXT PRIMARY KEY,
                room_data BLOB NOT NULL
            )
            """
        )
        self._conn.commit()

    def save(self, room: GameRoom) -> None:
        room_id_str = str(room.room_id)
        room_data = pickle.dumps(room)

        cursor = self._conn.cursor()
        cursor.execute(
            """
            INSERT OR REPLACE INTO rooms (room_id, room_data)
            VALUES (?, ?)
            """,
            (room_id_str, room_data),
        )
        self._conn.commit()

    def find_by_id(self, room_id: UUID) -> Optional[GameRoom]:
        room_id_str = str(room_id)
        cursor = self._conn.cursor()

        cursor.execute(
            "SELECT room_data FROM rooms WHERE room_id = ?", (room_id_str,)
        )
        result = cursor.fetchone()

        if result is None:
            return None

        try:
            return pickle.loads(result[0])
        except (pickle.UnpicklingError, ValueError):
            return None

    def delete(self, room_id: UUID) -> None:
        room_id_str = str(room_id)
        cursor = self._conn.cursor()
        cursor.execute("DELETE FROM rooms WHERE room_id = ?", (room_id_str,))
        self._conn.commit()

    def list_all(self) -> list[GameRoom]:
        cursor = self._conn.cursor()
        cursor.execute("SELECT room_data FROM rooms")
        results = cursor.fetchall()

        rooms = []
        for (room_data,) in results:
            try:
                room = pickle.loads(room_data)
                rooms.append(room)
            except (pickle.UnpicklingError, ValueError):
                continue

        return rooms

    def exists(self, room_id: UUID) -> bool:
        room_id_str = str(room_id)
        cursor = self._conn.cursor()
        cursor.execute(
            "SELECT 1 FROM rooms WHERE room_id = ? LIMIT 1", (room_id_str,)
        )
        return cursor.fetchone() is not None
