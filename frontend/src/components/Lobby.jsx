import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { api } from '../services/api';
import { playerStorage, preserveParams } from '../services/storage';

export default function Lobby() {
  const { roomCode } = useParams();
  const navigate = useNavigate();
  const [room, setRoom] = useState(null);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [draggedIndex, setDraggedIndex] = useState(null);
  const playerId = playerStorage.getPlayerId();

  useEffect(() => {
    fetchRoomState();

    const wsUrl = import.meta.env.VITE_WS_URL;

    // Connect to Websocket
    const socket = new WebSocket(wsUrl + '/' + roomCode);

    socket.onmessage = function(event) {
      const message = JSON.parse(event.data);
      if (message.type === 'game_state_updated') {
        fetchRoomState();
      }
    }

  }, [roomCode]);

  const fetchRoomState = async () => {
    try {
      const data = await api.getRoomState(roomCode);
      setRoom(data);

      if (data.status === 'IN_PROGRESS') {
        navigate(preserveParams(`/game/${roomCode}`));
      }
    } catch (err) {
      setError(err.message);
    }
  };

  const handleStartGame = async () => {
    setError('');
    setLoading(true);
    try {
      await api.startGame(roomCode, playerId);
      await fetchRoomState();
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const copyRoomCode = () => {
    navigator.clipboard.writeText(roomCode);
  };

  const handleDragStart = (index) => {
    setDraggedIndex(index);
  };

  const handleDragOver = (e) => {
    e.preventDefault();
  };

  const handleDrop = async (dropIndex) => {
    if (draggedIndex === null || draggedIndex === dropIndex) {
      setDraggedIndex(null);
      return;
    }

    const reorderedPlayers = [...room.players];
    const [draggedPlayer] = reorderedPlayers.splice(draggedIndex, 1);
    reorderedPlayers.splice(dropIndex, 0, draggedPlayer);

    const playerIds = reorderedPlayers.map(p => p.player_id);

    try {
      await api.reorderPlayers(roomCode, playerId, playerIds);
      setDraggedIndex(null);
    } catch (err) {
      setError(err.message);
      setDraggedIndex(null);
    }
  };

  if (!room) {
    return (
      <div className="container lobby">
        <div className="card">Loading...</div>
      </div>
    );
  }

  const isCreator = room.creator_id === playerId;
  const canStart = room.players.length >= 5;

  return (
    <div className="container lobby">
      <div className="card">
        <div className="header">
          <h1 className="title">Game Lobby</h1>
        </div>

        {error && <div className="error">{error}</div>}

        <div className="room-code-section">
          <span className="label">Room Code: </span>
          <span className="room-code">{roomCode}</span>
          <button onClick={copyRoomCode} className="copy-button">
            Copy
          </button>
          <div className="hint">Share this code with your friends</div>
        </div>

        <div className="section">
          <h2 className="subtitle">
            Players ({room.players.length}/10)
            {isCreator && <span className="hint"> (drag to reorder)</span>}
          </h2>
          <ul className="player-list">
            {room.players.map((player, index) => (
              <li
                key={player.player_id}
                className={`player-item ${isCreator ? 'draggable' : ''} ${draggedIndex === index ? 'dragging' : ''}`}
                draggable={isCreator}
                onDragStart={() => handleDragStart(index)}
                onDragOver={handleDragOver}
                onDrop={() => handleDrop(index)}
              >
                {player.name}
                {player.player_id === room.creator_id && (
                  <span className="badge">Host</span>
                )}
                {player.player_id === playerId && (
                  <span className="badge">You</span>
                )}
              </li>
            ))}
          </ul>
        </div>

        <div className="section">
          {isCreator ? (
            <>
              <div className="hint">
                {canStart
                  ? 'You can start the game now!'
                  : `Need at least 5 players to start (${5 - room.players.length} more needed)`}
              </div>
              <button
                onClick={handleStartGame}
                disabled={!canStart || loading}
              >
                {loading ? 'Starting...' : 'Start Game'}
              </button>
            </>
          ) : (
            <div className="waiting-message">
              Waiting for host to start the game...
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
