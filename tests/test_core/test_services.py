"""Tests for core services."""

from my_app.core.services import greet, process_data


def test_greet():
    """Test greet function."""
    assert greet("World") == "Hello, World!"


def test_process_data():
    """Test process_data function."""
    assert process_data("hello") == "HELLO"