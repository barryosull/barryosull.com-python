import sqlite3
from pathlib import Path
from typing import Optional
from uuid import UUID

from src.adapters.api.rest.code_factory import CodeFactory
from src.ports.code_repository_port import CodeRepositoryPort


class SqliteCodeRepository(CodeRepositoryPort):
    def __init__(self, db_path: str = ":memory:") -> None:
        self.db_path = db_path
        self._conn: Optional[sqlite3.Connection] = None

        if db_path == ":memory:":
            self._conn = sqlite3.connect(":memory:", check_same_thread=False)
        else:
            Path(db_path).parent.mkdir(parents=True, exist_ok=True)

        self._init_database()

    def _get_connection(self) -> sqlite3.Connection:
        if self._conn is not None:
            return self._conn
        return sqlite3.connect(self.db_path)

    def _init_database(self) -> None:
        if self._conn is not None:
            conn = self._conn
            cursor = conn.cursor()
        else:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

        try:
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
            conn.commit()
        finally:
            if self._conn is None:
                conn.close()

    def _increment_counter(self) -> int:
        if self._conn is not None:
            conn = self._conn
            cursor = conn.cursor()
        else:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

        try:
            cursor.execute(
                "UPDATE code_counter SET counter = counter + 1 WHERE id = 1"
            )
            cursor.execute("SELECT counter FROM code_counter WHERE id = 1")
            result = cursor.fetchone()
            conn.commit()
            return result[0] - 1
        finally:
            if self._conn is None:
                conn.close()

    def generate_code_for_room(self, room_id: UUID) -> str:
        room_id_str = str(room_id)

        if self._conn is not None:
            conn = self._conn
            cursor = conn.cursor()
        else:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

        try:
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
            conn.commit()

            return code
        finally:
            if self._conn is None:
                conn.close()

    def find_room_by_code(self, code: str) -> Optional[UUID]:
        if self._conn is not None:
            conn = self._conn
            cursor = conn.cursor()
        else:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

        try:
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
        finally:
            if self._conn is None:
                conn.close()

    def get_code_for_room(self, room_id: UUID) -> Optional[str]:
        room_id_str = str(room_id)

        if self._conn is not None:
            conn = self._conn
            cursor = conn.cursor()
        else:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

        try:
            cursor.execute(
                "SELECT code FROM code_mappings WHERE room_id = ?", (room_id_str,)
            )
            result = cursor.fetchone()

            return result[0] if result else None
        finally:
            if self._conn is None:
                conn.close()
