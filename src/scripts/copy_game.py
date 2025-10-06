#!/usr/bin/env python3
"""Debug script to copy an existing game and give it a new ID."""

import sys
from pathlib import Path
from uuid import uuid4

from src.adapters.persistence.file_system_repository import FileSystemRoomRepository


def main():
    if len(sys.argv) < 2:
        print("Usage: python debug_copy_game.py <source_room_id> [target_room_id]")
        print("\nIf target_room_id is not provided, a new UUID will be generated.")
        sys.exit(1)

    source_room_id = sys.argv[1]
    target_room_id = sys.argv[2] if len(sys.argv) > 2 else str(uuid4())

    repository = FileSystemRoomRepository()

    try:
        source_room = repository.find_by_id(source_room_id)
        if not source_room:
            print(f"Error: Room {source_room_id} not found")
            sys.exit(1)

        source_room.room_id = target_room_id

        repository.save(source_room)

        print(f"Successfully copied game:")
        print(f"  Source Room ID: {source_room_id}")
        print(f"  Target Room ID: {target_room_id}")
        print(f"  Player Count: {source_room.player_count}")
        print(f"  Status: {source_room.status.value}")
        if source_room.game_state:
            print(f"  Phase: {source_room.game_state.current_phase.value}")
            print(f"  Liberal Policies: {source_room.game_state.liberal_policies}")
            print(f"  Fascist Policies: {source_room.game_state.fascist_policies}")

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
