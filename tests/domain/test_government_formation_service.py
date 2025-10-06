from uuid import uuid4

import pytest

from src.domain.entities.game_state import GameState
from src.domain.entities.player import Player
from src.domain.services.government_formation_service import (
    GovernmentFormationService,
)
from src.domain.value_objects.role import Role


def test_can_nominate_chancellor_valid():
    president_id = uuid4()
    chancellor_id = uuid4()

    game_state = GameState(president_id=president_id)
    active_players = [Player(chancellor_id, "Alice"), Player(president_id, "Bob")]

    can_nominate, msg = GovernmentFormationService.can_nominate_chancellor(
        game_state, chancellor_id, active_players
    )

    assert can_nominate
    assert msg == ""


def test_cannot_nominate_self():
    president_id = uuid4()

    game_state = GameState(president_id=president_id)
    active_players = [Player(president_id, "Bob")]

    can_nominate, msg = GovernmentFormationService.can_nominate_chancellor(
        game_state, president_id, active_players
    )

    assert not can_nominate
    assert "cannot nominate themselves" in msg


def test_cannot_nominate_inactive_player():
    president_id = uuid4()
    chancellor_id = uuid4()
    inactive_id = uuid4()

    game_state = GameState(president_id=president_id)
    active_players = [Player(president_id, "Bob"), Player(chancellor_id, "Alice")]

    can_nominate, msg = GovernmentFormationService.can_nominate_chancellor(
        game_state, inactive_id, active_players
    )

    assert not can_nominate
    assert "active player" in msg


def test_cannot_nominate_previous_chancellor_when_more_than_5_alive():
    president_id = uuid4()
    chancellor_id = uuid4()
    previous_chancellor = uuid4()

    game_state = GameState(
        president_id=president_id, previous_chancellor_id=previous_chancellor
    )
    active_players = [
        Player(president_id, "Bob"),
        Player(chancellor_id, "Alice"),
        Player(previous_chancellor, "Charlie"),
        Player(uuid4(), "Dave"),
        Player(uuid4(), "Eve"),
        Player(uuid4(), "Frank"),
    ]

    can_nominate, msg = GovernmentFormationService.can_nominate_chancellor(
        game_state, previous_chancellor, active_players
    )

    assert not can_nominate
    assert "previous chancellor" in msg


def test_can_nominate_previous_chancellor_when_5_or_fewer_alive():
    president_id = uuid4()
    previous_chancellor = uuid4()

    game_state = GameState(
        president_id=president_id, previous_chancellor_id=previous_chancellor
    )
    active_players = [
        Player(president_id, "Bob"),
        Player(previous_chancellor, "Charlie"),
        Player(uuid4(), "Dave"),
        Player(uuid4(), "Eve"),
        Player(uuid4(), "Frank"),
    ]

    can_nominate, msg = GovernmentFormationService.can_nominate_chancellor(
        game_state, previous_chancellor, active_players
    )

    assert can_nominate


def test_can_nominate_hitler_after_3_fascist_policies():
    president_id = uuid4()
    hitler_id = uuid4()

    game_state = GameState(president_id=president_id, fascist_policies=3)
    game_state.role_assignments = {hitler_id: Role.hitler_role()}

    active_players = [Player(president_id, "Bob"), Player(hitler_id, "Hitler")]

    can_nominate, msg = GovernmentFormationService.can_nominate_chancellor(
        game_state, hitler_id, active_players
    )

    assert can_nominate


def test_can_nominate_hitler_before_3_fascist_policies():
    president_id = uuid4()
    hitler_id = uuid4()

    game_state = GameState(president_id=president_id, fascist_policies=2)
    game_state.role_assignments = {hitler_id: Role.hitler_role()}

    active_players = [Player(president_id, "Bob"), Player(hitler_id, "Hitler")]

    can_nominate, msg = GovernmentFormationService.can_nominate_chancellor(
        game_state, hitler_id, active_players
    )

    assert can_nominate


def test_is_government_elected_majority_yes():
    votes = {uuid4(): True, uuid4(): True, uuid4(): False}

    assert GovernmentFormationService.is_government_elected(votes)


def test_is_government_elected_majority_no():
    votes = {uuid4(): False, uuid4(): True, uuid4(): False}

    assert not GovernmentFormationService.is_government_elected(votes)


def test_is_government_elected_tie():
    votes = {uuid4(): True, uuid4(): False}

    assert not GovernmentFormationService.is_government_elected(votes)


def test_is_government_elected_no_votes():
    votes = {}

    assert not GovernmentFormationService.is_government_elected(votes)


def test_advance_president():
    p1_id = uuid4()
    p2_id = uuid4()
    p3_id = uuid4()

    players = [Player(p1_id, "A"), Player(p2_id, "B"), Player(p3_id, "C")]

    next_president = GovernmentFormationService.advance_president(p1_id, players)
    assert next_president == p2_id

    next_president = GovernmentFormationService.advance_president(p3_id, players)
    assert next_president == p1_id


def test_advance_president_when_none():
    p1_id = uuid4()
    players = [Player(p1_id, "A")]

    next_president = GovernmentFormationService.advance_president(None, players)
    assert next_president == p1_id


def test_advance_president_no_players_raises_error():
    with pytest.raises(ValueError, match="No active players"):
        GovernmentFormationService.advance_president(uuid4(), [])
