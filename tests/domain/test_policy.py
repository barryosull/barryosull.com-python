"""Tests for Policy value object."""

import pytest

from src.domain.value_objects.policy import Policy, PolicyType


def test_policy_creation_liberal():
    """Test creating a liberal policy."""
    policy = Policy(PolicyType.LIBERAL)
    assert policy.type == PolicyType.LIBERAL
    assert policy.is_liberal()
    assert not policy.is_fascist()


def test_policy_creation_fascist():
    """Test creating a fascist policy."""
    policy = Policy(PolicyType.FASCIST)
    assert policy.type == PolicyType.FASCIST
    assert policy.is_fascist()
    assert not policy.is_liberal()


def test_policy_equality():
    """Test policy equality comparison."""
    liberal1 = Policy(PolicyType.LIBERAL)
    liberal2 = Policy(PolicyType.LIBERAL)
    fascist = Policy(PolicyType.FASCIST)

    assert liberal1 == liberal2
    assert liberal1 != fascist


def test_policy_hash():
    """Test policy can be used in sets and as dict keys."""
    liberal1 = Policy(PolicyType.LIBERAL)
    liberal2 = Policy(PolicyType.LIBERAL)
    fascist = Policy(PolicyType.FASCIST)

    policy_set = {liberal1, liberal2, fascist}
    assert len(policy_set) == 2  # Only 2 unique policies


def test_policy_repr():
    """Test policy string representation."""
    liberal = Policy(PolicyType.LIBERAL)
    fascist = Policy(PolicyType.FASCIST)

    assert repr(liberal) == "Policy(LIBERAL)"
    assert repr(fascist) == "Policy(FASCIST)"
