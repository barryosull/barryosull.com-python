from uuid import uuid4

import pytest

from src.adapters.persistence.in_memory_repository import InMemoryRoomRepository
from src.application.command_bus import CommandBus
from src.application.commands.discard_policy import DiscardPolicyCommand
from src.domain.entities.game_room import GameRoom, RoomStatus
from src.domain.entities.game_state import GamePhase, GameState
from src.domain.entities.player import Player
from src.domain.value_objects.policy import Policy, PolicyType


def test_discard_policy_success():
    repository = InMemoryRoomRepository()
    command_bus = CommandBus(repository)

    president_id = uuid4()
    chancellor_id = uuid4()

    policies = [
        Policy(PolicyType.LIBERAL),
        Policy(PolicyType.FASCIST),
        Policy(PolicyType.LIBERAL),
    ]

    room = GameRoom()
    room.add_player(Player(president_id, "President"))
    room.add_player(Player(chancellor_id, "Chancellor"))
    room.status = RoomStatus.IN_PROGRESS
    room.game_state = GameState(
        president_id=president_id,
        chancellor_id=chancellor_id,
        current_phase=GamePhase.LEGISLATIVE_PRESIDENT,
    )
    room.game_state.president_policies = policies

    repository.save(room)

    command = DiscardPolicyCommand(
        room_id=room.room_id, player_id=president_id, policy_type="FASCIST"
    )
    command_bus.execute(command)

    updated_room = repository.find_by_id(room.room_id)
    assert updated_room.game_state.current_phase == GamePhase.LEGISLATIVE_CHANCELLOR
    assert len(updated_room.game_state.chancellor_policies) == 2
    assert policies[1] not in updated_room.game_state.chancellor_policies
    assert len(updated_room.game_state.president_policies) == 0


def test_discard_policy_wrong_phase():
    repository = InMemoryRoomRepository()
    command_bus = CommandBus(repository)

    president_id = uuid4()

    room = GameRoom()
    room.add_player(Player(president_id, "President"))
    room.status = RoomStatus.IN_PROGRESS
    room.game_state = GameState(
        president_id=president_id, current_phase=GamePhase.NOMINATION
    )

    repository.save(room)

    command = DiscardPolicyCommand(
        room_id=room.room_id, player_id=president_id, policy_type="LIBERAL"
    )

    with pytest.raises(ValueError, match="Cannot discard policy in phase"):
        command_bus.execute(command)


def test_discard_policy_not_president():
    repository = InMemoryRoomRepository()
    command_bus = CommandBus(repository)

    president_id = uuid4()
    other_player_id = uuid4()
    policy = Policy(PolicyType.LIBERAL)

    room = GameRoom()
    room.add_player(Player(president_id, "President"))
    room.add_player(Player(other_player_id, "Other"))
    room.status = RoomStatus.IN_PROGRESS
    room.game_state = GameState(
        president_id=president_id, current_phase=GamePhase.LEGISLATIVE_PRESIDENT
    )
    room.game_state.president_policies = [policy]

    repository.save(room)

    command = DiscardPolicyCommand(
        room_id=room.room_id, player_id=other_player_id, policy_type="LIBERAL"
    )

    with pytest.raises(ValueError, match="Only the president"):
        command_bus.execute(command)


def test_discard_policy_not_found():
    repository = InMemoryRoomRepository()
    command_bus = CommandBus(repository)

    president_id = uuid4()
    policies = [
        Policy(PolicyType.LIBERAL),
        Policy(PolicyType.LIBERAL),
        Policy(PolicyType.LIBERAL),
    ]

    room = GameRoom()
    room.add_player(Player(president_id, "President"))
    room.status = RoomStatus.IN_PROGRESS
    room.game_state = GameState(
        president_id=president_id, current_phase=GamePhase.LEGISLATIVE_PRESIDENT
    )
    room.game_state.president_policies = policies

    repository.save(room)

    command = DiscardPolicyCommand(
        room_id=room.room_id, player_id=president_id, policy_type="FASCIST"
    )

    with pytest.raises(ValueError, match="Policy FASCIST not found in president policies"):
        command_bus.execute(command)
