import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { api } from '../services/api';

export default function Lobby() {
  const { roomId } = useParams();
  const navigate = useNavigate();
  const [room, setRoom] = useState(null);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const playerId = localStorage.getItem('playerId');

  useEffect(() => {
    fetchRoomState();
    const interval = setInterval(fetchRoomState, 2000);
    return () => clearInterval(interval);
  }, [roomId]);

  const fetchRoomState = async () => {
    try {
      const data = await api.getRoomState(roomId);
      setRoom(data);

      if (data.status === 'IN_PROGRESS') {
        navigate(`/game/${roomId}`);
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
      <div style={styles.container}>
        <div style={styles.card}>Loading...</div>
      </div>
    );
  }

  const isCreator = room.creator_id === playerId;
  const canStart = room.players.length >= 5;

  return (
    <div style={styles.container}>
      <div style={styles.card}>
        <h1 style={styles.title}>Game Lobby</h1>

        {error && <div style={styles.error}>{error}</div>}

        <div style={styles.roomIdSection}>
          <div style={styles.label}>Room ID:</div>
          <div style={styles.roomIdBox}>
            <span style={styles.roomId}>{roomId}</span>
            <button onClick={copyRoomId} style={styles.copyButton}>
              Copy
            </button>
          </div>
          <div style={styles.hint}>Share this ID with your friends</div>
        </div>

        <div style={styles.section}>
          <h2 style={styles.subtitle}>
            Players ({room.players.length}/10)
          </h2>
          <ul style={styles.playerList}>
            {room.players.map((player) => (
              <li key={player.player_id} style={styles.playerItem}>
                {player.name}
                {player.player_id === room.creator_id && (
                  <span style={styles.badge}>Host</span>
                )}
                {player.player_id === playerId && (
                  <span style={styles.badge}>You</span>
                )}
              </li>
            ))}
          </ul>
        </div>

        <div style={styles.section}>
          {isCreator ? (
            <>
              <div style={styles.hint}>
                {canStart
                  ? 'You can start the game now!'
                  : `Need at least 5 players to start (${5 - room.players.length} more needed)`}
              </div>
              <button
                onClick={handleStartGame}
                style={{
                  ...styles.button,
                  ...((!canStart || loading) && styles.buttonDisabled)
                }}
                disabled={!canStart || loading}
              >
                {loading ? 'Starting...' : 'Start Game'}
              </button>
            </>
          ) : (
            <div style={styles.waitingMessage}>
              Waiting for host to start the game...
            </div>
          )}
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
    backgroundColor: '#2a2a2a',
    borderRadius: '8px',
    padding: '40px',
    maxWidth: '600px',
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
    fontSize: '20px',
    marginBottom: '15px'
  },
  section: {
    marginBottom: '30px'
  },
  roomIdSection: {
    marginBottom: '30px',
    padding: '20px',
    backgroundColor: '#333',
    borderRadius: '8px'
  },
  label: {
    color: '#999',
    fontSize: '14px',
    marginBottom: '8px'
  },
  roomIdBox: {
    display: 'flex',
    alignItems: 'center',
    gap: '10px'
  },
  roomId: {
    color: '#fff',
    fontSize: '24px',
    fontFamily: 'monospace',
    flex: 1
  },
  copyButton: {
    padding: '8px 16px',
    fontSize: '14px',
    borderRadius: '4px',
    border: 'none',
    backgroundColor: '#444',
    color: '#fff',
    cursor: 'pointer'
  },
  hint: {
    color: '#888',
    fontSize: '14px',
    marginTop: '8px'
  },
  playerList: {
    listStyle: 'none',
    padding: 0,
    margin: 0
  },
  playerItem: {
    color: '#fff',
    padding: '12px',
    marginBottom: '8px',
    backgroundColor: '#333',
    borderRadius: '4px',
    display: 'flex',
    alignItems: 'center',
    gap: '10px'
  },
  badge: {
    fontSize: '12px',
    padding: '4px 8px',
    borderRadius: '4px',
    backgroundColor: '#0066cc',
    marginLeft: 'auto'
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
  buttonDisabled: {
    backgroundColor: '#555',
    cursor: 'not-allowed'
  },
  waitingMessage: {
    textAlign: 'center',
    color: '#888',
    fontSize: '16px',
    padding: '20px'
  },
  error: {
    backgroundColor: '#d32f2f',
    color: '#fff',
    padding: '12px',
    borderRadius: '4px',
    marginBottom: '20px'
  }
};
