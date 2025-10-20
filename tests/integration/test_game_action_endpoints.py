import random
from uuid import uuid4, UUID

from fastapi.testclient import TestClient

from src.adapters.api.main import app
from src.adapters.api.rest.code_factory import CodeFactory
from src.adapters.persistence.in_memory_room_repository import InMemoryRoomRepository
from src.application.command_bus import CommandBus
from src.domain.entities.game_room import GameRoom
from src.domain.entities.game_state import GamePhase, GameState
from src.domain.entities.player import Player
from src.domain.services.role_assignment_service import RoleAssignmentService
from src.ports.code_repository_port import CodeRepositoryPort

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


# Deps and dep injection
room_repository = InMemoryRoomRepository()
code_repository = InMemoryCodeRepository()

def monkeypatch_deps(monkeypatch):
    import src.adapters.api.rest.routes as routes_module

    def mock_make_code_repository():
        return code_repository
    
    def mock_make_room_repository():
        return room_repository
    
    def make_command_bus():
        return CommandBus(room_repository)

    monkeypatch.setattr(routes_module, "make_room_repository", mock_make_room_repository)
    monkeypatch.setattr(routes_module, "make_code_repository", mock_make_code_repository)
    monkeypatch.setattr(routes_module, "make_command_bus", make_command_bus)


def test_nominate_chancellor_success(monkeypatch):
    room = GameRoom()
    player_ids = [uuid4() for _ in range(5)]

    for i, player_id in enumerate(player_ids):
        room.add_player(Player(player_id, f"Player{i}"))

    start_game_for_room(room)
    room_repository.save(room)
    room_code = code_repository.generate_code_for_room(room.room_id)

    president_id = room.game_state.president_id
    chancellor_id = [pid for pid in player_ids if pid != president_id][0]

    monkeypatch_deps(monkeypatch)

    response = client.post(
        f"/api/games/{room_code}/nominate",
        json={"player_id": str(president_id), "chancellor_id": str(chancellor_id)},
    )

    assert response.status_code == 204

    updated_room = room_repository.find_by_id(room.room_id)
    assert updated_room.game_state.nominated_chancellor_id == chancellor_id


def test_nominate_chancellor_not_president(monkeypatch):
    room = GameRoom()
    player_ids = [uuid4() for _ in range(5)]

    for i, player_id in enumerate(player_ids):
        room.add_player(Player(player_id, f"Player{i}"))

    start_game_for_room(room)
    room_repository.save(room)
    room_code = code_repository.generate_code_for_room(room.room_id)

    president_id = room.game_state.president_id
    other_player_id = [pid for pid in player_ids if pid != president_id][0]
    chancellor_id = [pid for pid in player_ids if pid not in [president_id, other_player_id]][0]

    monkeypatch_deps(monkeypatch)

    response = client.post(
        f"/api/games/{room_code}/nominate",
        json={"player_id": str(other_player_id), "chancellor_id": str(chancellor_id)},
    )

    assert response.status_code == 400


def test_cast_vote_success(monkeypatch):
    room = GameRoom()
    player_ids = [uuid4() for _ in range(5)]

    for i, player_id in enumerate(player_ids):
        room.add_player(Player(player_id, f"Player{i}"))

    start_game_for_room(room)
    president_id = room.game_state.president_id
    chancellor_id = [pid for pid in player_ids if pid != president_id][0]
    room.game_state.nominated_chancellor_id = chancellor_id
    room.game_state.current_phase = GamePhase.ELECTION
    room_repository.save(room)
    room_code = code_repository.generate_code_for_room(room.room_id)

    monkeypatch_deps(monkeypatch)

    for player_id in player_ids:
        if player_id == president_id:
            continue
        response = client.post(
            f"/api/games/{room_code}/vote",
            json={"player_id": str(player_id), "vote": True},
        )
        assert response.status_code == 204


def test_discard_policy_success(monkeypatch):
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

    room_repository.save(room)
    room_code = code_repository.generate_code_for_room(room.room_id)

    policy_type = room.game_state.president_policies[0].type.value

    monkeypatch_deps(monkeypatch)

    response = client.post(
        f"/api/games/{room_code}/discard-policy",
        json={"player_id": str(president_id), "policy_type": policy_type},
    )

    assert response.status_code == 204


def test_enact_policy_success(monkeypatch):
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

    room_repository.save(room)
    room_code = code_repository.generate_code_for_room(room.room_id)

    policy_type = room.game_state.chancellor_policies[0].type.value

    monkeypatch_deps(monkeypatch)

    response = client.post(
        f"/api/games/{room_code}/enact-policy",
        json={"player_id": str(chancellor_id), "policy_type": policy_type},
    )

    assert response.status_code == 204


def test_get_game_state_success(monkeypatch):
    
    
    room = GameRoom()
    player_ids = [uuid4() for _ in range(5)]

    for i, player_id in enumerate(player_ids):
        room.add_player(Player(player_id, f"Player{i}"))

    start_game_for_room(room)
    room_repository.save(room)
    room_code = code_repository.generate_code_for_room(room.room_id)

    monkeypatch_deps(monkeypatch)

    response = client.get(f"/api/games/{room_code}/state")

    assert response.status_code == 200
    data = response.json()
    assert data["round_number"] == 1
    assert data["liberal_policies"] == 0
    assert data["fascist_policies"] == 0
    assert data["election_tracker"] == 0


def test_get_game_state_not_started(monkeypatch):
    room = GameRoom()
    player_ids = [uuid4() for _ in range(5)]

    for i, player_id in enumerate(player_ids):
        room.add_player(Player(player_id, f"Player{i}"))

    room_repository.save(room)
    room_code = code_repository.generate_code_for_room(room.room_id)

    monkeypatch_deps(monkeypatch)

    response = client.get(f"/api/games/{room_code}/state")

    assert response.status_code == 404
    assert "not started" in response.json()["detail"].lower()


def test_get_my_role_success(monkeypatch):
    room = GameRoom()
    player_ids = [uuid4() for _ in range(5)]

    for i, player_id in enumerate(player_ids):
        room.add_player(Player(player_id, f"Player{i}"))

    start_game_for_room(room)
    room_repository.save(room)
    room_code = code_repository.generate_code_for_room(room.room_id)

    monkeypatch_deps(monkeypatch)

    response = client.get(
        f"/api/games/{room_code}/my-role", params={"player_id": str(player_ids[0])}
    )

    assert response.status_code == 200
    data = response.json()
    assert "team" in data
    assert "is_hitler" in data
    assert data["team"] in ["LIBERAL", "FASCIST"]
    assert isinstance(data["is_hitler"], bool)


def test_get_my_role_not_started(monkeypatch):
    room = GameRoom()
    player_ids = [uuid4() for _ in range(5)]

    for i, player_id in enumerate(player_ids):
        room.add_player(Player(player_id, f"Player{i}"))

    room_repository.save(room)
    room_code = code_repository.generate_code_for_room(room.room_id)

    monkeypatch_deps(monkeypatch)

    response = client.get(
        f"/api/games/{room_code}/my-role", params={"player_id": str(player_ids[0])}
    )

    assert response.status_code == 404
    assert "not started" in response.json()["detail"].lower()


def test_get_my_role_includes_teammate_for_small_games(monkeypatch):
    from src.domain.value_objects.role import  Team

    room = GameRoom()
    player_ids = [uuid4() for _ in range(5)]

    for i, player_id in enumerate(player_ids):
        room.add_player(Player(player_id, f"Player{i}"))

    start_game_for_room(room)

    hitler_id = None
    fascist_id = None
    for player_id, role in room.game_state.role_assignments.items():
        if role.team == Team.FASCIST and role.is_hitler:
            hitler_id = player_id
        elif role.team == Team.FASCIST and not role.is_hitler:
            fascist_id = player_id

    assert hitler_id is not None, f"Hitler not found in role assignments"
    assert fascist_id is not None, f"Fascist not found in role assignments"

    room_repository.save(room)
    room_code = code_repository.generate_code_for_room(room.room_id)

    monkeypatch_deps(monkeypatch)

    fascist_response = client.get(
        f"/api/games/{room_code}/my-role", params={"player_id": str(fascist_id)}
    )
    assert fascist_response.status_code == 200
    fascist_data = fascist_response.json()
    assert fascist_data["team"] == "FASCIST"
    assert fascist_data["is_hitler"] is False
    assert len(fascist_data["teammates"]) == 1
    assert fascist_data["teammates"][0]["player_id"] == str(hitler_id)
    assert fascist_data["teammates"][0]["name"] is not None
    assert fascist_data["teammates"][0]["is_hitler"] is True

    hitler_response = client.get(
        f"/api/games/{room_code}/my-role", params={"player_id": str(hitler_id)}
    )
    assert hitler_response.status_code == 200
    hitler_data = hitler_response.json()
    assert hitler_data["team"] == "FASCIST"
    assert hitler_data["is_hitler"] is True
    assert len(hitler_data["teammates"]) == 1
    assert hitler_data["teammates"][0]["player_id"] == str(fascist_id)
    assert hitler_data["teammates"][0]["name"] is not None
    assert hitler_data["teammates"][0]["is_hitler"] is False


def test_get_my_role_fascists_see_teammates_in_large_games(monkeypatch):
    from src.domain.value_objects.role import Team

    room = GameRoom()
    player_ids = [uuid4() for _ in range(7)]

    for i, player_id in enumerate(player_ids):
        room.add_player(Player(player_id, f"Player{i}"))

    start_game_for_room(room)

    hitler_id = None
    fascist_ids = []
    for player_id, role in room.game_state.role_assignments.items():
        if role.team == Team.FASCIST:
            if role.is_hitler:
                hitler_id = player_id
            else:
                fascist_ids.append(player_id)

    room_repository.save(room)
    room_code = code_repository.generate_code_for_room(room.room_id)

    monkeypatch_deps(monkeypatch)

    fascist_response = client.get(
        f"/api/games/{room_code}/my-role", params={"player_id": str(fascist_ids[0])}
    )
    assert fascist_response.status_code == 200
    fascist_data = fascist_response.json()
    assert fascist_data["team"] == "FASCIST"
    assert fascist_data["is_hitler"] is False
    assert len(fascist_data["teammates"]) == 2
    teammate_ids = [t["player_id"] for t in fascist_data["teammates"]]
    assert str(hitler_id) in teammate_ids
    assert str(fascist_ids[1]) in teammate_ids

    hitler_teammate = next(t for t in fascist_data["teammates"] if t["player_id"] == str(hitler_id))
    assert hitler_teammate["is_hitler"] is True

    other_fascist_teammate = next(t for t in fascist_data["teammates"] if t["player_id"] == str(fascist_ids[1]))
    assert other_fascist_teammate["is_hitler"] is False

    hitler_response = client.get(
        f"/api/games/{room_code}/my-role", params={"player_id": str(hitler_id)}
    )
    assert hitler_response.status_code == 200
    hitler_data = hitler_response.json()
    assert hitler_data["team"] == "FASCIST"
    assert hitler_data["is_hitler"] is True
    assert len(hitler_data["teammates"]) == 0


def test_investigate_loyalty_success(monkeypatch):
    from src.domain.entities.game_state import GamePhase
    from src.domain.value_objects.role import Role, Team

    room = GameRoom()
    player_ids = [uuid4() for _ in range(7)]

    for i, player_id in enumerate(player_ids):
        room.add_player(Player(player_id, f"Player{i}"))

    start_game_for_room(room)
    room.game_state.current_phase = GamePhase.EXECUTIVE_ACTION
    room.game_state.fascist_policies = 2
    room.game_state.role_assignments = {
        player_ids[0]: Role(team=Team.FASCIST, is_hitler=False),
        player_ids[1]: Role(team=Team.LIBERAL, is_hitler=False),
    }
    room.game_state.president_id = player_ids[0]
    room_repository.save(room)
    room_code = code_repository.generate_code_for_room(room.room_id)

    monkeypatch_deps(monkeypatch)

    response = client.get(
        f"/api/games/{room_code}/investigate-loyalty",
        params={"player_id": str(player_ids[0]), "target_player_id": str(player_ids[1])},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["team"] == "LIBERAL"
    assert data["is_hitler"] is False


def test_investigate_loyalty_not_president(monkeypatch):
    from src.domain.entities.game_state import GamePhase
    from src.domain.value_objects.role import Role, Team

    room = GameRoom()
    player_ids = [uuid4() for _ in range(7)]

    for i, player_id in enumerate(player_ids):
        room.add_player(Player(player_id, f"Player{i}"))

    start_game_for_room(room)
    room.game_state.current_phase = GamePhase.EXECUTIVE_ACTION
    room.game_state.fascist_policies = 2
    room.game_state.role_assignments = {
        player_ids[0]: Role(team=Team.FASCIST, is_hitler=False),
        player_ids[1]: Role(team=Team.LIBERAL, is_hitler=False),
    }
    room.game_state.president_id = player_ids[0]
    room_repository.save(room)
    room_code = code_repository.generate_code_for_room(room.room_id)

    monkeypatch_deps(monkeypatch)

    response = client.get(
        f"/api/games/{room_code}/investigate-loyalty",
        params={"player_id": str(player_ids[1]), "target_player_id": str(player_ids[2])},
    )

    assert response.status_code == 400
    assert "president" in response.json()["detail"].lower()


def test_get_game_state_includes_presidential_power(monkeypatch):
    from src.domain.entities.game_state import GamePhase

    room = GameRoom()
    player_ids = [uuid4() for _ in range(7)]

    for i, player_id in enumerate(player_ids):
        room.add_player(Player(player_id, f"Player{i}"))

    start_game_for_room(room)
    room.game_state.current_phase = GamePhase.EXECUTIVE_ACTION
    room.game_state.fascist_policies = 2
    room_repository.save(room)
    room_code = code_repository.generate_code_for_room(room.room_id)

    monkeypatch_deps(monkeypatch)

    response = client.get(f"/api/games/{room_code}/state")

    assert response.status_code == 200
    data = response.json()
    assert data["presidential_power"] == "INVESTIGATE_LOYALTY"
    assert data["current_phase"] == "EXECUTIVE_ACTION"


def test_investigate_loyalty_cannot_investigate_self(monkeypatch):
    from src.domain.entities.game_state import GamePhase
    from src.domain.value_objects.role import Role, Team

    room = GameRoom()
    player_ids = [uuid4() for _ in range(7)]

    for i, player_id in enumerate(player_ids):
        room.add_player(Player(player_id, f"Player{i}"))

    start_game_for_room(room)
    room.game_state.current_phase = GamePhase.EXECUTIVE_ACTION
    room.game_state.fascist_policies = 2
    room.game_state.role_assignments = {
        player_ids[0]: Role(team=Team.FASCIST, is_hitler=False),
    }
    room.game_state.president_id = player_ids[0]
    room_repository.save(room)
    room_code = code_repository.generate_code_for_room(room.room_id)

    monkeypatch_deps(monkeypatch)

    response = client.get(
        f"/api/games/{room_code}/investigate-loyalty",
        params={"player_id": str(player_ids[0]), "target_player_id": str(player_ids[0])},
    )

    assert response.status_code == 400
    assert "yourself" in response.json()["detail"].lower()
