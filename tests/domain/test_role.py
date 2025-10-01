"""Tests for Role value object."""

import pytest

from src.domain.value_objects.role import Role, Team


def test_role_liberal_creation():
    """Test creating a liberal role."""
    role = Role.liberal()
    assert role.team == Team.LIBERAL
    assert role.is_liberal()
    assert not role.is_fascist()
    assert not role.is_hitler


def test_role_fascist_creation():
    """Test creating a fascist role."""
    role = Role.fascist()
    assert role.team == Team.FASCIST
    assert role.is_fascist()
    assert not role.is_liberal()
    assert not role.is_hitler


def test_role_hitler_creation():
    """Test creating the Hitler role."""
    role = Role.hitler_role()
    assert role.team == Team.FASCIST
    assert role.is_fascist()
    assert not role.is_liberal()
    assert role.is_hitler


def test_role_hitler_must_be_fascist():
    """Test that Hitler must be on the fascist team."""
    with pytest.raises(ValueError, match="Hitler must be on the Fascist team"):
        Role(Team.LIBERAL, is_hitler=True)


def test_role_equality():
    """Test role equality comparison."""
    liberal1 = Role.liberal()
    liberal2 = Role.liberal()
    fascist = Role.fascist()
    hitler = Role.hitler_role()

    assert liberal1 == liberal2
    assert liberal1 != fascist
    assert fascist != hitler


def test_role_hash():
    """Test role can be used in sets and as dict keys."""
    liberal1 = Role.liberal()
    liberal2 = Role.liberal()
    fascist = Role.fascist()
    hitler = Role.hitler_role()

    role_set = {liberal1, liberal2, fascist, hitler}
    assert len(role_set) == 3  # Only 3 unique roles


def test_role_repr():
    """Test role string representation."""
    liberal = Role.liberal()
    fascist = Role.fascist()
    hitler = Role.hitler_role()

    assert repr(liberal) == "Role(LIBERAL)"
    assert repr(fascist) == "Role(FASCIST)"
    assert repr(hitler) == "Role(HITLER)"
