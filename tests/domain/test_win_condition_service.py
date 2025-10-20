from uuid import uuid4

from backend.domain.entities.game_state import GameState
from backend.domain.services.win_condition_service import WinConditionService
from backend.domain.value_objects.role import Role, Team


def test_check_liberal_victory_5_policies():
    game_state = GameState(liberal_policies=5)

    is_won, msg = WinConditionService.check_liberal_victory(game_state)

    assert is_won
    assert "5 liberal policies" in msg


def test_check_liberal_victory_not_won():
    game_state = GameState(liberal_policies=4)

    is_won, msg = WinConditionService.check_liberal_victory(game_state)

    assert not is_won
    assert msg == ""


def test_check_fascist_victory_6_policies():
    game_state = GameState(fascist_policies=6)

    is_won, msg = WinConditionService.check_fascist_victory(game_state)

    assert is_won
    assert "6 fascist policies" in msg


def test_check_fascist_victory_not_won():
    game_state = GameState(fascist_policies=5)

    is_won, msg = WinConditionService.check_fascist_victory(game_state)

    assert not is_won
    assert msg == ""


def test_check_hitler_elected_after_3_fascist_policies():
    hitler_id = uuid4()
    game_state = GameState(fascist_policies=3)
    game_state.role_assignments = {hitler_id: Role.hitler_role()}

    is_won, msg = WinConditionService.check_hitler_elected(game_state, hitler_id)

    assert is_won
    assert "Hitler elected" in msg


def test_check_hitler_elected_before_3_fascist_policies():
    hitler_id = uuid4()
    game_state = GameState(fascist_policies=2)
    game_state.role_assignments = {hitler_id: Role.hitler_role()}

    is_won, msg = WinConditionService.check_hitler_elected(game_state, hitler_id)

    assert not is_won


def test_check_hitler_elected_non_hitler():
    player_id = uuid4()
    game_state = GameState(fascist_policies=3)
    game_state.role_assignments = {player_id: Role.liberal()}

    is_won, msg = WinConditionService.check_hitler_elected(game_state, player_id)

    assert not is_won


def test_check_hitler_killed():
    hitler_id = uuid4()
    game_state = GameState()
    game_state.role_assignments = {hitler_id: Role.hitler_role()}

    is_killed = WinConditionService.check_hitler_killed(game_state, hitler_id)

    assert is_killed


def test_check_hitler_killed_non_hitler():
    player_id = uuid4()
    game_state = GameState()
    game_state.role_assignments = {player_id: Role.liberal()}

    is_killed = WinConditionService.check_hitler_killed(game_state, player_id)

    assert not is_killed


def test_check_game_over_liberal_win():
    game_state = GameState(liberal_policies=5)

    is_over, team, msg = WinConditionService.check_game_over(game_state)

    assert is_over
    assert team == Team.LIBERAL
    assert "5 liberal policies" in msg


def test_check_game_over_fascist_win():
    game_state = GameState(fascist_policies=6)

    is_over, team, msg = WinConditionService.check_game_over(game_state)

    assert is_over
    assert team == Team.FASCIST
    assert "6 fascist policies" in msg


def test_check_game_over_not_over():
    game_state = GameState(liberal_policies=3, fascist_policies=2)

    is_over, team, msg = WinConditionService.check_game_over(game_state)

    assert not is_over
    assert team is None
    assert msg == ""
