"""Policy deck entity for Secret Hitler game."""

import random
from dataclasses import dataclass, field

from backend.domain.value_objects.policy import Policy, PolicyType


@dataclass
class PolicyDeck:
    draw_pile: list[Policy] = field(default_factory=list)
    discard_pile: list[Policy] = field(default_factory=list)

    @classmethod
    def create_initial_deck(cls) -> "PolicyDeck":
        policies = (
            [Policy(PolicyType.LIBERAL) for _ in range(6)]
            + [Policy(PolicyType.FASCIST) for _ in range(11)]
        )
        random.shuffle(policies)
        return cls(draw_pile=policies, discard_pile=[])

    def draw(self, count: int) -> list[Policy]:
        self._reshuffle_if_needed()

        if len(self.draw_pile) < count:
            raise ValueError(
                f"Not enough policies to draw. Requested {count}, "
                f"available {len(self.draw_pile)}"
            )

        drawn = self.draw_pile[:count]
        self.draw_pile = self.draw_pile[count:]
        return drawn

    def discard(self, policies: list[Policy]) -> None:
        self.discard_pile.extend(policies)

    def _reshuffle_if_needed(self) -> None:
        if len(self.draw_pile) < 3 and self.discard_pile:
            self.draw_pile.extend(self.discard_pile)
            self.discard_pile = []
            random.shuffle(self.draw_pile)

    def peek(self, count: int) -> list[Policy]:
        if len(self.draw_pile) < count:
            raise ValueError(
                f"Not enough policies to peek. Requested {count}, "
                f"available {len(self.draw_pile)}"
            )
        return self.draw_pile[:count].copy()

    def cards_remaining(self) -> int:
        return len(self.draw_pile)

    def total_cards(self) -> int:
        return len(self.draw_pile) + len(self.discard_pile)
