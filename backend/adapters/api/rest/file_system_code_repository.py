import json
from pathlib import Path
from typing import Optional
from uuid import UUID

from backend.adapters.api.rest.code_factory import CodeFactory
from backend.ports.code_repository_port import CodeRepositoryPort


class FileSystemCodeRepository(CodeRepositoryPort):
    def __init__(self, base_path: str = "/tmp") -> None:
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
        self.counter_file = self.base_path / "code_counter.json"
        self.mappings_file = self.base_path / "code_mappings.json"

    def _load_counter(self) -> int:
        if not self.counter_file.exists():
            return 1
        try:
            with open(self.counter_file, "r") as f:
                data = json.load(f)
                return data.get("counter", 1)
        except (json.JSONDecodeError, FileNotFoundError):
            return 1

    def _save_counter(self, counter: int) -> None:
        with open(self.counter_file, "w") as f:
            json.dump({"counter": counter}, f)

    def _load_mappings(self) -> dict:
        if not self.mappings_file.exists():
            return {"code_to_room": {}, "room_to_code": {}}
        try:
            with open(self.mappings_file, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return {"code_to_room": {}, "room_to_code": {}}

    def _save_mappings(self, mappings: dict) -> None:
        with open(self.mappings_file, "w") as f:
            json.dump(mappings, f, indent=2)

    def generate_code_for_room(self, room_id: UUID) -> str:
        room_id_str = str(room_id)
        mappings = self._load_mappings()

        if room_id_str in mappings["room_to_code"]:
            return mappings["room_to_code"][room_id_str]

        counter = self._load_counter()
        code = CodeFactory.int_to_code(counter)

        mappings["code_to_room"][code] = room_id_str
        mappings["room_to_code"][room_id_str] = code

        self._save_mappings(mappings)
        self._save_counter(counter + 1)

        return code

    def find_room_by_code(self, code: str) -> Optional[UUID]:
        mappings = self._load_mappings()
        room_id_str = mappings["code_to_room"].get(code)

        if room_id_str is None:
            return None

        try:
            return UUID(room_id_str)
        except ValueError:
            return None

    def get_code_for_room(self, room_id: UUID) -> Optional[str]:
        room_id_str = str(room_id)
        mappings = self._load_mappings()
        return mappings["room_to_code"].get(room_id_str)
