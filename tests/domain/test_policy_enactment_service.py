import pytest

from backend.domain.entities.game_state import GameState
from backend.domain.services.policy_enactment_service import PolicyEnactmentService
from backend.domain.value_objects.policy import Policy, PolicyType


def test_draw_policies():
    game_state = GameState()

    policies = PolicyEnactmentService.draw_policies(game_state)

    assert len(policies) == 3
    assert all(isinstance(p, Policy) for p in policies)


def test_president_discards_policy():
    policies = [
        Policy(PolicyType.FASCIST),
        Policy(PolicyType.LIBERAL),
        Policy(PolicyType.FASCIST),
    ]
    discarded = policies[0]

    remaining = PolicyEnactmentService.president_discards_policy(policies, discarded)
    
    assert remaining == [Policy(PolicyType.LIBERAL), Policy(PolicyType.FASCIST)]


def test_president_discards_policy_invalid_count():
    policies = [Policy(PolicyType.LIBERAL), Policy(PolicyType.FASCIST)]
    discarded = policies[0]

    with pytest.raises(ValueError, match="exactly 3 policies"):
        PolicyEnactmentService.president_discards_policy(policies, discarded)


def test_president_discards_policy_not_in_hand():
    policies = [
        Policy(PolicyType.LIBERAL),
        Policy(PolicyType.LIBERAL),
        Policy(PolicyType.LIBERAL),
    ]
    other_policy = Policy(PolicyType.FASCIST)

    with pytest.raises(ValueError, match="must be one of the drawn policies"):
        PolicyEnactmentService.president_discards_policy(policies, other_policy)


def test_chancellor_enacts_liberal_policy():
    game_state = GameState()
    policies = [Policy(PolicyType.FASCIST), Policy(PolicyType.LIBERAL)]
    enacted = Policy(PolicyType.LIBERAL)

    result = PolicyEnactmentService.chancellor_enacts_policy(
        game_state, policies, enacted
    )

    assert result == enacted
    assert game_state.liberal_policies == 1
    assert game_state.fascist_policies == 0
    assert game_state.election_tracker == 0


def test_chancellor_enacts_fascist_policy():
    game_state = GameState()
    policies = [Policy(PolicyType.LIBERAL), Policy(PolicyType.FASCIST)]
    enacted = Policy(PolicyType.FASCIST)

    result = PolicyEnactmentService.chancellor_enacts_policy(
        game_state, policies, enacted
    )

    assert result == enacted
    assert game_state.liberal_policies == 0
    assert game_state.fascist_policies == 1
    assert game_state.election_tracker == 0


def test_chancellor_enacts_policy_invalid_count():
    game_state = GameState()
    policies = [Policy(PolicyType.LIBERAL)]
    enacted = policies[0]

    with pytest.raises(ValueError, match="exactly 2 policies"):
        PolicyEnactmentService.chancellor_enacts_policy(game_state, policies, enacted)


def test_chancellor_enacts_policy_not_in_hand():
    game_state = GameState()
    policies = [Policy(PolicyType.FASCIST), Policy(PolicyType.FASCIST)]
    other_policy = Policy(PolicyType.LIBERAL)

    with pytest.raises(ValueError, match="must be one of the available policies"):
        PolicyEnactmentService.chancellor_enacts_policy(
            game_state, policies, other_policy
        )


def test_enact_chaos_policy():
    game_state = GameState()

    enacted = PolicyEnactmentService.enact_chaos_policy(game_state)

    assert isinstance(enacted, Policy)
    total_policies = game_state.liberal_policies + game_state.fascist_policies
    assert total_policies == 1
    assert game_state.election_tracker == 0
