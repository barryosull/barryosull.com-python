from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from src.adapters.api.main import app
from src.adapters.persistence.in_memory_repository import InMemoryRoomRepository
from src.domain.entities.game_room import GameRoom
from src.domain.entities.player import Player

client = TestClient(app)


def test_start_game_success(monkeypatch):
    repository = InMemoryRoomRepository()

    room = GameRoom()
    creator_id = uuid4()

    for i in range(5):
        player_id = creator_id if i == 0 else uuid4()
        room.add_player(Player(player_id, f"Player{i}"))

    repository.save(room)

    def mock_repository():
        return repository

    import src.adapters.api.rest.routes as routes_module

    monkeypatch.setattr(routes_module, "repository", repository)

    response = client.post(
        f"/api/rooms/{room.room_id}/start", json={"player_id": str(creator_id)}
    )

    assert response.status_code == 204

    updated_room = repository.find_by_id(room.room_id)
    assert updated_room.status.value == "IN_PROGRESS"
    assert updated_room.game_state is not None


def test_start_game_not_creator(monkeypatch):
    repository = InMemoryRoomRepository()

    room = GameRoom()
    creator_id = uuid4()
    other_player_id = uuid4()

    for i in range(5):
        player_id = creator_id if i == 0 else (other_player_id if i == 1 else uuid4())
        room.add_player(Player(player_id, f"Player{i}"))

    repository.save(room)

    import src.adapters.api.rest.routes as routes_module

    monkeypatch.setattr(routes_module, "repository", repository)

    response = client.post(
        f"/api/rooms/{room.room_id}/start", json={"player_id": str(other_player_id)}
    )

    assert response.status_code == 400
    assert "only the room creator" in response.json()["detail"].lower()


def test_start_game_not_enough_players(monkeypatch):
    repository = InMemoryRoomRepository()

    room = GameRoom()
    creator_id = uuid4()

    for i in range(3):
        player_id = creator_id if i == 0 else uuid4()
        room.add_player(Player(player_id, f"Player{i}"))

    repository.save(room)

    import src.adapters.api.rest.routes as routes_module

    monkeypatch.setattr(routes_module, "repository", repository)

    response = client.post(
        f"/api/rooms/{room.room_id}/start", json={"player_id": str(creator_id)}
    )

    assert response.status_code == 400
    assert "at least 5 players" in response.json()["detail"].lower()


def test_start_game_room_not_found(monkeypatch):
    repository = InMemoryRoomRepository()

    import src.adapters.api.rest.routes as routes_module

    monkeypatch.setattr(routes_module, "repository", repository)

    fake_room_id = uuid4()
    fake_player_id = uuid4()

    response = client.post(
        f"/api/rooms/{fake_room_id}/start", json={"player_id": str(fake_player_id)}
    )

    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()
