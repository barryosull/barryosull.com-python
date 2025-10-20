from uuid import uuid4

import pytest

from src.adapters.persistence.in_memory_room_repository import InMemoryRoomRepository
from src.application.command_bus import CommandBus
from src.application.commands.reorder_players import ReorderPlayersCommand
from src.domain.entities.game_room import GameRoom, RoomStatus
from src.domain.entities.player import Player


def test_reorder_players_success():
    repository = InMemoryRoomRepository()
    command_bus = CommandBus(repository)

    room = GameRoom()
    creator_id = uuid4()
    player2_id = uuid4()
    player3_id = uuid4()

    room.add_player(Player(creator_id, "Creator"))
    room.add_player(Player(player2_id, "Player2"))
    room.add_player(Player(player3_id, "Player3"))

    repository.save(room)

    assert room.players[0].player_id == creator_id
    assert room.players[1].player_id == player2_id
    assert room.players[2].player_id == player3_id

    new_order = [player3_id, creator_id, player2_id]
    command = ReorderPlayersCommand(
        room_id=room.room_id,
        requester_id=creator_id,
        player_ids=new_order,
    )
    command_bus.execute(command)

    updated_room = repository.find_by_id(room.room_id)
    assert updated_room.players[0].player_id == player3_id
    assert updated_room.players[1].player_id == creator_id
    assert updated_room.players[2].player_id == player2_id


def test_reorder_players_room_not_found():
    repository = InMemoryRoomRepository()
    command_bus = CommandBus(repository)

    command = ReorderPlayersCommand(
        room_id=uuid4(),
        requester_id=uuid4(),
        player_ids=[uuid4(), uuid4()],
    )

    with pytest.raises(ValueError, match="not found"):
        command_bus.execute(command)


def test_reorder_players_not_creator():
    repository = InMemoryRoomRepository()
    command_bus = CommandBus(repository)

    room = GameRoom()
    creator_id = uuid4()
    other_player_id = uuid4()

    room.add_player(Player(creator_id, "Creator"))
    room.add_player(Player(other_player_id, "Other"))

    repository.save(room)

    command = ReorderPlayersCommand(
        room_id=room.room_id,
        requester_id=other_player_id,
        player_ids=[other_player_id, creator_id],
    )

    with pytest.raises(ValueError, match="Only the room creator"):
        command_bus.execute(command)


def test_reorder_players_wrong_number_of_players():
    repository = InMemoryRoomRepository()
    command_bus = CommandBus(repository)

    room = GameRoom()
    creator_id = uuid4()
    player2_id = uuid4()
    player3_id = uuid4()

    room.add_player(Player(creator_id, "Creator"))
    room.add_player(Player(player2_id, "Player2"))
    room.add_player(Player(player3_id, "Player3"))

    repository.save(room)

    command = ReorderPlayersCommand(
        room_id=room.room_id,
        requester_id=creator_id,
        player_ids=[creator_id, player2_id],
    )

    with pytest.raises(ValueError, match="must match current player count"):
        command_bus.execute(command)


def test_reorder_players_invalid_player_ids():
    repository = InMemoryRoomRepository()
    command_bus = CommandBus(repository)

    room = GameRoom()
    creator_id = uuid4()
    player2_id = uuid4()
    player3_id = uuid4()
    invalid_id = uuid4()

    room.add_player(Player(creator_id, "Creator"))
    room.add_player(Player(player2_id, "Player2"))
    room.add_player(Player(player3_id, "Player3"))

    repository.save(room)

    command = ReorderPlayersCommand(
        room_id=room.room_id,
        requester_id=creator_id,
        player_ids=[creator_id, player2_id, invalid_id],
    )

    with pytest.raises(ValueError, match="must match existing players"):
        command_bus.execute(command)


def test_reorder_players_duplicate_player_ids():
    repository = InMemoryRoomRepository()
    command_bus = CommandBus(repository)

    room = GameRoom()
    creator_id = uuid4()
    player2_id = uuid4()
    player3_id = uuid4()

    room.add_player(Player(creator_id, "Creator"))
    room.add_player(Player(player2_id, "Player2"))
    room.add_player(Player(player3_id, "Player3"))

    repository.save(room)

    command = ReorderPlayersCommand(
        room_id=room.room_id,
        requester_id=creator_id,
        player_ids=[creator_id, creator_id, player2_id],
    )

    with pytest.raises(ValueError, match="must match existing players"):
        command_bus.execute(command)


def test_reorder_players_game_in_progress():
    repository = InMemoryRoomRepository()
    command_bus = CommandBus(repository)

    room = GameRoom()
    creator_id = uuid4()
    player2_id = uuid4()
    player3_id = uuid4()

    room.add_player(Player(creator_id, "Creator"))
    room.add_player(Player(player2_id, "Player2"))
    room.add_player(Player(player3_id, "Player3"))

    room.status = RoomStatus.IN_PROGRESS

    repository.save(room)

    command = ReorderPlayersCommand(
        room_id=room.room_id,
        requester_id=creator_id,
        player_ids=[player3_id, creator_id, player2_id],
    )

    with pytest.raises(ValueError, match="Cannot reorder players in a game in progress"):
        command_bus.execute(command)
