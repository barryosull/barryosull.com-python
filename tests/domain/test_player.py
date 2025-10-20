
from uuid import uuid4

from backend.domain.entities.player import Player


def test_player_creation():
    player = Player(name="Alice")
    assert player.name == "Alice"
    assert player.is_connected
    assert player.is_alive
    assert player.player_id is not None


def test_player_disconnect():
    player = Player(name="Bob")
    assert player.is_connected

    player.disconnect()
    assert not player.is_connected


def test_player_reconnect():
    player = Player(name="Charlie")
    player.disconnect()
    assert not player.is_connected

    player.reconnect()
    assert player.is_connected


def test_player_kill():
    player = Player(name="David")
    assert player.is_alive

    player.kill()
    assert not player.is_alive


def test_player_can_participate_when_alive_and_connected():
    player = Player(name="Eve")
    assert player.can_participate()


def test_player_cannot_participate_when_dead():
    player = Player(name="Frank")
    player.kill()
    assert not player.can_participate()


def test_player_cannot_participate_when_disconnected():
    player = Player(name="Grace")
    player.disconnect()
    assert not player.can_participate()


def test_player_equality():
    player_id = uuid4()
    player1 = Player(player_id=player_id, name="Alice")
    player2 = Player(player_id=player_id, name="Bob")
    player3 = Player(name="Charlie")

    assert player1 == player2  # Same ID
    assert player1 != player3  # Different ID


def test_player_hash():
    player_id = uuid4()
    player1 = Player(player_id=player_id, name="Alice")
    player2 = Player(player_id=player_id, name="Bob")
    player3 = Player(name="Charlie")

    player_set = {player1, player2, player3}
    assert len(player_set) == 2  # player1 and player2 are the same
