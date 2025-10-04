import { useState } from 'react';

export default function NominationView({ players, gameState, myPlayerId, onNominate }) {
  const [selectedChancellor, setSelectedChancellor] = useState(null);
  const [loading, setLoading] = useState(false);

  const isPresident = gameState.president_id === myPlayerId;

  const handleNominate = async () => {
    if (!selectedChancellor) return;

    setLoading(true);
    try {
      await onNominate(selectedChancellor);
    } finally {
      setLoading(false);
    }
  };

  const eligiblePlayers = players.filter(
    (p) => p.is_alive && p.player_id !== gameState.president_id
  );

  if (!isPresident) {
    return (
      <div style={styles.container}>
        <h3 style={styles.title}>Nomination Phase</h3>
        <div style={styles.waiting}>
          Waiting for President to nominate a Chancellor...
        </div>
      </div>
    );
  }

  return (
    <div style={styles.container}>
      <h3 style={styles.title}>Nominate a Chancellor</h3>
      <div style={styles.subtitle}>
        You are the President. Choose a player to nominate as Chancellor.
      </div>

      <div style={styles.playerGrid}>
        {eligiblePlayers.map((player) => (
          <button
            key={player.player_id}
            onClick={() => setSelectedChancellor(player.player_id)}
            style={{
              ...styles.playerButton,
              ...(selectedChancellor === player.player_id && styles.selectedPlayer)
            }}
            disabled={loading}
          >
            {player.name}
          </button>
        ))}
      </div>

      <button
        onClick={handleNominate}
        style={{
          ...styles.confirmButton,
          ...(!selectedChancellor && styles.buttonDisabled)
        }}
        disabled={!selectedChancellor || loading}
      >
        {loading ? 'Nominating...' : 'Confirm Nomination'}
      </button>
    </div>
  );
}

const styles = {
  container: {
    backgroundColor: '#333',
    borderRadius: '8px',
    padding: '20px',
    marginBottom: '20px'
  },
  title: {
    color: '#fff',
    fontSize: '20px',
    marginBottom: '10px',
    marginTop: 0
  },
  subtitle: {
    color: '#aaa',
    fontSize: '14px',
    marginBottom: '20px'
  },
  waiting: {
    color: '#888',
    fontSize: '16px',
    textAlign: 'center',
    padding: '20px'
  },
  playerGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fill, minmax(150px, 1fr))',
    gap: '10px',
    marginBottom: '20px'
  },
  playerButton: {
    padding: '15px',
    fontSize: '14px',
    borderRadius: '4px',
    border: '2px solid #555',
    backgroundColor: '#2a2a2a',
    color: '#fff',
    cursor: 'pointer',
    transition: 'all 0.2s'
  },
  selectedPlayer: {
    borderColor: '#0066cc',
    backgroundColor: '#0066cc'
  },
  confirmButton: {
    width: '100%',
    padding: '15px',
    fontSize: '16px',
    borderRadius: '4px',
    border: 'none',
    backgroundColor: '#4caf50',
    color: '#fff',
    cursor: 'pointer',
    fontWeight: 'bold'
  },
  buttonDisabled: {
    backgroundColor: '#555',
    cursor: 'not-allowed'
  }
};
