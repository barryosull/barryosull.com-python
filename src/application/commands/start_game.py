import random
from dataclasses import dataclass
from uuid import UUID

from src.domain.entities.game_state import GamePhase, GameState
from src.domain.entities.policy_deck import PolicyDeck
from src.domain.services.role_assignment_service import RoleAssignmentService
from src.ports.repository_port import RoomRepositoryPort


@dataclass
class StartGameCommand:
    room_id: UUID
    requester_id: UUID
    first_president_id: UUID | None = None
    policy_deck: PolicyDeck | None = None
    shuffle_players: bool = True


class StartGameHandler:
    def __init__(self, repository: RoomRepositoryPort) -> None:
        self.repository = repository

    def handle(self, command: StartGameCommand) -> None:
        room = self.repository.find_by_id(command.room_id)
        if not room:
            raise ValueError(f"Room {command.room_id} not found")

        if not room.is_creator(command.requester_id):
            raise ValueError("Only the room creator can start the game")

        if not room.can_start_game():
            raise ValueError("Cannot start game - need at least 5 players")

        player_ids = [p.player_id for p in room.players]

        players_for_roles = player_ids.copy()
        if command.shuffle_players:
            random.shuffle(players_for_roles)
        role_assignments = RoleAssignmentService.assign_roles(players_for_roles)

        if command.first_president_id:
            if command.first_president_id not in player_ids:
                raise ValueError("first_president_id must be a player in the game")
            first_president_id = command.first_president_id
        else:
            first_president_id = random.choice(player_ids)

        game_state_kwargs = {
            "round_number": 1,
            "president_id": first_president_id,
            "current_phase": GamePhase.NOMINATION,
            "role_assignments": role_assignments,
        }

        if command.policy_deck:
            game_state_kwargs["policy_deck"] = command.policy_deck

        game_state = GameState(**game_state_kwargs)

        #print(game_state.policy_deck) 
        #exit

        room.start_game(game_state)
        self.repository.save(room)
