import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { api } from '../services/api';
import { playerStorage, preserveParams } from '../services/storage';

export default function HomePage() {
  const [playerName, setPlayerName] = useState(() => {
    const params = new URLSearchParams(window.location.search);
    return params.get('name') || '';
  });
  const [roomId, setRoomId] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleCreateRoom = async (e) => {
    e.preventDefault();
    setError('');

    if (!playerName.trim()) {
      setError('Please enter your name');
      return;
    }

    setLoading(true);
    try {
      const result = await api.createRoom(playerName.trim());
      playerStorage.setPlayerId(result.player_id);
      playerStorage.setPlayerName(playerName.trim());
      navigate(preserveParams(`/room/${result.room_id}`));
    } catch (err) {
      setError("Something went wrong");
    } finally {
      setLoading(false);
    }
  };

  const handleJoinRoom = async (e) => {
    e.preventDefault();
    setError('');

    if (!playerName.trim()) {
      setError('Please enter your name');
      return;
    }

    if (!roomId.trim()) {
      setError('Please enter a room ID');
      return;
    }

    setLoading(true);
    try {
      const result = await api.joinRoom(roomId.trim(), playerName.trim());
      playerStorage.setPlayerId(result.player_id);
      playerStorage.setPlayerName(playerName.trim());
      navigate(preserveParams(`/room/${roomId.trim()}`));
    } catch (err) {
      setError("Something went wrong");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container lobby">
      <div className="card">
        <div className="header">
          <h1 className="title">Secret Hitler</h1>
        </div>

        {error && <div className="error">{error}</div>}

        <div style={styles.section}>
          <input
            type="text"
            placeholder="Your Name"
            value={playerName}
            onChange={(e) => setPlayerName(e.target.value)}
            disabled={loading}
            maxLength={10}
          />
        </div>

        <div style={styles.section}>
          <h2 className="subtitle">Create New Game</h2>
          <button
            onClick={handleCreateRoom}
            disabled={loading}
          >
            Create Room
          </button>
        </div>

        <div className="divider">OR</div>

        <div style={styles.section}>
          <h2 className="subtitle">Join Existing Game</h2>
          <input
            type="text"
            placeholder="Room ID"
            value={roomId}
            onChange={(e) => setRoomId(e.target.value)}
            disabled={loading}
          />
          <button
            onClick={handleJoinRoom}
            disabled={loading}
          >
            Join Room
          </button>
        </div>
      </div>
    </div>
  );
}

const styles = {
  error: {
    backgroundColor: '#d32f2f',
    color: '#fff',
    padding: '12px',
    borderRadius: '4px',
    marginBottom: '20px'
  }
};
