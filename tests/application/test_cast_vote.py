from uuid import uuid4

import pytest

from src.adapters.persistence.in_memory_repository import InMemoryRoomRepository
from src.application.command_bus import CommandBus
from src.application.commands.cast_vote import CastVoteCommand
from src.domain.entities.game_room import GameRoom, RoomStatus
from src.domain.entities.game_state import GamePhase, GameState
from src.domain.entities.player import Player


def test_cast_vote_success():
    repository = InMemoryRoomRepository()
    command_bus = CommandBus(repository)

    president_id = uuid4()
    chancellor_id = uuid4()
    voter_id = uuid4()

    room = GameRoom()
    room.add_player(Player(president_id, "President"))
    room.add_player(Player(chancellor_id, "Chancellor"))
    room.add_player(Player(voter_id, "Voter"))
    room.status = RoomStatus.IN_PROGRESS
    room.game_state = GameState(
        president_id=president_id,
        nominated_chancellor_id=chancellor_id,
        current_phase=GamePhase.ELECTION,
    )

    repository.save(room)

    command = CastVoteCommand(room_id=room.room_id, player_id=voter_id, vote=True)
    command_bus.execute(command)

    updated_room = repository.find_by_id(room.room_id)
    assert voter_id in updated_room.game_state.votes
    assert updated_room.game_state.votes[voter_id] is True


def test_cast_vote_government_elected():
    repository = InMemoryRoomRepository()
    command_bus = CommandBus(repository)

    president_id = uuid4()
    chancellor_id = uuid4()
    voter1_id = uuid4()
    voter2_id = uuid4()

    room = GameRoom()
    room.add_player(Player(president_id, "President"))
    room.add_player(Player(chancellor_id, "Chancellor"))
    room.add_player(Player(voter1_id, "Voter1"))
    room.add_player(Player(voter2_id, "Voter2"))
    room.status = RoomStatus.IN_PROGRESS
    room.game_state = GameState(
        president_id=president_id,
        nominated_chancellor_id=chancellor_id,
        current_phase=GamePhase.ELECTION,
    )
    room.game_state.votes = {
        chancellor_id: True,
        voter1_id: True,
    }

    repository.save(room)

    command = CastVoteCommand(room_id=room.room_id, player_id=voter2_id, vote=True)
    command_bus.execute(command)

    updated_room = repository.find_by_id(room.room_id)
    assert updated_room.game_state.current_phase == GamePhase.LEGISLATIVE_PRESIDENT
    assert updated_room.game_state.chancellor_id == chancellor_id
    assert len(updated_room.game_state.president_policies) == 3


def test_cast_vote_government_rejected():
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
        nominated_chancellor_id=chancellor_id,
        current_phase=GamePhase.ELECTION,
        election_tracker=0,
    )
    room.game_state.votes = {chancellor_id: False}

    repository.save(room)

    command = CastVoteCommand(
        room_id=room.room_id, player_id=next_president_id, vote=False
    )
    command_bus.execute(command)

    updated_room = repository.find_by_id(room.room_id)
    assert updated_room.game_state.current_phase == GamePhase.NOMINATION
    assert updated_room.game_state.election_tracker == 1
    assert updated_room.game_state.nominated_chancellor_id is None
    assert updated_room.game_state.president_id == chancellor_id


def test_cast_vote_already_voted():
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
        nominated_chancellor_id=chancellor_id,
        current_phase=GamePhase.ELECTION,
    )
    room.game_state.votes = {chancellor_id: True}

    repository.save(room)

    command = CastVoteCommand(room_id=room.room_id, player_id=chancellor_id, vote=False)

    with pytest.raises(ValueError, match="already voted"):
        command_bus.execute(command)


def test_cast_vote_wrong_phase():
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

    command = CastVoteCommand(room_id=room.room_id, player_id=president_id, vote=True)

    with pytest.raises(ValueError, match="Cannot vote in phase"):
        command_bus.execute(command)


def test_president_cannot_vote():
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
        nominated_chancellor_id=chancellor_id,
        current_phase=GamePhase.ELECTION,
    )

    repository.save(room)

    command = CastVoteCommand(room_id=room.room_id, player_id=president_id, vote=True)

    with pytest.raises(ValueError, match="President cannot vote"):
        command_bus.execute(command)


def test_failed_election_preserves_previous_chancellor():
    repository = InMemoryRoomRepository()
    command_bus = CommandBus(repository)

    president_id = uuid4()
    last_chancellor_id = uuid4()
    voter1_id = uuid4()
    voter2_id = uuid4()

    room = GameRoom()
    room.add_player(Player(president_id, "President"))
    room.add_player(Player(last_chancellor_id, "LastChancellor"))
    room.add_player(Player(voter1_id, "Voter1"))
    room.add_player(Player(voter2_id, "Voter2"))
    room.status = RoomStatus.IN_PROGRESS
    room.game_state = GameState(
        president_id=president_id,
        nominated_chancellor_id=voter1_id,
        current_phase=GamePhase.ELECTION,
        previous_chancellor_id=last_chancellor_id,
        chancellor_id=None,
    )
    room.game_state.votes = {last_chancellor_id: False, voter1_id: False}

    repository.save(room)

    command = CastVoteCommand(room_id=room.room_id, player_id=voter2_id, vote=False)
    command_bus.execute(command)

    updated_room = repository.find_by_id(room.room_id)
    assert updated_room.game_state.previous_chancellor_id == last_chancellor_id
    assert updated_room.game_state.election_tracker == 1


def test_chaos_resets_previous_government():
    repository = InMemoryRoomRepository()
    command_bus = CommandBus(repository)

    president_id = uuid4()
    last_president_id = uuid4()
    last_chancellor_id = uuid4()
    voter1_id = uuid4()

    room = GameRoom()
    room.add_player(Player(president_id, "President"))
    room.add_player(Player(last_president_id, "LastPresident"))
    room.add_player(Player(last_chancellor_id, "LastChancellor"))
    room.add_player(Player(voter1_id, "Voter1"))
    room.status = RoomStatus.IN_PROGRESS
    room.game_state = GameState(
        president_id=president_id,
        nominated_chancellor_id=voter1_id,
        current_phase=GamePhase.ELECTION,
        previous_president_id=last_president_id,
        previous_chancellor_id=last_chancellor_id,
        election_tracker=2,
    )
    room.game_state.votes = {last_president_id: False, last_chancellor_id: False}

    repository.save(room)

    command = CastVoteCommand(room_id=room.room_id, player_id=voter1_id, vote=False)
    command_bus.execute(command)

    updated_room = repository.find_by_id(room.room_id)
    assert updated_room.game_state.previous_chancellor_id is None
    assert updated_room.game_state.previous_president_id is None
    assert updated_room.game_state.election_tracker == 0
