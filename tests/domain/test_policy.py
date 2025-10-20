
import pytest

from src.domain.value_objects.policy import Policy, PolicyType


def test_policy_creation_liberal():
    policy = Policy(PolicyType.LIBERAL)
    assert policy.type == PolicyType.LIBERAL
    assert policy.is_liberal()
    assert not policy.is_fascist()


def test_policy_creation_fascist():
    policy = Policy(PolicyType.FASCIST)
    assert policy.type == PolicyType.FASCIST
    assert policy.is_fascist()
    assert not policy.is_liberal()


def test_policy_equality():
    liberal1 = Policy(PolicyType.LIBERAL)
    liberal2 = Policy(PolicyType.LIBERAL)
    fascist = Policy(PolicyType.FASCIST)

    assert liberal1 == liberal2
    assert liberal1 != fascist


def test_policy_hash():
    liberal1 = Policy(PolicyType.LIBERAL)
    liberal2 = Policy(PolicyType.LIBERAL)
    fascist = Policy(PolicyType.FASCIST)

    policy_set = {liberal1, liberal2, fascist}
    assert len(policy_set) == 2


def test_policy_repr():
    liberal = Policy(PolicyType.LIBERAL)
    fascist = Policy(PolicyType.FASCIST)

    assert repr(liberal) == "Policy(LIBERAL)"
    assert repr(fascist) == "Policy(FASCIST)"
