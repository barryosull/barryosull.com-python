"""Tests for PolicyDeck entity."""

import pytest

from src.domain.entities.policy_deck import PolicyDeck
from src.domain.value_objects.policy import Policy, PolicyType


def test_create_initial_deck():
    """Test creating a deck with standard distribution."""
    deck = PolicyDeck.create_initial_deck()

    assert deck.total_cards() == 17
    assert deck.cards_remaining() == 17
    assert len(deck.discard_pile) == 0

    # Count policy types
    liberal_count = sum(1 for p in deck.draw_pile if p.is_liberal())
    fascist_count = sum(1 for p in deck.draw_pile if p.is_fascist())

    assert liberal_count == 6
    assert fascist_count == 11


def test_draw_policies():
    """Test drawing policies from the deck."""
    deck = PolicyDeck.create_initial_deck()
    initial_count = deck.cards_remaining()

    policies = deck.draw(3)

    assert len(policies) == 3
    assert deck.cards_remaining() == initial_count - 3
    assert all(isinstance(p, Policy) for p in policies)


def test_draw_not_enough_policies_raises_error():
    """Test that drawing more policies than available raises error."""
    deck = PolicyDeck.create_initial_deck()

    with pytest.raises(ValueError, match="Not enough policies to draw"):
        deck.draw(20)


def test_discard_policies():
    """Test discarding policies."""
    deck = PolicyDeck.create_initial_deck()
    policies = deck.draw(3)

    assert len(deck.discard_pile) == 0

    deck.discard(policies)

    assert len(deck.discard_pile) == 3


def test_reshuffle_when_low():
    """Test that discard pile is reshuffled when draw pile is low."""
    deck = PolicyDeck.create_initial_deck()

    # Draw cards until we have fewer than 3 left
    while deck.cards_remaining() >= 3:
        policies = deck.draw(3)
        deck.discard(policies[:2])  # Discard 2, keep 1 in play

    # Now draw pile has < 3 cards and discard pile has cards
    initial_discard_count = len(deck.discard_pile)
    assert deck.cards_remaining() < 3
    assert initial_discard_count > 0

    # Drawing should trigger reshuffle
    policies = deck.draw(3)

    assert len(policies) == 3
    assert len(deck.discard_pile) == 0  # Discard pile was reshuffled


def test_peek_policies():
    """Test peeking at top policies without removing them."""
    deck = PolicyDeck.create_initial_deck()
    initial_count = deck.cards_remaining()

    peeked = deck.peek(3)

    assert len(peeked) == 3
    assert deck.cards_remaining() == initial_count  # Count unchanged
    assert all(isinstance(p, Policy) for p in peeked)


def test_peek_not_enough_policies_raises_error():
    """Test that peeking at more policies than available raises error."""
    deck = PolicyDeck.create_initial_deck()

    with pytest.raises(ValueError, match="Not enough policies to peek"):
        deck.peek(20)


def test_total_cards():
    """Test total card count across both piles."""
    deck = PolicyDeck.create_initial_deck()

    assert deck.total_cards() == 17

    policies = deck.draw(3)
    deck.discard([policies[0]])

    # 17 - 3 drawn + 1 discarded = 15 total
    assert deck.total_cards() == 15
