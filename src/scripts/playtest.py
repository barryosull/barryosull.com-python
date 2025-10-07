#!/usr/bin/env python3
"""Script to create a test game using the command bus."""

import argparse
import random
import sys
from pathlib import Path
import webbrowser
from uuid import UUID

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.adapters.persistence.file_system_repository import FileSystemRoomRepository
from src.application.command_bus import CommandBus
from src.application.commands.create_room import CreateRoomCommand
from src.application.commands.join_room import JoinRoomCommand
from src.application.commands.start_game import StartGameCommand

PLAYER_NAMES = [
    "Alice",
    "Bob",
    "Charlie",
    "Diana",
    "Edward",
    "Fiona",
    "George",
    "Hannah",
    "Ivan",
    "Julia",
]

repository = FileSystemRoomRepository()
command_bus = CommandBus(repository)

def start_game(selected_names, room_id, creator_id) -> list[UUID]:
    
    commands = []
    for name in selected_names[1:]:
        commands.append(JoinRoomCommand(room_id=room_id, player_name=name))
    commands.append(StartGameCommand(room_id=room_id, requester_id=creator_id, first_president_id=creator_id))

    player_ids = [creator_id]
    for command in commands:
        result = command_bus.execute(command)
        if isinstance(command, JoinRoomCommand):
            player_ids.append(result.player_id)
            print(f"Player {command.player_name} joined: {result.player_id}")
        elif isinstance(command, StartGameCommand):
            print(f"\nGame started successfully!")
            print(f"Room ID: {room_id}")
    
    return player_ids

def main():
    parser = argparse.ArgumentParser(description="Create a test game with N players")
    parser.add_argument(
        "player_count",
        type=int,
        nargs="?",
        default=6,
        help="Number of players (5-10, default: 6)"
    )
    args = parser.parse_args()

    if args.player_count < 5 or args.player_count > 10:
        print(f"Error: Player count must be between 5 and 10 (got {args.player_count})")
        sys.exit(1)

    selected_names = random.sample(PLAYER_NAMES, args.player_count)

    create_result = command_bus.execute(CreateRoomCommand(player_name=selected_names[0]))
    room_id = create_result.room_id
    creator_id = create_result.player_id

    print(f"Created room: {room_id}")
    print(f"Creator ({selected_names[0]}): {creator_id}")

    player_ids = start_game(selected_names, room_id, creator_id)

    print("Player IDs" + ", ".join([str(id) for id in player_ids]))

    room = repository.find_by_id(room_id)
    if room and room.game_state:
        print(f"President: {room.game_state.president_id}")
        print(f"Phase: {room.game_state.current_phase.value}")

    # Open the game for testing
    webbrowser.open(f"http://localhost:3000/test-multi-player.html?roomId={room_id}", new=2)

if __name__ == "__main__":
    main()
