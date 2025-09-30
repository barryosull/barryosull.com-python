"""Task-related CLI commands."""

import click
from my_app.core.services import process_data


@click.command()
@click.argument("data")
def process(data: str):
    """Process data and display the result."""
    result = process_data(data)
    click.echo(f"Processed: {result}")