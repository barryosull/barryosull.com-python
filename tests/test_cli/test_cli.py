"""Tests for CLI."""

from click.testing import CliRunner
from my_app.cli import main


def test_hello_command():
    """Test hello command."""
    runner = CliRunner()
    result = runner.invoke(main, ["hello", "World"])
    assert result.exit_code == 0
    assert "Hello, World!" in result.output