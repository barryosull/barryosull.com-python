"""Business logic services."""


def greet(name: str) -> str:
    """Generate a greeting message."""
    return f"Hello, {name}!"


def process_data(data: str) -> str:
    """Process some data."""
    return data.upper()