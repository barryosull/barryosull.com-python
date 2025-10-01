"""Policy deck entity for Secret Hitler game."""

import random
from dataclasses import dataclass, field

from src.domain.value_objects.policy import Policy, PolicyType


@dataclass
class PolicyDeck:
    """Entity representing the policy deck in the game.

    The deck contains liberal and fascist policies. It manages drawing,
    discarding, and reshuffling of policies.

    Attributes:
        draw_pile: List of policies available to draw.
        discard_pile: List of discarded policies.
    """

    draw_pile: list[Policy] = field(default_factory=list)
    discard_pile: list[Policy] = field(default_factory=list)

    @classmethod
    def create_initial_deck(cls) -> "PolicyDeck":
        """Create a new deck with the standard distribution of policies.

        The standard deck contains 6 liberal and 11 fascist policies.

        Returns:
            A new PolicyDeck with shuffled policies.
        """
        policies = (
            [Policy(PolicyType.LIBERAL) for _ in range(6)]
            + [Policy(PolicyType.FASCIST) for _ in range(11)]
        )
        random.shuffle(policies)
        return cls(draw_pile=policies, discard_pile=[])

    def draw(self, count: int) -> list[Policy]:
        """Draw policies from the top of the deck.

        If there are fewer than 3 cards in the draw pile before drawing,
        the discard pile is reshuffled into the draw pile.

        Args:
            count: Number of policies to draw.

        Returns:
            List of drawn policies.

        Raises:
            ValueError: If there aren't enough policies to draw even after reshuffling.
        """
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
        """Add policies to the discard pile.

        Args:
            policies: List of policies to discard.
        """
        self.discard_pile.extend(policies)

    def _reshuffle_if_needed(self) -> None:
        """Reshuffle the discard pile into the draw pile if needed.

        Reshuffling occurs when there are fewer than 3 cards in the draw pile.
        """
        if len(self.draw_pile) < 3 and self.discard_pile:
            self.draw_pile.extend(self.discard_pile)
            self.discard_pile = []
            random.shuffle(self.draw_pile)

    def peek(self, count: int) -> list[Policy]:
        """Peek at the top policies without removing them.

        Used for the Policy Peek presidential power.

        Args:
            count: Number of policies to peek at.

        Returns:
            List of top policies (without removing them from the deck).

        Raises:
            ValueError: If there aren't enough policies to peek at.
        """
        if len(self.draw_pile) < count:
            raise ValueError(
                f"Not enough policies to peek. Requested {count}, "
                f"available {len(self.draw_pile)}"
            )
        return self.draw_pile[:count].copy()

    def cards_remaining(self) -> int:
        """Get the number of cards remaining in the draw pile.

        Returns:
            Number of policies in the draw pile.
        """
        return len(self.draw_pile)

    def total_cards(self) -> int:
        """Get the total number of cards in both piles.

        Returns:
            Total number of policies in draw and discard piles.
        """
        return len(self.draw_pile) + len(self.discard_pile)
