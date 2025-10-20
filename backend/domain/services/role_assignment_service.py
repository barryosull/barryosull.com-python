import random
from uuid import UUID

from backend.domain.value_objects.role import Role


class RoleAssignmentService:
    @staticmethod
    def assign_roles(player_ids: list[UUID]) -> dict[UUID, Role]:
        player_count = len(player_ids)

        if player_count < 5 or player_count > 10:
            raise ValueError(f"Invalid player count: {player_count}. Must be 5-10.")

        role_distribution = {
            5: (3, 1),
            6: (4, 1),
            7: (4, 2),
            8: (5, 2),
            9: (5, 3),
            10: (6, 3),
        }

        liberal_count, fascist_count = role_distribution[player_count]

        roles = (
            [Role.hitler_role()]
            + [Role.fascist() for _ in range(fascist_count)]
            + [Role.liberal() for _ in range(liberal_count)]
        )

        return dict(zip(player_ids, roles))
