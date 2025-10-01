"""Role value object for Secret Hitler game."""

from enum import Enum


class Team(Enum):
    """Enum representing the team a player belongs to."""

    LIBERAL = "LIBERAL"
    FASCIST = "FASCIST"


class Role:
    """Value object representing a player's role in the game.

    A role consists of a team (Liberal or Fascist) and whether the player is Hitler.
    This is an immutable value object.
    """

    def __init__(self, team: Team, is_hitler: bool = False) -> None:
        """Initialize a Role.

        Args:
            team: The team this role belongs to (LIBERAL or FASCIST).
            is_hitler: Whether this role is Hitler (default: False).

        Raises:
            ValueError: If is_hitler is True but team is not FASCIST.
        """
        if is_hitler and team != Team.FASCIST:
            raise ValueError("Hitler must be on the Fascist team")
        self._team = team
        self._is_hitler = is_hitler

    @property
    def team(self) -> Team:
        """Get the team this role belongs to.

        Returns:
            The Team of this role.
        """
        return self._team

    @property
    def is_hitler(self) -> bool:
        """Check if this role is Hitler.

        Returns:
            True if this is Hitler, False otherwise.
        """
        return self._is_hitler

    def is_liberal(self) -> bool:
        """Check if this role is on the Liberal team.

        Returns:
            True if this is a Liberal role, False otherwise.
        """
        return self._team == Team.LIBERAL

    def is_fascist(self) -> bool:
        """Check if this role is on the Fascist team.

        Returns:
            True if this is a Fascist role (including Hitler), False otherwise.
        """
        return self._team == Team.FASCIST

    @classmethod
    def liberal(cls) -> "Role":
        """Create a Liberal role.

        Returns:
            A new Liberal Role instance.
        """
        return cls(Team.LIBERAL, is_hitler=False)

    @classmethod
    def fascist(cls) -> "Role":
        """Create a Fascist role (not Hitler).

        Returns:
            A new Fascist Role instance.
        """
        return cls(Team.FASCIST, is_hitler=False)

    @classmethod
    def hitler_role(cls) -> "Role":
        """Create the Hitler role.

        Returns:
            A new Hitler Role instance.
        """
        return cls(Team.FASCIST, is_hitler=True)

    def __eq__(self, other: object) -> bool:
        """Check equality with another Role.

        Args:
            other: The object to compare with.

        Returns:
            True if both roles have the same team and hitler status, False otherwise.
        """
        if not isinstance(other, Role):
            return False
        return self._team == other._team and self._is_hitler == other._is_hitler

    def __hash__(self) -> int:
        """Generate hash for the role.

        Returns:
            Hash value based on team and hitler status.
        """
        return hash((self._team, self._is_hitler))

    def __repr__(self) -> str:
        """String representation of the role.

        Returns:
            String representation showing the team and whether it's Hitler.
        """
        if self._is_hitler:
            return "Role(HITLER)"
        return f"Role({self._team.value})"
