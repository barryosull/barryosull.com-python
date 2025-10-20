#!/usr/bin/env python3
"""Script to create a test game using the command bus."""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import argparse
import webbrowser
from uuid import UUID

from src.application.commands.use_executive_action import UseExecutiveActionCommand
from src.domain.entities.game_state import GamePhase, PresidentialPower
from src.application.commands.cast_vote import CastVoteCommand
from src.application.commands.discard_policy import DiscardPolicyCommand
from src.application.commands.enact_policy import EnactPolicyCommand
from src.application.commands.nominate_chancellor import NominateChancellorCommand
from src.domain.entities.policy_deck import PolicyDeck
from src.domain.value_objects.policy import Policy, PolicyType
from src.adapters.persistence.file_system_room_repository import FileSystemRoomRepository
from src.adapters.persistence.file_system_code_repository import FileSystemCodeRepository
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

room_repository = FileSystemRoomRepository()
code_repository = FileSystemCodeRepository()
command_bus = CommandBus(room_repository)


def execute(command):
    print(f"Executing: {command.__class__.__name__}")
    return command_bus.execute(command) 


def start_game(selected_names, room_id, creator_id) -> list[UUID]:
    
    player_ids = [creator_id]

    for name in selected_names[1:]:
        command = JoinRoomCommand(room_id=room_id, player_name=name)
        result = execute(command)
        player_ids.append(result.player_id)

    execute(StartGameCommand(
        room_id=room_id, 
        requester_id=creator_id, 
        first_president_id=creator_id, # First player is always president
        policy_deck=make_diverse_deck(),
        shuffle_players=False # We want roles to be deterministic, first player is always Hitler
    ))
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

def play_rounds_and_enact_fascist_policies(rounds: int, room_id: UUID, player_ids: list[UUID]):

    president_id = player_ids[0]
    executed_ids = []

    # Rounds of play
    for i in range(0, rounds):
        # Chancellor is player after president
        president_index = player_ids.index(president_id)
        chancellor_id = player_ids[(president_index + 1) % len(player_ids)]

        execute(NominateChancellorCommand(
            room_id=room_id,
            nominating_player_id=president_id,
            chancellor_id=chancellor_id
        ))

        # Elect chancellor
        for player_id in player_ids:
            if player_id != president_id and player_id not in executed_ids:
                execute(CastVoteCommand(
                    room_id,
                    player_id,
                    True
                ))

        if (i >= 6):
            # Enact liberal so game doesn't end
            execute(DiscardPolicyCommand(
                room_id=room_id,
                player_id=president_id,
                policy_type=PolicyType.FASCIST
            ))
            execute(EnactPolicyCommand(
                room_id=room_id,
                player_id=chancellor_id,
                policy_type=PolicyType.LIBERAL
            )) 
        else:
            # Enact fascist policy
            execute(DiscardPolicyCommand(
                room_id=room_id,
                player_id=president_id,
                policy_type=PolicyType.LIBERAL
            ))
            execute(EnactPolicyCommand(
                room_id=room_id,
                player_id=chancellor_id,
                policy_type=PolicyType.FASCIST
            ))    
        
        room = room_repository.find_by_id(room_id)
        print(f"Game phase: {room.game_state.current_phase}")

        # Execute executive actions, but not the one from the last policy enactment
        if i < rounds - 1 and room.game_state.current_phase == GamePhase.EXECUTIVE_ACTION:
            power = room.game_state.get_presidential_power(len(room.active_players()))
            print(f"Executive action: {power}")
            if power == PresidentialPower.INVESTIGATE_LOYALTY:
                execute(UseExecutiveActionCommand(
                    room_id=room_id,
                    player_id=president_id,
                    target_player_id=chancellor_id
                )) 
            if power == PresidentialPower.POLICY_PEEK:
                execute(UseExecutiveActionCommand(
                    room_id=room_id,
                    player_id=president_id,
                ))  
            if power == PresidentialPower.CALL_SPECIAL_ELECTION:
                special_president_id = player_ids[(president_index + 1) % len(player_ids)]
                execute(UseExecutiveActionCommand(
                    room_id=room_id,
                    player_id=president_id,
                    target_player_id=special_president_id
                ))  
            if power == PresidentialPower.EXECUTION:
                executed_id = player_ids[(president_index - 1) % len(player_ids)]
                execute(UseExecutiveActionCommand(
                    room_id=room_id,
                    player_id=president_id,
                    target_player_id=executed_id
                ))
                executed_ids.append(executed_id)
        
        room = room_repository.find_by_id(room_id)
        president_id = room.game_state.president_id

def main():
    parser = argparse.ArgumentParser(description="Create a test game with N players")
    parser.add_argument(
        "player_count",
        type=int,
        nargs="?",
        default=6,
        help="Number of players (5-10, default: 6)"
    )
    parser.add_argument(
        "rounds",
        type=int,
        nargs="?",
        default=0,
        help="Number of rounds to play until (1-6, default: 0)"
    )

    args = parser.parse_args()

    if args.player_count < 5 or args.player_count > 10:
        print(f"Error: Player count must be between 5 and 10 (got {args.player_count})")
        sys.exit(1)

    if args.rounds < 0 or args.rounds > 6:
        print(f"Error: Rounds must be between 0 and 6 (got {args.rounds})")
        sys.exit(1)

    selected_names = PLAYER_NAMES[0:args.player_count]

    create_result = execute(CreateRoomCommand(player_name=selected_names[0]))
    room_id = create_result.room_id
    creator_id = create_result.player_id

    print(f"Created room: {room_id}")
    print(f"Creator ({selected_names[0]}): {creator_id}")

    player_ids = start_game(selected_names, room_id, creator_id)

    play_rounds_and_enact_fascist_policies(args.rounds, room_id, player_ids);

    room = room_repository.find_by_id(room_id)
    if room and room.game_state:
        print(f"President: {room.game_state.president_id}")
        print(f"Phase: {room.game_state.current_phase.value}")

    code = code_repository.generate_code_for_room(room_id)

    # Open the game for testing
    webbrowser.open(f"http://localhost:3000/test-multi-player.html?roomCode={code}", new=2)

if __name__ == "__main__":
    main()
