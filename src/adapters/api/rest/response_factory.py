from src.adapters.api.rest.schemas import PlayerResponse, RoomStateResponse
from src.application.queries.get_room_state import RoomStateDTO


class ResponseFactory:

    @staticmethod
    def make_room_state_response(result: RoomStateDTO) -> RoomStateResponse:
        return RoomStateResponse(
            room_id=result.room_id,
            status=result.status,
            creator_id=result.creator_id,
            players=[
                PlayerResponse(
                    player_id=p.player_id,
                    name=p.name,
                    is_connected=p.is_connected,
                    is_alive=p.is_alive,
                )
                for p in result.players
            ],
            player_count=result.player_count,
            can_start=result.can_start,
            created_at=result.created_at,
        )
