import pickle
from pathlib import Path
from typing import Optional
from uuid import UUID

from src.domain.entities.game_room import GameRoom
from src.ports.room_repository_port import RoomRepositoryPort


class FileSystemRoomRepository(RoomRepositoryPort):
    def __init__(self, base_path: str = "/tmp") -> None:
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)

    def _get_file_path(self, room_id: UUID) -> Path:
        return self.base_path / f"secret-hitler-{room_id}.txt"

    def save(self, room: GameRoom) -> None:
        file_path = self._get_file_path(room.room_id)
        with open(file_path, "wb") as f:
            pickle.dump(room, f)

    def find_by_id(self, room_id: UUID) -> Optional[GameRoom]:
        file_path = self._get_file_path(room_id)
        if not file_path.exists():
            return None

        try:
            with open(file_path, "rb") as f:
                return pickle.load(f)
        except (FileNotFoundError, pickle.UnpicklingError):
            return None

    def delete(self, room_id: UUID) -> None:
        file_path = self._get_file_path(room_id)
        file_path.unlink(missing_ok=True)

    def list_all(self) -> list[GameRoom]:
        rooms = []
        for file_path in self.base_path.glob("secret-hitler-*.txt"):
            try:
                with open(file_path, "rb") as f:
                    room = pickle.load(f)
                    rooms.append(room)
            except (pickle.UnpicklingError, EOFError):
                continue
        return rooms

    def exists(self, room_id: UUID) -> bool:
        return self._get_file_path(room_id).exists()
