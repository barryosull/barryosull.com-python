"""Policy value object for Secret Hitler game."""

from enum import Enum


class PolicyType(Enum):
    """Enum representing the type of policy."""

    LIBERAL = "LIBERAL"
    FASCIST = "FASCIST"


class Policy:
    """Value object representing a policy card in the game.

    Policies can be either Liberal or Fascist. This is an immutable value object.
    """

    def __init__(self, policy_type: PolicyType) -> None:
        self._type = policy_type

    @property
    def type(self) -> PolicyType:
        return self._type

    def is_liberal(self) -> bool:
        return self._type == PolicyType.LIBERAL

    def is_fascist(self) -> bool:
        return self._type == PolicyType.FASCIST

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Policy):
            return False
        return self._type == other._type

    def __hash__(self) -> int:
        return hash(self._type)

    def __repr__(self) -> str:
        return f"Policy({self._type.value})"
