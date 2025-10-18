from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID


class CodeRepositoryPort(ABC):
    @abstractmethod
    def generate_code_for_room(self, room_id: UUID) -> str:
        pass

    @abstractmethod
    def find_room_by_code(self, code: str) -> Optional[UUID]:
        pass

    @abstractmethod
    def get_code_for_room(self, room_id: UUID) -> Optional[str]:
        pass
