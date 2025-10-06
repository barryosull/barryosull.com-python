from uuid import uuid4

import pytest

from src.adapters.persistence.in_memory_repository import InMemoryRoomRepository
from src.application.commands.use_executive_action import (
    UseExecutiveActionCommand,
    UseExecutiveActionHandler,
)
from src.domain.entities.game_room import GameRoom, RoomStatus
from src.domain.entities.game_state import GamePhase, GameState
from src.domain.entities.player import Player
from src.domain.value_objects.role import Role, Team


def test_investigate_loyalty():
    repository = InMemoryRoomRepository()
    handler = UseExecutiveActionHandler(repository)

    president_id = uuid4()
    target_id = uuid4()
    player3_id = uuid4()
    player4_id = uuid4()
    player5_id = uuid4()
    player6_id = uuid4()
    player7_id = uuid4()

    room = GameRoom()
    room.add_player(Player(president_id, "President"))
    room.add_player(Player(target_id, "Target"))
    room.add_player(Player(player3_id, "Player3"))
    room.add_player(Player(player4_id, "Player4"))
    room.add_player(Player(player5_id, "Player5"))
    room.add_player(Player(player6_id, "Player6"))
    room.add_player(Player(player7_id, "Player7"))
    room.status = RoomStatus.IN_PROGRESS

    room.game_state = GameState(
        president_id=president_id,
        current_phase=GamePhase.EXECUTIVE_ACTION,
        fascist_policies=1,
    )
    room.game_state.role_assignments = {
        president_id: Role(team=Team.FASCIST, is_hitler=False),
        target_id: Role(team=Team.LIBERAL, is_hitler=False),
    }

    repository.save(room)

    command = UseExecutiveActionCommand(
        room_id=room.room_id, player_id=president_id, target_player_id=target_id
    )
    result = handler.handle(command)

    assert result["party_membership"] == Team.LIBERAL
    updated_room = repository.find_by_id(room.room_id)
    assert updated_room.game_state.current_phase == GamePhase.NOMINATION


def test_policy_peek():
    repository = InMemoryRoomRepository()
    handler = UseExecutiveActionHandler(repository)

    president_id = uuid4()
    player2_id = uuid4()
    player3_id = uuid4()
    player4_id = uuid4()
    player5_id = uuid4()

    room = GameRoom()
    room.add_player(Player(president_id, "President"))
    room.add_player(Player(player2_id, "Player2"))
    room.add_player(Player(player3_id, "Player3"))
    room.add_player(Player(player4_id, "Player4"))
    room.add_player(Player(player5_id, "Player5"))
    room.status = RoomStatus.IN_PROGRESS

    room.game_state = GameState(
        president_id=president_id,
        current_phase=GamePhase.EXECUTIVE_ACTION,
        fascist_policies=3,
    )

    repository.save(room)

    command = UseExecutiveActionCommand(room_id=room.room_id, player_id=president_id)
    result = handler.handle(command)

    assert "policies" in result
    assert len(result["policies"]) == 3
    assert all("type" in p for p in result["policies"])


def test_execution_regular_player():
    repository = InMemoryRoomRepository()
    handler = UseExecutiveActionHandler(repository)

    president_id = uuid4()
    target_id = uuid4()
    player3_id = uuid4()
    player4_id = uuid4()
    player5_id = uuid4()
    player6_id = uuid4()

    room = GameRoom()
    room.add_player(Player(president_id, "President"))
    room.add_player(Player(target_id, "Target"))
    room.add_player(Player(player3_id, "Player3"))
    room.add_player(Player(player4_id, "Player4"))
    room.add_player(Player(player5_id, "Player5"))
    room.add_player(Player(player6_id, "Player6"))
    room.status = RoomStatus.IN_PROGRESS

    room.game_state = GameState(
        president_id=president_id,
        current_phase=GamePhase.EXECUTIVE_ACTION,
        fascist_policies=4,
    )
    room.game_state.role_assignments = {
        target_id: Role(team=Team.LIBERAL, is_hitler=False)
    }

    repository.save(room)

    command = UseExecutiveActionCommand(
        room_id=room.room_id, player_id=president_id, target_player_id=target_id
    )
    result = handler.handle(command)

    assert result["executed_player_id"] == str(target_id)
    assert "game_over" not in result
    updated_room = repository.find_by_id(room.room_id)
    assert not updated_room.get_player(target_id).is_alive
    assert updated_room.game_state.current_phase == GamePhase.NOMINATION


def test_execution_hitler_ends_game():
    repository = InMemoryRoomRepository()
    handler = UseExecutiveActionHandler(repository)

    president_id = uuid4()
    hitler_id = uuid4()
    player3_id = uuid4()
    player4_id = uuid4()
    player5_id = uuid4()
    player6_id = uuid4()

    room = GameRoom()
    room.add_player(Player(president_id, "President"))
    room.add_player(Player(hitler_id, "Hitler"))
    room.add_player(Player(player3_id, "Player3"))
    room.add_player(Player(player4_id, "Player4"))
    room.add_player(Player(player5_id, "Player5"))
    room.add_player(Player(player6_id, "Player6"))
    room.status = RoomStatus.IN_PROGRESS

    room.game_state = GameState(
        president_id=president_id,
        current_phase=GamePhase.EXECUTIVE_ACTION,
        fascist_policies=4,
    )
    room.game_state.role_assignments = {hitler_id: Role.hitler_role()}

    repository.save(room)

    command = UseExecutiveActionCommand(
        room_id=room.room_id, player_id=president_id, target_player_id=hitler_id
    )
    result = handler.handle(command)

    assert result["executed_player_id"] == str(hitler_id)
    assert result["game_over"] is True
    assert result["winning_team"] == "LIBERAL"
    updated_room = repository.find_by_id(room.room_id)
    assert updated_room.game_state.current_phase == GamePhase.GAME_OVER
    assert updated_room.status == RoomStatus.COMPLETED


def test_call_special_election():
    repository = InMemoryRoomRepository()
    handler = UseExecutiveActionHandler(repository)

    president_id = uuid4()
    special_president_id = uuid4()
    player3_id = uuid4()
    player4_id = uuid4()
    player5_id = uuid4()
    player6_id = uuid4()
    player7_id = uuid4()

    room = GameRoom()
    room.add_player(Player(president_id, "President"))
    room.add_player(Player(special_president_id, "SpecialPres"))
    room.add_player(Player(player3_id, "Player3"))
    room.add_player(Player(player4_id, "Player4"))
    room.add_player(Player(player5_id, "Player5"))
    room.add_player(Player(player6_id, "Player6"))
    room.add_player(Player(player7_id, "Player7"))
    room.status = RoomStatus.IN_PROGRESS

    room.game_state = GameState(
        president_id=president_id,
        current_phase=GamePhase.EXECUTIVE_ACTION,
        fascist_policies=3,
    )

    repository.save(room)

    command = UseExecutiveActionCommand(
        room_id=room.room_id,
        player_id=president_id,
        target_player_id=special_president_id,
    )
    result = handler.handle(command)

    updated_room = repository.find_by_id(room.room_id)
    assert updated_room.game_state.president_id == special_president_id
    assert updated_room.game_state.current_phase == GamePhase.NOMINATION
    assert updated_room.game_state.chancellor_id is None
    assert updated_room.game_state.nominated_chancellor_id is None


def test_not_president_cannot_use_power():
    repository = InMemoryRoomRepository()
    handler = UseExecutiveActionHandler(repository)

    president_id = uuid4()
    non_president_id = uuid4()

    room = GameRoom()
    room.add_player(Player(president_id, "President"))
    room.add_player(Player(non_president_id, "NonPres"))
    room.status = RoomStatus.IN_PROGRESS

    room.game_state = GameState(
        president_id=president_id,
        current_phase=GamePhase.EXECUTIVE_ACTION,
        fascist_policies=1,
    )

    repository.save(room)

    command = UseExecutiveActionCommand(
        room_id=room.room_id, player_id=non_president_id
    )

    with pytest.raises(ValueError, match="Only the president can use executive actions"):
        handler.handle(command)


def test_wrong_phase():
    repository = InMemoryRoomRepository()
    handler = UseExecutiveActionHandler(repository)

    president_id = uuid4()

    room = GameRoom()
    room.add_player(Player(president_id, "President"))
    room.status = RoomStatus.IN_PROGRESS

    room.game_state = GameState(
        president_id=president_id, current_phase=GamePhase.NOMINATION
    )

    repository.save(room)

    command = UseExecutiveActionCommand(room_id=room.room_id, player_id=president_id)

    with pytest.raises(ValueError, match="Cannot use executive action in phase"):
        handler.handle(command)


def test_execution_requires_target():
    repository = InMemoryRoomRepository()
    handler = UseExecutiveActionHandler(repository)

    president_id = uuid4()
    player2_id = uuid4()
    player3_id = uuid4()
    player4_id = uuid4()
    player5_id = uuid4()
    player6_id = uuid4()

    room = GameRoom()
    room.add_player(Player(president_id, "President"))
    room.add_player(Player(player2_id, "Player2"))
    room.add_player(Player(player3_id, "Player3"))
    room.add_player(Player(player4_id, "Player4"))
    room.add_player(Player(player5_id, "Player5"))
    room.add_player(Player(player6_id, "Player6"))
    room.status = RoomStatus.IN_PROGRESS

    room.game_state = GameState(
        president_id=president_id,
        current_phase=GamePhase.EXECUTIVE_ACTION,
        fascist_policies=4,
    )

    repository.save(room)

    command = UseExecutiveActionCommand(room_id=room.room_id, player_id=president_id)

    with pytest.raises(ValueError, match="Target player required for execution"):
        handler.handle(command)


def test_execution_dead_player():
    repository = InMemoryRoomRepository()
    handler = UseExecutiveActionHandler(repository)

    president_id = uuid4()
    dead_player_id = uuid4()
    player3_id = uuid4()
    player4_id = uuid4()
    player5_id = uuid4()
    player6_id = uuid4()

    room = GameRoom()
    room.add_player(Player(president_id, "President"))
    dead_player = Player(dead_player_id, "DeadPlayer")
    dead_player.kill()
    room.add_player(dead_player)
    room.add_player(Player(player3_id, "Player3"))
    room.add_player(Player(player4_id, "Player4"))
    room.add_player(Player(player5_id, "Player5"))
    room.add_player(Player(player6_id, "Player6"))
    room.status = RoomStatus.IN_PROGRESS

    room.game_state = GameState(
        president_id=president_id,
        current_phase=GamePhase.EXECUTIVE_ACTION,
        fascist_policies=4,
    )

    repository.save(room)

    command = UseExecutiveActionCommand(
        room_id=room.room_id, player_id=president_id, target_player_id=dead_player_id
    )

    with pytest.raises(ValueError, match="Target player is already dead"):
        handler.handle(command)
