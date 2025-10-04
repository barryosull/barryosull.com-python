from uuid import uuid4

import pytest

from src.adapters.persistence.in_memory_repository import InMemoryRoomRepository
from src.application.commands.enact_policy import EnactPolicyCommand, EnactPolicyHandler
from src.domain.entities.game_room import GameRoom, RoomStatus
from src.domain.entities.game_state import GamePhase, GameState
from src.domain.entities.player import Player
from src.domain.value_objects.policy import Policy, PolicyType


def test_enact_policy_success():
    repository = InMemoryRoomRepository()
    handler = EnactPolicyHandler(repository)

    president_id = uuid4()
    chancellor_id = uuid4()

    policies = [Policy(PolicyType.LIBERAL), Policy(PolicyType.FASCIST)]

    room = GameRoom()
    room.add_player(Player(president_id, "President"))
    room.add_player(Player(chancellor_id, "Chancellor"))
    room.status = RoomStatus.IN_PROGRESS
    room.game_state = GameState(
        president_id=president_id,
        chancellor_id=chancellor_id,
        current_phase=GamePhase.LEGISLATIVE_CHANCELLOR,
    )
    room.game_state.chancellor_policies = policies

    repository.save(room)

    command = EnactPolicyCommand(
        room_id=room.room_id, player_id=chancellor_id, enacted_policy=policies[0]
    )
    handler.handle(command)

    updated_room = repository.find_by_id(room.room_id)
    assert updated_room.game_state.liberal_policies == 1
    assert updated_room.game_state.current_phase == GamePhase.NOMINATION
    assert len(updated_room.game_state.chancellor_policies) == 0


def test_enact_policy_triggers_executive_action():
    repository = InMemoryRoomRepository()
    handler = EnactPolicyHandler(repository)

    president_id = uuid4()
    chancellor_id = uuid4()

    policies = [Policy(PolicyType.FASCIST), Policy(PolicyType.LIBERAL)]

    room = GameRoom()
    for i in range(7):
        player_id = president_id if i == 0 else (chancellor_id if i == 1 else uuid4())
        room.add_player(Player(player_id, f"Player{i}"))

    room.status = RoomStatus.IN_PROGRESS
    room.game_state = GameState(
        president_id=president_id,
        chancellor_id=chancellor_id,
        current_phase=GamePhase.LEGISLATIVE_CHANCELLOR,
        fascist_policies=0,
    )
    room.game_state.chancellor_policies = policies

    repository.save(room)

    command = EnactPolicyCommand(
        room_id=room.room_id, player_id=chancellor_id, enacted_policy=policies[0]
    )
    handler.handle(command)

    updated_room = repository.find_by_id(room.room_id)
    assert updated_room.game_state.fascist_policies == 1
    assert updated_room.game_state.current_phase == GamePhase.EXECUTIVE_ACTION


def test_enact_policy_liberal_victory():
    repository = InMemoryRoomRepository()
    handler = EnactPolicyHandler(repository)

    president_id = uuid4()
    chancellor_id = uuid4()

    policies = [Policy(PolicyType.LIBERAL), Policy(PolicyType.FASCIST)]

    room = GameRoom()
    room.add_player(Player(president_id, "President"))
    room.add_player(Player(chancellor_id, "Chancellor"))
    room.status = RoomStatus.IN_PROGRESS
    room.game_state = GameState(
        president_id=president_id,
        chancellor_id=chancellor_id,
        current_phase=GamePhase.LEGISLATIVE_CHANCELLOR,
        liberal_policies=4,
    )
    room.game_state.chancellor_policies = policies

    repository.save(room)

    command = EnactPolicyCommand(
        room_id=room.room_id, player_id=chancellor_id, enacted_policy=policies[0]
    )
    handler.handle(command)

    updated_room = repository.find_by_id(room.room_id)
    assert updated_room.game_state.liberal_policies == 5
    assert updated_room.game_state.current_phase == GamePhase.GAME_OVER
    assert updated_room.status == RoomStatus.COMPLETED


def test_enact_policy_fascist_victory():
    repository = InMemoryRoomRepository()
    handler = EnactPolicyHandler(repository)

    president_id = uuid4()
    chancellor_id = uuid4()

    policies = [Policy(PolicyType.FASCIST), Policy(PolicyType.LIBERAL)]

    room = GameRoom()
    room.add_player(Player(president_id, "President"))
    room.add_player(Player(chancellor_id, "Chancellor"))
    room.status = RoomStatus.IN_PROGRESS
    room.game_state = GameState(
        president_id=president_id,
        chancellor_id=chancellor_id,
        current_phase=GamePhase.LEGISLATIVE_CHANCELLOR,
        fascist_policies=5,
    )
    room.game_state.chancellor_policies = policies

    repository.save(room)

    command = EnactPolicyCommand(
        room_id=room.room_id, player_id=chancellor_id, enacted_policy=policies[0]
    )
    handler.handle(command)

    updated_room = repository.find_by_id(room.room_id)
    assert updated_room.game_state.fascist_policies == 6
    assert updated_room.game_state.current_phase == GamePhase.GAME_OVER
    assert updated_room.status == RoomStatus.COMPLETED


def test_enact_policy_wrong_phase():
    repository = InMemoryRoomRepository()
    handler = EnactPolicyHandler(repository)

    chancellor_id = uuid4()
    policy = Policy(PolicyType.LIBERAL)

    room = GameRoom()
    room.add_player(Player(chancellor_id, "Chancellor"))
    room.status = RoomStatus.IN_PROGRESS
    room.game_state = GameState(
        chancellor_id=chancellor_id, current_phase=GamePhase.NOMINATION
    )

    repository.save(room)

    command = EnactPolicyCommand(
        room_id=room.room_id, player_id=chancellor_id, enacted_policy=policy
    )

    with pytest.raises(ValueError, match="Cannot enact policy in phase"):
        handler.handle(command)


def test_enact_policy_not_chancellor():
    repository = InMemoryRoomRepository()
    handler = EnactPolicyHandler(repository)

    chancellor_id = uuid4()
    other_player_id = uuid4()
    policy = Policy(PolicyType.LIBERAL)

    room = GameRoom()
    room.add_player(Player(chancellor_id, "Chancellor"))
    room.add_player(Player(other_player_id, "Other"))
    room.status = RoomStatus.IN_PROGRESS
    room.game_state = GameState(
        chancellor_id=chancellor_id, current_phase=GamePhase.LEGISLATIVE_CHANCELLOR
    )
    room.game_state.chancellor_policies = [policy]

    repository.save(room)

    command = EnactPolicyCommand(
        room_id=room.room_id, player_id=other_player_id, enacted_policy=policy
    )

    with pytest.raises(ValueError, match="Only the chancellor"):
        handler.handle(command)
