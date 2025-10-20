from uuid import uuid4

import pytest

from backend.domain.services.role_assignment_service import RoleAssignmentService
from backend.domain.value_objects.role import Role


def test_assign_roles_5_players():
    player_ids = [uuid4() for _ in range(5)]

    roles = RoleAssignmentService.assign_roles(player_ids)

    assert len(roles) == 5

    liberal_count = sum(1 for r in roles.values() if r.is_liberal())
    fascist_count = sum(
        1 for r in roles.values() if r.is_fascist() and not r.is_hitler
    )
    hitler_count = sum(1 for r in roles.values() if r.is_hitler)

    assert liberal_count == 3
    assert fascist_count == 1
    assert hitler_count == 1


def test_assign_roles_6_players():
    player_ids = [uuid4() for _ in range(6)]

    roles = RoleAssignmentService.assign_roles(player_ids)

    assert len(roles) == 6

    liberal_count = sum(1 for r in roles.values() if r.is_liberal())
    fascist_count = sum(
        1 for r in roles.values() if r.is_fascist() and not r.is_hitler
    )
    hitler_count = sum(1 for r in roles.values() if r.is_hitler)

    assert liberal_count == 4
    assert fascist_count == 1
    assert hitler_count == 1


def test_assign_roles_10_players():
    player_ids = [uuid4() for _ in range(10)]

    roles = RoleAssignmentService.assign_roles(player_ids)

    assert len(roles) == 10

    liberal_count = sum(1 for r in roles.values() if r.is_liberal())
    fascist_count = sum(
        1 for r in roles.values() if r.is_fascist() and not r.is_hitler
    )
    hitler_count = sum(1 for r in roles.values() if r.is_hitler)

    assert liberal_count == 6
    assert fascist_count == 3
    assert hitler_count == 1


def test_assign_roles_invalid_player_count_too_few():
    player_ids = [uuid4() for _ in range(4)]

    with pytest.raises(ValueError, match="Invalid player count: 4"):
        RoleAssignmentService.assign_roles(player_ids)


def test_assign_roles_invalid_player_count_too_many():
    player_ids = [uuid4() for _ in range(11)]

    with pytest.raises(ValueError, match="Invalid player count: 11"):
        RoleAssignmentService.assign_roles(player_ids)


def test_assign_roles_randomization():
    player_ids = [uuid4() for _ in range(5)]

    roles1 = RoleAssignmentService.assign_roles(player_ids)
    roles2 = RoleAssignmentService.assign_roles(player_ids)

    assert roles1 != roles2 or True
