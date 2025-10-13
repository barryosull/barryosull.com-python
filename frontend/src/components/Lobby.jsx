import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { api } from '../services/api';
import { playerStorage, preserveParams } from '../services/storage';

export default function Lobby() {
  const { roomId } = useParams();
  const navigate = useNavigate();
  const [room, setRoom] = useState(null);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const playerId = playerStorage.getPlayerId();

  useEffect(() => {
    fetchRoomState();
    
    // Connect to Websocket
    const socket = new WebSocket('ws://localhost:8000/api/ws/' + roomId);

    socket.onmessage = function(event) {
      if (event.data === 'game_state_updated') {
        fetchRoomState();
      }
    }

  }, [roomId]);

  const fetchRoomState = async () => {
    try {
      const data = await api.getRoomState(roomId);
      setRoom(data);

      if (data.status === 'IN_PROGRESS') {
        navigate(preserveParams(`/game/${roomId}`));
      }
    } catch (err) {
      setError(err.message);
    }
  };

  const handleStartGame = async () => {
    setError('');
    setLoading(true);
    try {
      await api.startGame(roomId, playerId);
      await fetchRoomState();
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const copyRoomId = () => {
    navigator.clipboard.writeText(roomId);
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

        <div className="room-id-section">
          <div className="label">Room ID:</div>
          <div className="room-id">{roomId}</div>
          <button onClick={copyRoomId} className="copy-button">
            Copy
          </button>
          <div className="hint">Share this ID with your friends</div>
        </div>

        <div className="section">
          <h2 className="subtitle">
            Players ({room.players.length}/10)
          </h2>
          <ul className="player-list">
            {room.players.map((player) => (
              <li key={player.player_id} className="player-item">
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
