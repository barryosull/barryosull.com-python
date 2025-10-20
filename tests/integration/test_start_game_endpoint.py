from uuid import uuid4, UUID

import pytest
from fastapi.testclient import TestClient

from backend.adapters.api.main import app
from backend.adapters.api.rest.code_factory import CodeFactory
from backend.adapters.persistence.in_memory_repository import InMemoryRoomRepository
from backend.application.command_bus import CommandBus
from backend.domain.entities.game_room import GameRoom
from backend.domain.entities.player import Player
from backend.ports.code_repository_port import CodeRepositoryPort

client = TestClient(app)


class InMemoryCodeRepository(CodeRepositoryPort):
    def __init__(self):
        self.counter = 1
        self.code_to_room = {}
        self.room_to_code = {}

    def generate_code_for_room(self, room_id: UUID) -> str:
        room_id_str = str(room_id)
        if room_id_str in self.room_to_code:
            return self.room_to_code[room_id_str]

        code = CodeFactory.int_to_code(self.counter)
        self.counter += 1

        self.code_to_room[code] = room_id_str
        self.room_to_code[room_id_str] = code

        return code

    def find_room_by_code(self, code: str) -> UUID | None:
        room_id_str = self.code_to_room.get(code)
        if room_id_str is None:
            return None
        try:
            return UUID(room_id_str)
        except ValueError:
            return None

    def get_code_for_room(self, room_id: UUID) -> str | None:
        room_id_str = str(room_id)
        return self.room_to_code.get(room_id_str)


def test_start_game_success(monkeypatch):
    repository = InMemoryRoomRepository()
    code_repository = InMemoryCodeRepository()

    room = GameRoom()
    creator_id = uuid4()

    for i in range(5):
        player_id = creator_id if i == 0 else uuid4()
        room.add_player(Player(player_id, f"Player{i}"))

    repository.save(room)
    room_code = code_repository.generate_code_for_room(room.room_id)

    import backend.adapters.api.rest.routes as routes_module

    monkeypatch.setattr(routes_module, "repository", repository)
    monkeypatch.setattr(routes_module, "command_bus", CommandBus(repository))
    monkeypatch.setattr(routes_module, "code_repository", code_repository)

    response = client.post(
        f"/api/rooms/{room_code}/start", json={"player_id": str(creator_id)}
    )

    assert response.status_code == 204

    updated_room = repository.find_by_id(room.room_id)
    assert updated_room.status.value == "IN_PROGRESS"
    assert updated_room.game_state is not None


def test_start_game_not_creator(monkeypatch):
    repository = InMemoryRoomRepository()
    code_repository = InMemoryCodeRepository()
    import backend.adapters.api.rest.routes as routes_module

    monkeypatch.setattr(routes_module, "repository", repository)
    monkeypatch.setattr(routes_module, "command_bus", CommandBus(repository))

    room = GameRoom()
    creator_id = uuid4()
    other_player_id = uuid4()

    for i in range(5):
        player_id = creator_id if i == 0 else (other_player_id if i == 1 else uuid4())
        room.add_player(Player(player_id, f"Player{i}"))

    repository.save(room)
    room_code = code_repository.generate_code_for_room(room.room_id)

    import backend.adapters.api.rest.routes as routes_module

    monkeypatch.setattr(routes_module, "repository", repository)
    monkeypatch.setattr(routes_module, "code_repository", code_repository)

    response = client.post(
        f"/api/rooms/{room_code}/start", json={"player_id": str(other_player_id)}
    )

    assert response.status_code == 400
    assert "only the room creator" in response.json()["detail"].lower()


def test_start_game_not_enough_players(monkeypatch):
    repository = InMemoryRoomRepository()
    code_repository = InMemoryCodeRepository()
    import backend.adapters.api.rest.routes as routes_module

    monkeypatch.setattr(routes_module, "repository", repository)
    monkeypatch.setattr(routes_module, "command_bus", CommandBus(repository))
    monkeypatch.setattr(routes_module, "code_repository", code_repository)

    room = GameRoom()
    creator_id = uuid4()

    for i in range(3):
        player_id = creator_id if i == 0 else uuid4()
        room.add_player(Player(player_id, f"Player{i}"))

    repository.save(room)
    room_code = code_repository.generate_code_for_room(room.room_id)

    response = client.post(
        f"/api/rooms/{room_code}/start", json={"player_id": str(creator_id)}
    )

    assert response.status_code == 400
    assert "at least 5 players" in response.json()["detail"].lower()


def test_start_game_room_not_found(monkeypatch):
    repository = InMemoryRoomRepository()
    code_repository = InMemoryCodeRepository()
    import backend.adapters.api.rest.routes as routes_module

    monkeypatch.setattr(routes_module, "repository", repository)
    monkeypatch.setattr(routes_module, "command_bus", CommandBus(repository))
    monkeypatch.setattr(routes_module, "code_repository", code_repository)

    fake_room_code = "FAKE"
    fake_player_id = uuid4()

    response = client.post(
        f"/api/rooms/{fake_room_code}/start", json={"player_id": str(fake_player_id)}
    )

    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()
