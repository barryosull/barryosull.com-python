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

from src.application.commands.cast_vote import CastVoteCommand
from src.application.commands.discard_policy import DiscardPolicyCommand
from src.application.commands.enact_policy import EnactPolicyCommand
from src.application.commands.nominate_chancellor import NominateChancellorCommand
from src.domain.entities.policy_deck import PolicyDeck
from src.domain.value_objects.policy import Policy, PolicyType
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
    
    player_ids = [creator_id]

    for name in selected_names[1:]:
        command = JoinRoomCommand(room_id=room_id, player_name=name)
        result = command_bus.execute(command)
        player_ids.append(result.player_id)
        print(f"Player {command.player_name} joined: {result.player_id}")

    command_bus.execute(StartGameCommand(
        room_id=room_id, 
        requester_id=creator_id, 
        first_president_id=creator_id, # First player is always president
        policy_deck=make_diverse_deck(),
        shuffle_players=False # We want roles to be deterministic, first player is always Hitler
    ))
    print(f"\nGame started successfully!")
    print(f"Room ID: {room_id}")
        
    return player_ids

# Make a policy deck with two fascist and one liberal policy per hand
def make_diverse_deck() -> PolicyDeck:
    return PolicyDeck(
        draw_pile=[
            Policy(PolicyType.LIBERAL),
            Policy(PolicyType.FASCIST),
            Policy(PolicyType.FASCIST),
        ] * 6,
        discard_pile=[],
    )

def play_3_rounds_enact_fascist_policies(room_id, player_ids):

    president_id = player_ids[0]

    # 3 rounds
    for i in range(0, 3):
        # Chancellor is player after president
        president_index = player_ids.index(president_id)
        chancellor_id = player_ids[(president_index + 1) % len(player_ids)]

        command_bus.execute(NominateChancellorCommand(
            room_id=room_id,
            nominating_player_id=president_id,
            chancellor_id=chancellor_id
        ))

        # Elect chancellor
        for player_id in player_ids:
            if player_id != president_id:
                command_bus.execute(CastVoteCommand(
                    room_id,
                    player_id,
                    True
                ))

        # Enact fascist policy
        command_bus.execute(DiscardPolicyCommand(
            room_id=room_id,
            player_id=president_id,
            policy_type=PolicyType.LIBERAL
        ))

        command_bus.execute(EnactPolicyCommand(
            room_id=room_id,
            player_id=chancellor_id,
            policy_type=PolicyType.FASCIST
        ))

        president_id = chancellor_id

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

    selected_names = PLAYER_NAMES[0:args.player_count]

    create_result = command_bus.execute(CreateRoomCommand(player_name=selected_names[0]))
    room_id = create_result.room_id
    creator_id = create_result.player_id

    print(f"Created room: {room_id}")
    print(f"Creator ({selected_names[0]}): {creator_id}")

    player_ids = start_game(selected_names, room_id, creator_id)

    print("Player IDs" + ", ".join([str(id) for id in player_ids]))

    play_3_rounds_enact_fascist_policies(room_id, player_ids);

    room = repository.find_by_id(room_id)
    if room and room.game_state:
        print(f"President: {room.game_state.president_id}")
        print(f"Phase: {room.game_state.current_phase.value}")

    # Open the game for testing
    webbrowser.open(f"http://localhost:3000/test-multi-player.html?roomId={room_id}", new=2)

if __name__ == "__main__":
    main()
