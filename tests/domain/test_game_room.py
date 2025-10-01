"""Tests for GameRoom entity."""

import pytest

from src.domain.entities.game_room import GameRoom, RoomStatus
from src.domain.entities.game_state import GameState
from src.domain.entities.player import Player


def test_game_room_creation():
    """Test creating a new game room."""
    room = GameRoom()
    assert room.room_id is not None
    assert room.status == RoomStatus.WAITING
    assert len(room.players) == 0
    assert room.game_state is None
    assert room.creator_id is None


def test_add_first_player_sets_creator():
    """Test that adding first player sets them as creator."""
    room = GameRoom()
    player = Player(name="Alice")

    room.add_player(player)

    assert room.creator_id == player.player_id
    assert len(room.players) == 1


def test_add_multiple_players():
    """Test adding multiple players to a room."""
    room = GameRoom()
    alice = Player(name="Alice")
    bob = Player(name="Bob")

    room.add_player(alice)
    room.add_player(bob)

    assert len(room.players) == 2
    assert room.creator_id == alice.player_id


def test_cannot_add_duplicate_player():
    """Test that adding the same player twice raises error."""
    room = GameRoom()
    player = Player(name="Alice")

    room.add_player(player)

    with pytest.raises(ValueError, match="Player already in room"):
        room.add_player(player)


def test_cannot_add_player_after_game_starts():
    """Test that players cannot be added after game starts."""
    room = GameRoom()
    for i in range(5):
        room.add_player(Player(name=f"Player{i}"))

    game_state = GameState()
    room.start_game(game_state)

    with pytest.raises(ValueError, match="Cannot add players to a game in progress"):
        room.add_player(Player(name="Late"))


def test_remove_player():
    """Test removing a player from the room."""
    room = GameRoom()
    alice = Player(name="Alice")
    bob = Player(name="Bob")

    room.add_player(alice)
    room.add_player(bob)

    room.remove_player(bob.player_id)

    assert len(room.players) == 1
    assert room.get_player(bob.player_id) is None


def test_remove_creator_transfers_ownership():
    """Test that removing creator transfers ownership to next player."""
    room = GameRoom()
    alice = Player(name="Alice")
    bob = Player(name="Bob")

    room.add_player(alice)
    room.add_player(bob)

    assert room.creator_id == alice.player_id

    room.remove_player(alice.player_id)

    assert room.creator_id == bob.player_id


def test_cannot_remove_player_after_game_starts():
    """Test that players cannot be removed after game starts."""
    room = GameRoom()
    players = [Player(name=f"Player{i}") for i in range(5)]
    for player in players:
        room.add_player(player)

    game_state = GameState()
    room.start_game(game_state)

    with pytest.raises(
        ValueError, match="Cannot remove players from a game in progress"
    ):
        room.remove_player(players[0].player_id)


def test_get_player():
    """Test retrieving a player by ID."""
    room = GameRoom()
    alice = Player(name="Alice")
    bob = Player(name="Bob")

    room.add_player(alice)
    room.add_player(bob)

    assert room.get_player(alice.player_id) == alice
    assert room.get_player(bob.player_id) == bob


def test_player_count():
    """Test getting the player count."""
    room = GameRoom()

    assert room.player_count() == 0

    for i in range(5):
        room.add_player(Player(name=f"Player{i}"))

    assert room.player_count() == 5


def test_can_start_game_with_enough_players():
    """Test that game can start with 5 or more players."""
    room = GameRoom()

    assert not room.can_start_game()

    for i in range(4):
        room.add_player(Player(name=f"Player{i}"))

    assert not room.can_start_game()

    room.add_player(Player(name="Player4"))

    assert room.can_start_game()


def test_start_game():
    """Test starting a game."""
    room = GameRoom()
    for i in range(5):
        room.add_player(Player(name=f"Player{i}"))

    game_state = GameState()
    room.start_game(game_state)

    assert room.status == RoomStatus.IN_PROGRESS
    assert room.game_state == game_state


def test_cannot_start_game_with_too_few_players():
    """Test that game cannot start with fewer than 5 players."""
    room = GameRoom()
    for i in range(4):
        room.add_player(Player(name=f"Player{i}"))

    game_state = GameState()

    with pytest.raises(ValueError, match="Cannot start game"):
        room.start_game(game_state)


def test_end_game():
    """Test ending a game."""
    room = GameRoom()
    for i in range(5):
        room.add_player(Player(name=f"Player{i}"))

    game_state = GameState()
    room.start_game(game_state)

    room.end_game()

    assert room.status == RoomStatus.COMPLETED


def test_is_creator():
    """Test checking if a player is the creator."""
    room = GameRoom()
    alice = Player(name="Alice")
    bob = Player(name="Bob")

    room.add_player(alice)
    room.add_player(bob)

    assert room.is_creator(alice.player_id)
    assert not room.is_creator(bob.player_id)


def test_active_players():
    """Test getting list of active players."""
    room = GameRoom()
    alice = Player(name="Alice")
    bob = Player(name="Bob")
    charlie = Player(name="Charlie")

    room.add_player(alice)
    room.add_player(bob)
    room.add_player(charlie)

    bob.disconnect()
    charlie.kill()

    active = room.active_players()

    assert len(active) == 1
    assert active[0] == alice


def test_room_equality():
    """Test room equality based on room_id."""
    room1 = GameRoom()
    room2 = GameRoom()

    assert room1 != room2  # Different IDs

    room3 = room1
    assert room1 == room3  # Same instance


def test_room_hash():
    """Test room can be used in sets and as dict keys."""
    room1 = GameRoom()
    room2 = GameRoom()

    room_set = {room1, room2}
    assert len(room_set) == 2
