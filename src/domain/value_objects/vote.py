"""Vote value object for Secret Hitler game."""

from enum import Enum


class VoteChoice(Enum):
    JA = "JA"
    NEIN = "NEIN"


class Vote:

    def __init__(self, choice: VoteChoice) -> None:
        self._choice = choice

    @property
    def choice(self) -> VoteChoice:
        return self._choice

    def is_ja(self) -> bool:
        return self._choice == VoteChoice.JA

    def is_nein(self) -> bool:
        return self._choice == VoteChoice.NEIN

    @classmethod
    def ja(cls) -> "Vote":
        return cls(VoteChoice.JA)

    @classmethod
    def nein(cls) -> "Vote":
        return cls(VoteChoice.NEIN)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Vote):
            return False
        return self._choice == other._choice

    def __hash__(self) -> int:
        return hash(self._choice)

    def __repr__(self) -> str:
        return f"Vote({self._choice.value})"
