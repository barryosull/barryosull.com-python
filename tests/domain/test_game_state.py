from uuid import uuid4

from backend.domain.entities.game_state import GamePhase, GameState


def test_move_to_nomination_phase():
    old_president_id = uuid4()
    new_president_id = uuid4()
    chancellor_id = uuid4()
    nominated_chancellor_id = uuid4()

    game_state = GameState(
        president_id=old_president_id,
        chancellor_id=chancellor_id,
        nominated_chancellor_id=nominated_chancellor_id,
        current_phase=GamePhase.ELECTION,
        votes={uuid4(): True, uuid4(): False},
    )

    game_state.move_to_nomination_phase(new_president_id)

    assert game_state.current_phase == GamePhase.NOMINATION
    assert game_state.president_id == new_president_id
    assert game_state.nominated_chancellor_id is None
    assert game_state.chancellor_id is None
    assert game_state.votes == {}
