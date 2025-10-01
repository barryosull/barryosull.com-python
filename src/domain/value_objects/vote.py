"""Vote value object for Secret Hitler game."""

from enum import Enum


class VoteChoice(Enum):
    """Enum representing a player's vote choice."""

    JA = "JA"  # Yes in German
    NEIN = "NEIN"  # No in German


class Vote:
    """Value object representing a player's vote on a proposed government.

    This is an immutable value object.
    """

    def __init__(self, choice: VoteChoice) -> None:
        """Initialize a Vote.

        Args:
            choice: The vote choice (JA or NEIN).
        """
        self._choice = choice

    @property
    def choice(self) -> VoteChoice:
        """Get the vote choice.

        Returns:
            The VoteChoice of this vote.
        """
        return self._choice

    def is_ja(self) -> bool:
        """Check if this is a 'Ja' (yes) vote.

        Returns:
            True if this is a yes vote, False otherwise.
        """
        return self._choice == VoteChoice.JA

    def is_nein(self) -> bool:
        """Check if this is a 'Nein' (no) vote.

        Returns:
            True if this is a no vote, False otherwise.
        """
        return self._choice == VoteChoice.NEIN

    @classmethod
    def ja(cls) -> "Vote":
        """Create a 'Ja' (yes) vote.

        Returns:
            A new Vote instance representing a yes vote.
        """
        return cls(VoteChoice.JA)

    @classmethod
    def nein(cls) -> "Vote":
        """Create a 'Nein' (no) vote.

        Returns:
            A new Vote instance representing a no vote.
        """
        return cls(VoteChoice.NEIN)

    def __eq__(self, other: object) -> bool:
        """Check equality with another Vote.

        Args:
            other: The object to compare with.

        Returns:
            True if both votes have the same choice, False otherwise.
        """
        if not isinstance(other, Vote):
            return False
        return self._choice == other._choice

    def __hash__(self) -> int:
        """Generate hash for the vote.

        Returns:
            Hash value based on vote choice.
        """
        return hash(self._choice)

    def __repr__(self) -> str:
        """String representation of the vote.

        Returns:
            String representation showing the vote choice.
        """
        return f"Vote({self._choice.value})"
