from unittest.mock import AsyncMock, Mock
from uuid import UUID, uuid4
import pytest
from backend.adapters.api.rest.room_manager import RoomManager


@pytest.fixture
def room_manager():
    return RoomManager()


@pytest.fixture
def mock_websocket():
    ws = Mock()
    ws.accept = AsyncMock()
    ws.send_text = AsyncMock()
    return ws


def test_initialization(room_manager):
    assert room_manager.rooms == {}


@pytest.mark.asyncio
async def test_connect_creates_new_room(room_manager, mock_websocket):
    room_id = uuid4()

    await room_manager.connect(mock_websocket, room_id)

    mock_websocket.accept.assert_called_once()
    assert room_id in room_manager.rooms
    assert mock_websocket in room_manager.rooms[room_id]
    assert len(room_manager.rooms[room_id]) == 1


@pytest.mark.asyncio
async def test_connect_adds_to_existing_room(room_manager):
    room_id = uuid4()
    ws1 = Mock()
    ws1.accept = AsyncMock()
    ws2 = Mock()
    ws2.accept = AsyncMock()

    await room_manager.connect(ws1, room_id)
    await room_manager.connect(ws2, room_id)

    assert len(room_manager.rooms[room_id]) == 2
    assert ws1 in room_manager.rooms[room_id]
    assert ws2 in room_manager.rooms[room_id]


def test_disconnect_removes_websocket(room_manager):
    room_id = uuid4()
    ws1 = Mock()
    ws2 = Mock()
    room_manager.rooms[room_id] = [ws1, ws2]

    room_manager.disconnect(ws1, room_id)

    assert room_id in room_manager.rooms
    assert ws1 not in room_manager.rooms[room_id]
    assert ws2 in room_manager.rooms[room_id]
    assert len(room_manager.rooms[room_id]) == 1


def test_disconnect_removes_empty_room(room_manager, mock_websocket):
    room_id = uuid4()
    room_manager.rooms[room_id] = [mock_websocket]

    room_manager.disconnect(mock_websocket, room_id)

    assert room_id not in room_manager.rooms


def test_disconnect_keeps_room_with_remaining_connections(room_manager):
    room_id = uuid4()
    ws1 = Mock()
    ws2 = Mock()
    room_manager.rooms[room_id] = [ws1, ws2]

    room_manager.disconnect(ws1, room_id)

    assert room_id in room_manager.rooms
    assert ws1 not in room_manager.rooms[room_id]
    assert ws2 in room_manager.rooms[room_id]
    assert len(room_manager.rooms[room_id]) == 1


@pytest.mark.asyncio
async def test_broadcast_sends_to_all_connections(room_manager):
    room_id = uuid4()
    ws1 = Mock()
    ws1.send_json = AsyncMock()
    ws2 = Mock()
    ws2.send_json = AsyncMock()
    ws3 = Mock()
    ws3.send_json = AsyncMock()

    room_manager.rooms[room_id] = [ws1, ws2, ws3]
    message = {"type": "message"}

    await room_manager.broadcast(room_id, message)

    ws1.send_json.assert_called_once_with(message)
    ws2.send_json.assert_called_once_with(message)
    ws3.send_json.assert_called_once_with(message)


@pytest.mark.asyncio
async def test_broadcast_to_nonexistent_room(room_manager, mock_websocket):
    room_id = uuid4()

    await room_manager.broadcast(room_id, "test message")

    mock_websocket.send_json.assert_not_called()


@pytest.mark.asyncio
async def test_broadcast_to_empty_room_list(room_manager):
    room_id = uuid4()
    room_manager.rooms[room_id] = []
    ws = Mock()
    ws.send_json = AsyncMock()

    await room_manager.broadcast(room_id, "test message")

    ws.send_json.assert_not_called()


@pytest.mark.asyncio
async def test_full_lifecycle(room_manager):
    room_id = uuid4()
    ws1 = Mock()
    ws1.accept = AsyncMock()
    ws1.send_json = AsyncMock()
    ws2 = Mock()
    ws2.accept = AsyncMock()
    ws2.send_json = AsyncMock()
    message = {"type": "message"}

    await room_manager.connect(ws1, room_id)
    await room_manager.connect(ws2, room_id)
    assert len(room_manager.rooms[room_id]) == 2

    await room_manager.broadcast(room_id, message)
    ws1.send_json.assert_called_once_with(message)
    ws2.send_json.assert_called_once_with(message)

    room_manager.disconnect(ws1, room_id)
    assert len(room_manager.rooms[room_id]) == 1
    assert ws2 in room_manager.rooms[room_id]

    room_manager.disconnect(ws2, room_id)
    assert room_id not in room_manager.rooms
