from uuid import uuid4

from src.adapters.persistence.in_memory_repository import InMemoryRoomRepository
from src.application.command_bus import CommandBus
from src.application.commands.cast_vote import CastVoteCommand
from src.domain.entities.game_room import GameRoom, RoomStatus
from src.domain.entities.game_state import GamePhase, GameState
from src.domain.entities.player import Player
from src.domain.value_objects.role import Role


def test_hitler_elected_after_3_fascist_policies_ends_game():
    repository = InMemoryRoomRepository()
    command_bus = CommandBus(repository)

    president_id = uuid4()
    hitler_id = uuid4()
    voter1_id = uuid4()

    room = GameRoom()
    room.add_player(Player(president_id, "President"))
    room.add_player(Player(hitler_id, "Hitler"))
    room.add_player(Player(voter1_id, "Voter1"))
    room.status = RoomStatus.IN_PROGRESS

    room.game_state = GameState(
        president_id=president_id,
        nominated_chancellor_id=hitler_id,
        current_phase=GamePhase.ELECTION,
        fascist_policies=3,
    )
    room.game_state.role_assignments = {hitler_id: Role.hitler_role()}
    room.game_state.votes = {hitler_id: True}

    repository.save(room)

    command = CastVoteCommand(room_id=room.room_id, player_id=voter1_id, vote=True)
    command_bus.execute(command)

    updated_room = repository.find_by_id(room.room_id)
    assert updated_room.game_state.current_phase == GamePhase.GAME_OVER
    assert updated_room.status == RoomStatus.COMPLETED


def test_hitler_elected_before_3_fascist_policies_continues_game():
    repository = InMemoryRoomRepository()
    command_bus = CommandBus(repository)

    president_id = uuid4()
    hitler_id = uuid4()
    voter1_id = uuid4()

    room = GameRoom()
    room.add_player(Player(president_id, "President"))
    room.add_player(Player(hitler_id, "Hitler"))
    room.add_player(Player(voter1_id, "Voter1"))
    room.status = RoomStatus.IN_PROGRESS

    room.game_state = GameState(
        president_id=president_id,
        nominated_chancellor_id=hitler_id,
        current_phase=GamePhase.ELECTION,
        fascist_policies=2,
    )
    room.game_state.role_assignments = {hitler_id: Role.hitler_role()}
    room.game_state.votes = {hitler_id: True}

    repository.save(room)

    command = CastVoteCommand(room_id=room.room_id, player_id=voter1_id, vote=True)
    command_bus.execute(command)

    updated_room = repository.find_by_id(room.room_id)
    assert updated_room.game_state.current_phase == GamePhase.LEGISLATIVE_PRESIDENT
    assert updated_room.game_state.chancellor_id == hitler_id
    assert len(updated_room.game_state.president_policies) == 3


def test_hitler_elected_exactly_3_fascist_policies_ends_game():
    repository = InMemoryRoomRepository()
    command_bus = CommandBus(repository)

    president_id = uuid4()
    hitler_id = uuid4()
    voter1_id = uuid4()

    room = GameRoom()
    room.add_player(Player(president_id, "President"))
    room.add_player(Player(hitler_id, "Hitler"))
    room.add_player(Player(voter1_id, "Voter1"))
    room.status = RoomStatus.IN_PROGRESS

    room.game_state = GameState(
        president_id=president_id,
        nominated_chancellor_id=hitler_id,
        current_phase=GamePhase.ELECTION,
        fascist_policies=3,
    )
    room.game_state.role_assignments = {hitler_id: Role.hitler_role()}
    room.game_state.votes = {hitler_id: True}

    repository.save(room)

    command = CastVoteCommand(room_id=room.room_id, player_id=voter1_id, vote=True)
    command_bus.execute(command)

    updated_room = repository.find_by_id(room.room_id)
    assert updated_room.game_state.current_phase == GamePhase.GAME_OVER
    assert updated_room.status == RoomStatus.COMPLETED
