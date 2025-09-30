"""CLI interface for my_app."""

import click
from my_app.core.services import greet


@click.group()
@click.version_option()
def main():
    """My App CLI - A tool for managing tasks."""
    pass


@main.command()
@click.argument("name")
def hello(name: str):
    """Say hello to NAME."""
    message = greet(name)
    click.echo(message)


if __name__ == "__main__":
    main()