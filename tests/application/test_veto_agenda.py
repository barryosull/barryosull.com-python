from uuid import uuid4

import pytest

from src.adapters.persistence.in_memory_repository import InMemoryRoomRepository
from src.application.commands.veto_agenda import VetoAgendaCommand, VetoAgendaHandler
from src.domain.entities.game_room import GameRoom, RoomStatus
from src.domain.entities.game_state import GamePhase, GameState
from src.domain.entities.player import Player
from src.domain.value_objects.policy import Policy, PolicyType


def test_chancellor_initiates_veto():
    repository = InMemoryRoomRepository()
    handler = VetoAgendaHandler(repository)

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

    command = VetoAgendaCommand(
        room_id=room.room_id, player_id=chancellor_id, approve_veto=True
    )
    handler.handle(command)

    updated_room = repository.find_by_id(room.room_id)
    assert updated_room.game_state.current_phase == GamePhase.NOMINATION
    assert updated_room.game_state.election_tracker == 1
    assert updated_room.game_state.chancellor_policies == []
    assert updated_room.game_state.president_policies == []
    assert updated_room.game_state.president_id == chancellor_id


def test_president_approves_veto():
    repository = InMemoryRoomRepository()
    handler = VetoAgendaHandler(repository)

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

    command = VetoAgendaCommand(
        room_id=room.room_id, player_id=president_id, approve_veto=True
    )
    handler.handle(command)

    updated_room = repository.find_by_id(room.room_id)
    assert updated_room.game_state.current_phase == GamePhase.NOMINATION
    assert updated_room.game_state.election_tracker == 1
    assert updated_room.game_state.chancellor_policies == []
    assert updated_room.game_state.president_policies == []
    assert updated_room.game_state.president_id == chancellor_id


def test_president_rejects_veto():
    repository = InMemoryRoomRepository()
    handler = VetoAgendaHandler(repository)

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
        room_id=room.room_id, player_id=president_id, approve_veto=False
    )

    with pytest.raises(ValueError, match="President rejected veto"):
        handler.handle(command)


def test_chancellor_cannot_reject_veto():
    repository = InMemoryRoomRepository()
    handler = VetoAgendaHandler(repository)

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

    with pytest.raises(ValueError, match="Chancellor initiated veto, cannot reject"):
        handler.handle(command)


def test_veto_not_available_before_5_policies():
    repository = InMemoryRoomRepository()
    handler = VetoAgendaHandler(repository)

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
        handler.handle(command)


def test_veto_wrong_phase():
    repository = InMemoryRoomRepository()
    handler = VetoAgendaHandler(repository)

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
        handler.handle(command)


def test_non_government_member_cannot_veto():
    repository = InMemoryRoomRepository()
    handler = VetoAgendaHandler(repository)

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
        handler.handle(command)


def test_room_not_found():
    repository = InMemoryRoomRepository()
    handler = VetoAgendaHandler(repository)

    command = VetoAgendaCommand(
        room_id=uuid4(), player_id=uuid4(), approve_veto=True
    )

    with pytest.raises(ValueError, match="not found"):
        handler.handle(command)


def test_game_not_started():
    repository = InMemoryRoomRepository()
    handler = VetoAgendaHandler(repository)

    president_id = uuid4()

    room = GameRoom()
    room.add_player(Player(president_id, "President"))

    repository.save(room)

    command = VetoAgendaCommand(
        room_id=room.room_id, player_id=president_id, approve_veto=True
    )

    with pytest.raises(ValueError, match="Game not started"):
        handler.handle(command)
