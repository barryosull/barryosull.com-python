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
      setError(err.message);
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
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={styles.container}>
      <div style={styles.card}>
        <h1 style={styles.title}>Secret Hitler</h1>

        {error && <div style={styles.error}>{error}</div>}

        <div style={styles.section}>
          <input
            type="text"
            placeholder="Your Name"
            value={playerName}
            onChange={(e) => setPlayerName(e.target.value)}
            style={styles.input}
            disabled={loading}
            maxLength={10}
          />
        </div>

        <div style={styles.section}>
          <h2 style={styles.subtitle}>Create New Game</h2>
          <button
            onClick={handleCreateRoom}
            style={styles.button}
            disabled={loading}
          >
            Create Room
          </button>
        </div>

        <div style={styles.divider}>OR</div>

        <div style={styles.section}>
          <h2 style={styles.subtitle}>Join Existing Game</h2>
          <input
            type="text"
            placeholder="Room ID"
            value={roomId}
            onChange={(e) => setRoomId(e.target.value)}
            style={styles.input}
            disabled={loading}
          />
          <button
            onClick={handleJoinRoom}
            style={styles.button}
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
  container: {
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    minHeight: '100vh',
    backgroundColor: '#1a1a1a',
    padding: '20px'
  },
  card: {
    backgroundColor: '#FBB969',
    borderRadius: '8px',
    padding: '40px',
    maxWidth: '500px',
    width: '100%',
    boxShadow: '0 4px 6px rgba(0, 0, 0, 0.3)'
  },
  title: {
    color: '#fff',
    fontSize: '32px',
    marginBottom: '30px',
    textAlign: 'center'
  },
  subtitle: {
    color: '#ccc',
    fontSize: '18px',
    marginBottom: '15px'
  },
  section: {
    marginBottom: '25px'
  },
  input: {
    width: '100%',
    padding: '12px',
    fontSize: '16px',
    borderRadius: '4px',
    border: '1px solid #444',
    backgroundColor: '#333',
    color: '#fff',
    marginBottom: '10px',
    boxSizing: 'border-box'
  },
  button: {
    width: '100%',
    padding: '12px',
    fontSize: '16px',
    borderRadius: '4px',
    border: 'none',
    backgroundColor: '#0066cc',
    color: '#fff',
    cursor: 'pointer',
    fontWeight: 'bold'
  },
  divider: {
    textAlign: 'center',
    color: '#666',
    margin: '30px 0',
    fontSize: '14px'
  },
  error: {
    backgroundColor: '#d32f2f',
    color: '#fff',
    padding: '12px',
    borderRadius: '4px',
    marginBottom: '20px'
  }
};
