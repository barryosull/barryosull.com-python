from uuid import uuid4

import pytest

from backend.adapters.persistence.in_memory_repository import InMemoryRoomRepository
from backend.application.command_bus import CommandBus
from backend.application.commands.veto_agenda import VetoAgendaCommand
from backend.domain.entities.game_room import GameRoom, RoomStatus
from backend.domain.entities.game_state import GamePhase, GameState
from backend.domain.entities.player import Player
from backend.domain.value_objects.policy import Policy, PolicyType


def test_chancellor_initiates_veto():
    repository = InMemoryRoomRepository()
    command_bus = CommandBus(repository)

    president_id = uuid4()
    chancellor_id = uuid4()
    next_president_id = uuid4()

    room = GameRoom()
    room.add_player(Player(president_id, "President"))
    room.add_player(Player(chancellor_id, "Chancellor"))
    room.add_player(Player(next_president_id, "NextPres"))
    room.status = RoomStatus.IN_PROGRESS

    room.game_state = GameState(
        president_id=president_id,
        chancellor_id=chancellor_id,
        current_phase=GamePhase.LEGISLATIVE_CHANCELLOR,
        fascist_policies=5,
        election_tracker=0,
    )
    room.game_state.chancellor_policies = [
        Policy(PolicyType.FASCIST),
        Policy(PolicyType.FASCIST),
    ]

    repository.save(room)

    chancellor_command = VetoAgendaCommand(
        room_id=room.room_id, player_id=chancellor_id, approve_veto=True
    )
    command_bus.execute(chancellor_command)

    updated_room = repository.find_by_id(room.room_id)
    assert updated_room.game_state.veto_requested is True
    assert updated_room.game_state.current_phase == GamePhase.LEGISLATIVE_CHANCELLOR
    assert updated_room.game_state.election_tracker == 0

    president_command = VetoAgendaCommand(
        room_id=room.room_id, player_id=president_id, approve_veto=True
    )
    command_bus.execute(president_command)

    final_room = repository.find_by_id(room.room_id)
    assert final_room.game_state.veto_requested is False
    assert final_room.game_state.current_phase == GamePhase.NOMINATION
    assert final_room.game_state.election_tracker == 1
    assert final_room.game_state.chancellor_policies == []
    assert final_room.game_state.president_policies == []
    assert final_room.game_state.president_id == chancellor_id


def test_president_approves_veto():
    repository = InMemoryRoomRepository()
    command_bus = CommandBus(repository)

    president_id = uuid4()
    chancellor_id = uuid4()
    next_president_id = uuid4()

    room = GameRoom()
    room.add_player(Player(president_id, "President"))
    room.add_player(Player(chancellor_id, "Chancellor"))
    room.add_player(Player(next_president_id, "NextPres"))
    room.status = RoomStatus.IN_PROGRESS

    room.game_state = GameState(
        president_id=president_id,
        chancellor_id=chancellor_id,
        current_phase=GamePhase.LEGISLATIVE_CHANCELLOR,
        fascist_policies=5,
        election_tracker=0,
    )
    room.game_state.chancellor_policies = [
        Policy(PolicyType.FASCIST),
        Policy(PolicyType.FASCIST),
    ]

    repository.save(room)

    chancellor_command = VetoAgendaCommand(
        room_id=room.room_id, player_id=chancellor_id, approve_veto=True
    )
    command_bus.execute(chancellor_command)

    president_command = VetoAgendaCommand(
        room_id=room.room_id, player_id=president_id, approve_veto=True
    )
    command_bus.execute(president_command)

    updated_room = repository.find_by_id(room.room_id)
    assert updated_room.game_state.veto_requested is False
    assert updated_room.game_state.current_phase == GamePhase.NOMINATION
    assert updated_room.game_state.election_tracker == 1
    assert updated_room.game_state.chancellor_policies == []
    assert updated_room.game_state.president_policies == []
    assert updated_room.game_state.president_id == chancellor_id


def test_president_rejects_veto():
    repository = InMemoryRoomRepository()
    command_bus = CommandBus(repository)

    president_id = uuid4()
    chancellor_id = uuid4()

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
    room.game_state.chancellor_policies = [
        Policy(PolicyType.FASCIST),
        Policy(PolicyType.FASCIST),
    ]

    repository.save(room)

    chancellor_command = VetoAgendaCommand(
        room_id=room.room_id, player_id=chancellor_id, approve_veto=True
    )
    command_bus.execute(chancellor_command)

    updated_room = repository.find_by_id(room.room_id)
    assert updated_room.game_state.veto_requested is True

    president_command = VetoAgendaCommand(
        room_id=room.room_id, player_id=president_id, approve_veto=False
    )
    command_bus.execute(president_command)

    final_room = repository.find_by_id(room.room_id)
    assert final_room.game_state.veto_requested is False
    assert final_room.game_state.current_phase == GamePhase.LEGISLATIVE_CHANCELLOR
    assert len(final_room.game_state.chancellor_policies) == 2


def test_chancellor_cannot_reject_veto():
    repository = InMemoryRoomRepository()
    command_bus = CommandBus(repository)

    president_id = uuid4()
    chancellor_id = uuid4()

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

    repository.save(room)

    command = VetoAgendaCommand(
        room_id=room.room_id, player_id=chancellor_id, approve_veto=False
    )

    with pytest.raises(ValueError, match="Chancellor cannot reject their own veto request"):
        command_bus.execute(command)


def test_veto_not_available_before_5_policies():
    repository = InMemoryRoomRepository()
    command_bus = CommandBus(repository)

    president_id = uuid4()
    chancellor_id = uuid4()

    room = GameRoom()
    room.add_player(Player(president_id, "President"))
    room.add_player(Player(chancellor_id, "Chancellor"))
    room.status = RoomStatus.IN_PROGRESS

    room.game_state = GameState(
        president_id=president_id,
        chancellor_id=chancellor_id,
        current_phase=GamePhase.LEGISLATIVE_CHANCELLOR,
        fascist_policies=4,
    )

    repository.save(room)

    command = VetoAgendaCommand(
        room_id=room.room_id, player_id=chancellor_id, approve_veto=True
    )

    with pytest.raises(
        ValueError, match="Veto power is not available until 5 fascist policies"
    ):
        command_bus.execute(command)


def test_veto_wrong_phase():
    repository = InMemoryRoomRepository()
    command_bus = CommandBus(repository)

    president_id = uuid4()
    chancellor_id = uuid4()

    room = GameRoom()
    room.add_player(Player(president_id, "President"))
    room.add_player(Player(chancellor_id, "Chancellor"))
    room.status = RoomStatus.IN_PROGRESS

    room.game_state = GameState(
        president_id=president_id,
        chancellor_id=chancellor_id,
        current_phase=GamePhase.NOMINATION,
        fascist_policies=5,
    )

    repository.save(room)

    command = VetoAgendaCommand(
        room_id=room.room_id, player_id=chancellor_id, approve_veto=True
    )

    with pytest.raises(ValueError, match="Cannot veto in phase"):
        command_bus.execute(command)


def test_non_government_member_cannot_veto():
    repository = InMemoryRoomRepository()
    command_bus = CommandBus(repository)

    president_id = uuid4()
    chancellor_id = uuid4()
    other_player_id = uuid4()

    room = GameRoom()
    room.add_player(Player(president_id, "President"))
    room.add_player(Player(chancellor_id, "Chancellor"))
    room.add_player(Player(other_player_id, "Other"))
    room.status = RoomStatus.IN_PROGRESS

    room.game_state = GameState(
        president_id=president_id,
        chancellor_id=chancellor_id,
        current_phase=GamePhase.LEGISLATIVE_CHANCELLOR,
        fascist_policies=5,
    )

    repository.save(room)

    command = VetoAgendaCommand(
        room_id=room.room_id, player_id=other_player_id, approve_veto=True
    )

    with pytest.raises(
        ValueError, match="Only the president or chancellor can respond to veto"
    ):
        command_bus.execute(command)


def test_room_not_found():
    repository = InMemoryRoomRepository()
    command_bus = CommandBus(repository)

    command = VetoAgendaCommand(
        room_id=uuid4(), player_id=uuid4(), approve_veto=True
    )

    with pytest.raises(ValueError, match="not found"):
        command_bus.execute(command)


def test_game_not_started():
    repository = InMemoryRoomRepository()
    command_bus = CommandBus(repository)

    president_id = uuid4()

    room = GameRoom()
    room.add_player(Player(president_id, "President"))

    repository.save(room)

    command = VetoAgendaCommand(
        room_id=room.room_id, player_id=president_id, approve_veto=True
    )

    with pytest.raises(ValueError, match="Game not started"):
        command_bus.execute(command)


def test_president_cannot_respond_without_veto_request():
    repository = InMemoryRoomRepository()
    command_bus = CommandBus(repository)

    president_id = uuid4()
    chancellor_id = uuid4()

    room = GameRoom()
    room.add_player(Player(president_id, "President"))
    room.add_player(Player(chancellor_id, "Chancellor"))
    room.status = RoomStatus.IN_PROGRESS

    room.game_state = GameState(
        president_id=president_id,
        chancellor_id=chancellor_id,
        current_phase=GamePhase.LEGISLATIVE_CHANCELLOR,
        fascist_policies=5,
        veto_requested=False,
    )

    repository.save(room)

    command = VetoAgendaCommand(
        room_id=room.room_id, player_id=president_id, approve_veto=True
    )

    with pytest.raises(ValueError, match="No veto request to respond to"):
        command_bus.execute(command)
