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
        """Initialize a Policy.

        Args:
            policy_type: The type of policy (LIBERAL or FASCIST).
        """
        self._type = policy_type

    @property
    def type(self) -> PolicyType:
        """Get the policy type.

        Returns:
            The PolicyType of this policy.
        """
        return self._type

    def is_liberal(self) -> bool:
        """Check if this is a liberal policy.

        Returns:
            True if this is a liberal policy, False otherwise.
        """
        return self._type == PolicyType.LIBERAL

    def is_fascist(self) -> bool:
        """Check if this is a fascist policy.

        Returns:
            True if this is a fascist policy, False otherwise.
        """
        return self._type == PolicyType.FASCIST

    def __eq__(self, other: object) -> bool:
        """Check equality with another Policy.

        Args:
            other: The object to compare with.

        Returns:
            True if both policies have the same type, False otherwise.
        """
        if not isinstance(other, Policy):
            return False
        return self._type == other._type

    def __hash__(self) -> int:
        """Generate hash for the policy.

        Returns:
            Hash value based on policy type.
        """
        return hash(self._type)

    def __repr__(self) -> str:
        """String representation of the policy.

        Returns:
            String representation showing the policy type.
        """
        return f"Policy({self._type.value})"
