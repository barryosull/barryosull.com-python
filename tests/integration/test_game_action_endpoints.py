import random
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from src.adapters.api.main import app
from src.adapters.persistence.in_memory_repository import InMemoryRoomRepository
from src.application.command_bus import CommandBus
from src.domain.entities.game_room import GameRoom
from src.domain.entities.game_state import GamePhase, GameState
from src.domain.entities.player import Player
from src.domain.services.role_assignment_service import RoleAssignmentService

client = TestClient(app)


def start_game_for_room(room: GameRoom) -> None:
    player_ids = [p.player_id for p in room.players]
    role_assignments = RoleAssignmentService.assign_roles(player_ids)
    first_president_id = random.choice(player_ids)
    game_state = GameState(
        round_number=1,
        president_id=first_president_id,
        current_phase=GamePhase.NOMINATION,
        role_assignments=role_assignments,
    )
    room.start_game(game_state)


def test_nominate_chancellor_success(monkeypatch):
    repository = InMemoryRoomRepository()

    room = GameRoom()
    player_ids = [uuid4() for _ in range(5)]

    for i, player_id in enumerate(player_ids):
        room.add_player(Player(player_id, f"Player{i}"))

    start_game_for_room(room)
    repository.save(room)

    president_id = room.game_state.president_id
    chancellor_id = [pid for pid in player_ids if pid != president_id][0]

    import src.adapters.api.rest.routes as routes_module

    monkeypatch.setattr(routes_module, "repository", repository)
    monkeypatch.setattr(routes_module, "command_bus", CommandBus(repository))

    response = client.post(
        f"/api/games/{room.room_id}/nominate",
        json={"player_id": str(president_id), "chancellor_id": str(chancellor_id)},
    )

    assert response.status_code == 204

    updated_room = repository.find_by_id(room.room_id)
    assert updated_room.game_state.nominated_chancellor_id == chancellor_id


def test_nominate_chancellor_not_president(monkeypatch):
    repository = InMemoryRoomRepository()

    room = GameRoom()
    player_ids = [uuid4() for _ in range(5)]

    for i, player_id in enumerate(player_ids):
        room.add_player(Player(player_id, f"Player{i}"))

    start_game_for_room(room)
    repository.save(room)

    president_id = room.game_state.president_id
    other_player_id = [pid for pid in player_ids if pid != president_id][0]
    chancellor_id = [pid for pid in player_ids if pid not in [president_id, other_player_id]][0]

    import src.adapters.api.rest.routes as routes_module

    monkeypatch.setattr(routes_module, "repository", repository)
    monkeypatch.setattr(routes_module, "command_bus", CommandBus(repository))

    response = client.post(
        f"/api/games/{room.room_id}/nominate",
        json={"player_id": str(other_player_id), "chancellor_id": str(chancellor_id)},
    )

    assert response.status_code == 400


def test_cast_vote_success(monkeypatch):
    repository = InMemoryRoomRepository()

    room = GameRoom()
    player_ids = [uuid4() for _ in range(5)]

    for i, player_id in enumerate(player_ids):
        room.add_player(Player(player_id, f"Player{i}"))

    start_game_for_room(room)
    president_id = room.game_state.president_id
    chancellor_id = [pid for pid in player_ids if pid != president_id][0]
    room.game_state.nominated_chancellor_id = chancellor_id
    room.game_state.current_phase = GamePhase.ELECTION
    repository.save(room)

    import src.adapters.api.rest.routes as routes_module

    monkeypatch.setattr(routes_module, "repository", repository)
    monkeypatch.setattr(routes_module, "command_bus", CommandBus(repository))

    for player_id in player_ids:
        response = client.post(
            f"/api/games/{room.room_id}/vote",
            json={"player_id": str(player_id), "vote": True},
        )
        assert response.status_code == 204


def test_discard_policy_success(monkeypatch):
    repository = InMemoryRoomRepository()

    room = GameRoom()
    player_ids = [uuid4() for _ in range(5)]

    for i, player_id in enumerate(player_ids):
        room.add_player(Player(player_id, f"Player{i}"))

    start_game_for_room(room)
    president_id = room.game_state.president_id
    chancellor_id = [pid for pid in player_ids if pid != president_id][0]
    room.game_state.nominated_chancellor_id = chancellor_id
    room.game_state.current_phase = GamePhase.ELECTION

    for player_id in player_ids:
        room.game_state.votes[player_id] = True

    room.game_state.chancellor_id = chancellor_id
    room.game_state.current_phase = GamePhase.LEGISLATIVE_PRESIDENT
    room.game_state.president_policies = room.game_state.policy_deck.draw(3)

    repository.save(room)

    policy_type = room.game_state.president_policies[0].type.value

    import src.adapters.api.rest.routes as routes_module

    monkeypatch.setattr(routes_module, "repository", repository)
    monkeypatch.setattr(routes_module, "command_bus", CommandBus(repository))

    response = client.post(
        f"/api/games/{room.room_id}/discard-policy",
        json={"player_id": str(president_id), "policy_type": policy_type},
    )

    assert response.status_code == 204


def test_enact_policy_success(monkeypatch):
    repository = InMemoryRoomRepository()

    room = GameRoom()
    player_ids = [uuid4() for _ in range(5)]

    for i, player_id in enumerate(player_ids):
        room.add_player(Player(player_id, f"Player{i}"))

    start_game_for_room(room)
    president_id = room.game_state.president_id
    chancellor_id = [pid for pid in player_ids if pid != president_id][0]
    room.game_state.nominated_chancellor_id = chancellor_id
    room.game_state.current_phase = GamePhase.ELECTION

    for player_id in player_ids:
        room.game_state.votes[player_id] = True

    room.game_state.chancellor_id = chancellor_id
    room.game_state.current_phase = GamePhase.LEGISLATIVE_PRESIDENT
    room.game_state.president_policies = room.game_state.policy_deck.draw(3)

    policy_to_discard = room.game_state.president_policies[0]
    room.game_state.chancellor_policies = [p for p in room.game_state.president_policies if p is not policy_to_discard]
    room.game_state.current_phase = GamePhase.LEGISLATIVE_CHANCELLOR

    repository.save(room)

    policy_type = room.game_state.chancellor_policies[0].type.value

    import src.adapters.api.rest.routes as routes_module

    monkeypatch.setattr(routes_module, "repository", repository)
    monkeypatch.setattr(routes_module, "command_bus", CommandBus(repository))

    response = client.post(
        f"/api/games/{room.room_id}/enact-policy",
        json={"player_id": str(chancellor_id), "policy_type": policy_type},
    )

    assert response.status_code == 204


def test_get_game_state_success(monkeypatch):
    repository = InMemoryRoomRepository()

    room = GameRoom()
    player_ids = [uuid4() for _ in range(5)]

    for i, player_id in enumerate(player_ids):
        room.add_player(Player(player_id, f"Player{i}"))

    start_game_for_room(room)
    repository.save(room)

    import src.adapters.api.rest.routes as routes_module

    monkeypatch.setattr(routes_module, "repository", repository)
    monkeypatch.setattr(routes_module, "command_bus", CommandBus(repository))

    response = client.get(f"/api/games/{room.room_id}/state")

    assert response.status_code == 200
    data = response.json()
    assert data["round_number"] == 1
    assert data["liberal_policies"] == 0
    assert data["fascist_policies"] == 0
    assert data["election_tracker"] == 0


def test_get_game_state_not_started(monkeypatch):
    repository = InMemoryRoomRepository()

    room = GameRoom()
    player_ids = [uuid4() for _ in range(5)]

    for i, player_id in enumerate(player_ids):
        room.add_player(Player(player_id, f"Player{i}"))

    repository.save(room)

    import src.adapters.api.rest.routes as routes_module

    monkeypatch.setattr(routes_module, "repository", repository)
    monkeypatch.setattr(routes_module, "command_bus", CommandBus(repository))

    response = client.get(f"/api/games/{room.room_id}/state")

    assert response.status_code == 404
    assert "not started" in response.json()["detail"].lower()


def test_get_my_role_success(monkeypatch):
    repository = InMemoryRoomRepository()

    room = GameRoom()
    player_ids = [uuid4() for _ in range(5)]

    for i, player_id in enumerate(player_ids):
        room.add_player(Player(player_id, f"Player{i}"))

    start_game_for_room(room)
    repository.save(room)

    import src.adapters.api.rest.routes as routes_module

    monkeypatch.setattr(routes_module, "repository", repository)
    monkeypatch.setattr(routes_module, "command_bus", CommandBus(repository))

    response = client.get(
        f"/api/games/{room.room_id}/my-role", params={"player_id": str(player_ids[0])}
    )

    assert response.status_code == 200
    data = response.json()
    assert "team" in data
    assert "is_hitler" in data
    assert data["team"] in ["LIBERAL", "FASCIST"]
    assert isinstance(data["is_hitler"], bool)


def test_get_my_role_not_started(monkeypatch):
    repository = InMemoryRoomRepository()

    room = GameRoom()
    player_ids = [uuid4() for _ in range(5)]

    for i, player_id in enumerate(player_ids):
        room.add_player(Player(player_id, f"Player{i}"))

    repository.save(room)

    import src.adapters.api.rest.routes as routes_module

    monkeypatch.setattr(routes_module, "repository", repository)
    monkeypatch.setattr(routes_module, "command_bus", CommandBus(repository))

    response = client.get(
        f"/api/games/{room.room_id}/my-role", params={"player_id": str(player_ids[0])}
    )

    assert response.status_code == 404
    assert "not started" in response.json()["detail"].lower()
