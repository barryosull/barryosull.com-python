"""Role value object for Secret Hitler game."""

from enum import Enum


class Team(Enum):
    LIBERAL = "LIBERAL"
    FASCIST = "FASCIST"


class Role:

    def __init__(self, team: Team, is_hitler: bool = False) -> None:
        if is_hitler and team != Team.FASCIST:
            raise ValueError("Hitler must be on the Fascist team")
        self._team = team
        self._is_hitler = is_hitler

    @property
    def team(self) -> Team:
        return self._team

    @property
    def is_hitler(self) -> bool:
        return self._is_hitler

    def is_liberal(self) -> bool:
        return self._team == Team.LIBERAL

    def is_fascist(self) -> bool:
        return self._team == Team.FASCIST

    @classmethod
    def liberal(cls) -> "Role":
        return cls(Team.LIBERAL, is_hitler=False)

    @classmethod
    def fascist(cls) -> "Role":
        return cls(Team.FASCIST, is_hitler=False)

    @classmethod
    def hitler_role(cls) -> "Role":
        return cls(Team.FASCIST, is_hitler=True)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Role):
            return False
        return self._team == other._team and self._is_hitler == other._is_hitler

    def __hash__(self) -> int:
        return hash((self._team, self._is_hitler))

    def __repr__(self) -> str:
        if self._is_hitler:
            return "Role(HITLER)"
        return f"Role({self._team.value})"
