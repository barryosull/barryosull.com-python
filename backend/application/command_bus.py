"""Generic command bus for dispatching commands to their handlers."""

from typing import Any

from backend.application.commands.cast_vote import CastVoteCommand, CastVoteHandler
from backend.application.commands.create_room import CreateRoomCommand, CreateRoomHandler
from backend.application.commands.discard_policy import (
    DiscardPolicyCommand,
    DiscardPolicyHandler,
)
from backend.application.commands.enact_policy import EnactPolicyCommand, EnactPolicyHandler
from backend.application.commands.join_room import JoinRoomCommand, JoinRoomHandler
from backend.application.commands.nominate_chancellor import (
    NominateChancellorCommand,
    NominateChancellorHandler,
)
from backend.application.commands.reorder_players import (
    ReorderPlayersCommand,
    ReorderPlayersHandler,
)
from backend.application.commands.start_game import StartGameCommand, StartGameHandler
from backend.application.commands.use_executive_action import (
    UseExecutiveActionCommand,
    UseExecutiveActionHandler,
)
from backend.application.commands.veto_agenda import VetoAgendaCommand, VetoAgendaHandler
from backend.ports.room_repository_port import RoomRepositoryPort


class CommandBus:
    def __init__(self, repository: RoomRepositoryPort) -> None:
        self.repository = repository
        self._handlers = {
            CreateRoomCommand: CreateRoomHandler,
            JoinRoomCommand: JoinRoomHandler,
            ReorderPlayersCommand: ReorderPlayersHandler,
            StartGameCommand: StartGameHandler,
            NominateChancellorCommand: NominateChancellorHandler,
            CastVoteCommand: CastVoteHandler,
            DiscardPolicyCommand: DiscardPolicyHandler,
            EnactPolicyCommand: EnactPolicyHandler,
            UseExecutiveActionCommand: UseExecutiveActionHandler,
            VetoAgendaCommand: VetoAgendaHandler,
        }

    def execute(self, command: Any) -> Any:
        command_type = type(command)
        handler_class = self._handlers.get(command_type)

        if not handler_class:
            raise ValueError(f"No handler registered for command type: {command_type}")

        handler = handler_class(self.repository)
        return handler.handle(command)
