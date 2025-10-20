import sqlite3
from typing import Optional
from uuid import UUID

from src.adapters.api.rest.code_factory import CodeFactory
from src.ports.code_repository_port import CodeRepositoryPort


class SqliteCodeRepository(CodeRepositoryPort):
    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn
        self._init_database()

    def _init_database(self) -> None:
        cursor = self._conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS code_counter (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                counter INTEGER NOT NULL DEFAULT 1
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS code_mappings (
                code TEXT PRIMARY KEY,
                room_id TEXT NOT NULL UNIQUE
            )
            """
        )
        cursor.execute(
            "INSERT OR IGNORE INTO code_counter (id, counter) VALUES (1, 1)"
        )
        self._conn.commit()

    def _increment_counter(self) -> int:
        cursor = self._conn.cursor()
        cursor.execute(
            "UPDATE code_counter SET counter = counter + 1 WHERE id = 1"
        )
        cursor.execute("SELECT counter FROM code_counter WHERE id = 1")
        result = cursor.fetchone()
        self._conn.commit()
        return result[0] - 1

    def generate_code_for_room(self, room_id: UUID) -> str:
        room_id_str = str(room_id)
        cursor = self._conn.cursor()

        cursor.execute(
            "SELECT code FROM code_mappings WHERE room_id = ?", (room_id_str,)
        )
        result = cursor.fetchone()

        if result:
            return result[0]

        counter = self._increment_counter()
        code = CodeFactory.int_to_code(counter)

        cursor.execute(
            "INSERT INTO code_mappings (code, room_id) VALUES (?, ?)",
            (code, room_id_str),
        )
        self._conn.commit()

        return code

    def find_room_by_code(self, code: str) -> Optional[UUID]:
        cursor = self._conn.cursor()
        cursor.execute(
            "SELECT room_id FROM code_mappings WHERE code = ?", (code,)
        )
        result = cursor.fetchone()

        if result is None:
            return None

        try:
            return UUID(result[0])
        except ValueError:
            return None

    def get_code_for_room(self, room_id: UUID) -> Optional[str]:
        room_id_str = str(room_id)
        cursor = self._conn.cursor()

        cursor.execute(
            "SELECT code FROM code_mappings WHERE room_id = ?", (room_id_str,)
        )
        result = cursor.fetchone()

        return result[0] if result else None
