#!/usr/bin/env python3
"""Debug script to copy an existing game and give it a new ID."""

import sys
from pathlib import Path
from uuid import uuid4
import webbrowser

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

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

        # Open the game for testing
        webbrowser.open(f"http://localhost:3000/test-multi-player.html?roomId={target_room_id}", new=2)

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
